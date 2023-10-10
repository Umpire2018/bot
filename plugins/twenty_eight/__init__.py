import asyncio
import random
from .config import  get_allow_bet
from nonebot import on_command, on_notice, get_driver
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from plugins.tortoise_orm.model import Users, TwentyEightRecordHistory, SystemConfig
from nonebot.adapters.telegram import Message, Bot
from nonebot.adapters.telegram.event import GroupMessageEvent, PrivateMessageEvent, NewChatMemberEvent
from nonebot.adapters.telegram.exception import ActionFailed
from tortoise.exceptions import DoesNotExist
from .utils import get_user_info, parse_bet
from nonebot.log import logger


async def random_sleep():
    sleep_duration = random.uniform(1, 3)  # Generate a random float between 1 and 3
    await asyncio.sleep(sleep_duration)  # Sleep for the generated duration


global_config = get_driver().config

welcome = on_notice()


@welcome.handle()
async def welcome_handle(event: NewChatMemberEvent) -> None:
    """ 当用户加入了指定群聊后，写入初始积分值，发送入群提示。
 
    :param 响应 NewChatMemberEvent 
    :return: None
    """
    if event.chat.id == global_config.chat_id and event.from_.is_bot != True :
        user = event.from_  
        await welcome.send(f'欢迎 {user.first_name} 加入，请点击 @{global_config.bot_username} 完成账号登记', reply_to_message_id=event.message_id)
        await random_sleep()

start = on_command("start")

@start.handle()
async def handle_function(event: PrivateMessageEvent, bot: Bot) -> None:
    """ 处理用户信息，写入默认积分。

    :param event PrivateMessageEvent 仅响应私聊消息
    :param bot Bot
    :return: None
    """
    try:
        # 若用户不在设定群聊中，则不允许开注
        chat_member = await bot.get_chat_member(chat_id=global_config.chat_id, user_id=event.get_user_id())
        new_user = chat_member.user
        if len(new_user.first_name) > 10:
            new_user.first_name = new_user.first_name[:10] + '...'

        # 优化：只查询一次数据库，获取或创建用户
        user_obj, created = await Users.get_or_create(tg_id=event.get_user_id(), defaults={'name': new_user.first_name})
        if created:
            await start.finish(f'欢迎加入我们！您已经拥有超级可爱的 {global_config.default_point} 分啦！💖')
        else:
            await start.finish(f'欢迎回来！您的积分为：{user_obj.point}')
    except ActionFailed:
        await start.reject(f'您未获取使用权限，请先加入群聊。')


set_user_bet = on_command("bet", aliases={"下注"}, rule=get_allow_bet)


# 1. 设置命令是否生效，是否仅群聊可用
@set_user_bet.handle()
async def handle_function(event: GroupMessageEvent, args: Message = CommandArg()) -> None:
    """ 设定用户赌注

    :param event GroupMessageEvent 仅响应群聊
    :param args 获取消息命令后跟随的内容
    :return: None
    """
    try:
        user = await get_user_info(event.get_user_id())
        if user.allowance and user.point < 1:
            await set_user_bet.reject(f'您已用完当日低保所给分数，请明天领取低保后再进行游戏', reply_to_message_id=event.message_id)
        elif user.point < 1:
            await set_user_bet.reject(f'您的积分不足，请向 @{global_config.bot_username} 发送私聊信息 /低保 来获取当天一次性低保', reply_to_message_id=event.message_id)

        # Parse the user's bet input
        result = await parse_bet(args.extract_plain_text())
        if isinstance(result, str):
            await set_user_bet.reject(result, reply_to_message_id=event.message_id)
        else:
            user_bet_json = result

        user_bet_point = 0
        for i in user_bet_json.values():
            user_bet_point = user_bet_point + int(i)

        if user_bet_point > user.point:
            await set_user_bet.reject(f"你想使用{user_bet_point}分，但你当前的积分为{user.point},无法完成下注", reply_to_message_id=event.message_id)
    
        user_bet_record, created = await TwentyEightRecordHistory.get_or_create(
            period=await SystemConfig.first().values_list("newest_period", flat=True),
            tg_id=event.get_user_id(),
            defaults={'bet_log': user_bet_json}
        )
        if created:
            await random_sleep()
            await set_user_bet.finish(f'您下注为 {args.extract_plain_text()}', reply_to_message_id=event.message_id)
        else:
            await set_user_bet.finish(f'本期您已下注。', reply_to_message_id=event.message_id)
    except DoesNotExist:
        await set_user_bet.reject(f'噢噢噢，您还没有进行账号登记呢！请您点击 @{global_config.bot_username} 这样才能继续使用相关功能哦！麻烦您尽快完成账号登记吧！(ﾟ´ω`ﾟ)ﾟ', reply_to_message_id=event.message_id)

    


