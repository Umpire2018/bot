from nonebot import get_driver, get_bot
from tortoise import Tortoise
from nonebot.log import logger
from sqlite3 import connect
from .model import TwentyEightRecord, SystemConfig, Users
from datetime import date

connect('db.sqlite3').close()  # 新建sqlite数据库


driver = get_driver()
global_config = driver.config


# Todo 读取全局配置
@driver.on_startup
async def connect():
    await Tortoise.init(db_url=global_config.db_url,
                        modules={"models": ["plugins.tortoise_orm.model"]},
                        timezone='Asia/Shanghai')
    await Tortoise.generate_schemas()
    logger.opt(colors=True).success("<y>数据库: 连接成功</y> ")
    # 当程序启动，读取数据库中 TwentyEightRecord，若为第一次启动，则写入首期；若启动时当期不为最新，写入最新
    lastest = await TwentyEightRecord.all().order_by("-period").first().values_list("period", "lottery_date")
    try:
        lastest_game, lastest_date = lastest[0], lastest[1]
        if (not bool(lastest_game)) or lastest_date.date() != date.today():
            await reset_record()
    except TypeError or UnboundLocalError:
        await reset_record()


@driver.on_shutdown
async def disconnect():
    await Tortoise.close_connections()
    logger.opt(colors=True).success("<y>数据库: 断开链接</y>")
    await get_bot().call_api("send_message", chat_id=global_config.chat_id, text='好的呀，机器人已经成功关闭了！需要我的时候记得再启动我哦！(｡･ω･｡)ﾉ♡')


async def reset_record():
    today_period = int(date.today().strftime("%Y%m%d") + '001')
    # await SystemConfig.filter(id=1).delete()
    # await SystemConfig.update_or_create(id=1,newest_period=today_period, everyday_game_times=1)
    first_id = await SystemConfig.first().values_list("id", flat=True)
    if not first_id:
        await SystemConfig(newest_period=today_period, everyday_game_times=1).save()
    else:
        await SystemConfig.filter(id=first_id).update(newest_period=today_period, everyday_game_times=1)
    await Users.all().update(allowance=False)
    logger.success('使用当天第一期, 当天次数已归零')
