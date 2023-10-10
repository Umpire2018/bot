from .config import Config
from plugins.twenty_eight.config import plugin_config
from plugins.twenty_eight.bet import *
from plugins.tortoise_orm import reset_record
from nonebot.adapters.telegram.model import ChatPermissions
from tortoise.exceptions import IntegrityError
from nonebot.log import logger
from nonebot import require, get_bot, get_driver
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler  # 定时器时区默认为北京时间
import arrow
from random import choice
from nonebot.log import logger


driver = get_driver()
global_config = driver.config

def start_job():
    # 在8:03开始运行job_1和job_2
    start_time = arrow.now().shift(minutes=3)
    scheduler.add_job(ban_chat_bet, 'interval', minutes=3, start_date=start_time.datetime, id="job_1")
    scheduler.add_job(unban_chat_bet, 'interval', minutes=3, start_date=start_time.shift(seconds=30).datetime, id="job_2")


@driver.on_bot_connect
async def get_telegram_bot():
    Config.base_bot = get_bot()
    await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id, text='呀，机器人已经启动啦！请问有什么需要我的帮助吗？ヾ(≧▽≦*)o')
    logger.warning('Autobots, Roll out!')   
    start_job()

# job0 在每天运行一次开盘
@scheduler.scheduled_job("cron", hour='8', id="job_0")
async def start_bet_at_8():
    await reset_record()
    plugin_config.allow_bet = True
    start_job()
    await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id, text='早上好呀，亲爱的小伙伴们！现在是恢复下注的时间啦~')
    await Config.base_bot.call_api("set_chat_permissions", chat_id=global_config.chat_id,
                                   permissions=ChatPermissions(can_send_messages=True))


# job1 在设定小时的开盘时间前一分钟禁言并封盘，允许2秒误差，并发送所有人的下注记录
async def ban_chat_bet():
    plugin_config.allow_bet = not plugin_config.allow_bet
    await Config.base_bot.call_api("set_chat_permissions",
                                   chat_id=global_config.chat_id,
                                   permissions=ChatPermissions(can_send_messages=False))
    text, send_photo_flag, buffer = await handle_all_history()
    await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id, text=text)
    if send_photo_flag:
        await Config.base_bot.call_api("send_photo", chat_id=global_config.chat_id, photo=buffer,
                                        caption="用户下注记录")


# job2 在设定小时的开盘时间开盘并取消禁言, 当天最后一次时不执行，维持禁止下注状态
async def unban_chat_bet():
    try:
        twenty_eight_result_str, twenty_eight_result = await get_twenty_eight_result()
        await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id, text=twenty_eight_result_str)

        try:
            profit_message, send_user_message_list = await handle_user_point(twenty_eight_result)
            await Config.base_bot.send_to(chat_id=global_config.chat_id, message=profit_message)
            for send_user_message in send_user_message_list:
                await Config.base_bot.send_to(chat_id=send_user_message["tg_id"], message=send_user_message["message"])

        except TypeError:  # 处理 profit_list
            pass
    except IntegrityError:
        await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id,
                                        text=f'''raise IntegrityError,current period:{await SystemConfig.first().values_list("newest_period", flat=True)} ,请通知管理员
                                        ''')

    newest_period = await SystemConfig.first().values_list("newest_period", flat=True)
    newest_period += 1
    await SystemConfig.filter(id=1).update(newest_period=newest_period)

    everyday_game_times = await SystemConfig.first().values_list("everyday_game_times", flat=True)
    everyday_game_times += 1
    await SystemConfig.filter(id=1).update(everyday_game_times=everyday_game_times)

    buffer = await handle_history_period()
    await Config.base_bot.call_api("send_photo",
                                    chat_id=global_config.chat_id,
                                    photo=buffer,
                                    caption="历史记录")

    last_run_time = scheduler.get_job("job_2").next_run_time
    end_of_day = arrow.now('Asia/Shanghai').replace(hour=23, minute=59, second=59)
    time_delta = end_of_day - arrow.get(last_run_time)

    if last_run_time and time_delta.total_seconds() > 180:
        await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id,
                                        text=f'第 {everyday_game_times} 期开始下注！')
        await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id, text=choice(global_config.sentences))
        await Config.base_bot.call_api("set_chat_permissions", chat_id=global_config.chat_id,
                                        permissions=ChatPermissions(can_send_messages=True))
        plugin_config.allow_bet = True
    else:
        logger.warning(f'当前时间为：{arrow.now().format("HH:mm:ss")}, 时间差：{time_delta.total_seconds()}, 下一次运行时间：{last_run_time}')
        plugin_config.allow_bet = False
        await Config.base_bot.call_api("set_chat_permissions", chat_id=global_config.chat_id,
                                        permissions=ChatPermissions(can_send_messages=False))

        await Config.base_bot.call_api("send_message", chat_id=global_config.chat_id,
                                text=f'嘻嘻！今日游戏时间到啦，小伙伴们请注意啦~')

        scheduler.remove_job("job_1")
        scheduler.remove_job("job_2")
 