rankday = on_command("rankday", aliases={"积分排行榜"})


@rankday.handle()
async def handle_function(event: GroupMessageEvent, bot:Bot) -> None:
    # Get the top 10 users with the highest points in one operation
    top_users = await Users.all().order_by('-point').limit(10).values('name', 'point')
    # Generate the ranking message
    ranking_message = "用户积分排行榜：\n"
    for i, user in enumerate(top_users, start=1):
        ranking_message += f"{i}. {user['name']}.   {user['point']}分\n"
    # Send the message
    await bot.send_to(chat_id=global_config.chat_id, message=ranking_message)

me = on_command("me",aliases={"我"})


@me.handle()
async def handle_function(event: PrivateMessageEvent) -> None:
    try:
        user = await Users.get(tg_id=event.get_user_id())
        await me.finish(f'''
    telegram id: {user.tg_id}                    
    用户名：{event.from_.first_name}         
    积分数量：{user.point}           
    ''')
    except DoesNotExist:
        await me.reject(f'噢噢噢，您还没有进行账号登记呢！请您重新发送 /start 这样才能继续使用相关功能哦！麻烦您尽快完成账号登记吧！(ﾟ´ω`ﾟ)ﾟ', reply_to_message_id=event.message_id)

    
point = on_command("point", permission=SUPERUSER)


@point.handle()
async def handle_function(event: GroupMessageEvent, args: Message = CommandArg()) -> None:
    reply_user_id = event.reply_to_message.get_user_id()
    if not reply_user_id:
        point.reject('亲爱的管理员您好，未获取到用户信息，请转发信息后输入命令。')

    # Get the user's points and send the message in one operation
    user = await Users.get(tg_id=reply_user_id)
    await point.finish(f'亲爱的管理员您好！查询到 {user.name} 目前有 {user.point} 分', reply_to_message_id=event.message_id)

allin = on_command("allin", aliases={'梭哈'})


@allin.handle()    
async def handle_function(event: GroupMessageEvent, args: Message = CommandArg()) -> None:
    try:
        # Combine two database queries into one
        user, system_config = await asyncio.gather(
            get_user_info(event.get_user_id()),
            SystemConfig.first().values_list("newest_period", flat=True)
        )
        try:
            content = args.extract_plain_text().split()[0]
        except IndexError:
            logger.warning(args.extract_plain_text())
            await allin.reject('您的命令格式有误，请重新输入', reply_to_message_id=event.message_id)
        if user.allowance and user.point < 1:
            await allin.reject('您已用完当日低保所给分数，请明天领取低保后再进行游戏', reply_to_message_id=event.message_id)
        elif user.point < 1:
            await allin.reject(f'您的积分不足，请向 @{global_config.bot_username} 发送私聊信息 /低保 来获取当天一次性低保', reply_to_message_id=event.message_id)
        elif len(content) == 1 and content in ['单', '双', '小', '大']:
            history, created = await TwentyEightRecordHistory.get_or_create(
                period=system_config,
                tg_id=event.get_user_id(),
                defaults={'bet_log': {content: str(int(user.point))}}  # Set bet_log value when creating the record
            )
            if created:
                await random_sleep()
                await allin.finish(f'已为您在 {content} 上下注 {user.point} 分', reply_to_message_id=event.message_id)
            else:
                # Give a more specific error message
                await allin.finish(f'本期({system_config})您已下注。', reply_to_message_id=event.message_id)
        else:
            await allin.reject(f'您的输入格式有误，请重新输入', reply_to_message_id=event.message_id)
    except DoesNotExist:
        await allin.reject(f'噢噢噢，您还没有进行账号登记呢！请您点击 @{global_config.bot_username} 这样才能继续使用相关功能哦！麻烦您尽快完成账号登记', reply_to_message_id=event.message_id)

allowance = on_command("allowance", aliases={'低保'})


@allowance.handle()    
async def handle_function(event: PrivateMessageEvent, args: Message = CommandArg()) -> None:
    try:
        user = await Users.get(tg_id=event.get_user_id())
        if user.point == 0 and not user.allowance :
            await Users.filter(tg_id=event.get_user_id()).update(allowance=True, point=global_config.default_point / 2)
            await allowance.finish(f'已为您重设积分值为 {int(global_config.default_point / 2)} 分')
        else:
            await allowance.finish('您今天已领取过低保或积分不为零啦')
    except DoesNotExist:
        await allowance.reject(f'噢噢噢，您还没有进行账号登记呢！请您点击 @{global_config.bot_username} ，这样才能继续使用相关功能哦！麻烦您尽快完成账号登记', reply_to_message_id=event.message_id)

