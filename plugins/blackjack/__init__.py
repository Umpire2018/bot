from nonebot import on_command
from nonebot.adapters.telegram import Bot
from nonebot.adapters.telegram.event import GroupMessageEvent

from nonebot.params import Message, CommandArg
from .game import get_point, add_game, start_game, call_card, stop_card, get_game_ls, duel, get_rank
from .sign import sign_today, get_point, update_point
from typing import Dict, List


blackjack = on_command("21点", aliases={"发起21点"}, priority=21, block=True)
accept_blackjack = on_command("接受游戏", aliases={'接受'}, priority=21, block=True)
blackjack_list = on_command("游戏列表", aliases={'列表'}, priority=21, block=True)
call = on_command("叫牌", aliases={'call'}, priority=21, block=True)
stop = on_command("停牌", aliases={'stop'}, priority=21, block=True)
sign = on_command("签到", priority=1, block=True)
point_battle = on_command("积分对战", aliases={"对战", "发起对战"}, priority=1, block=True)
accept_battle = on_command("接受对战", aliases={"dual"}, priority=1, block=True)
battle_list = on_command("对战列表", priority=1, block=True)
battle_dic: Dict[int, List[List[int]]] = {}


@blackjack.handle()
async def start_blackjack(event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.get_session_id().split('_')[1]
    user_id = event.get_user_id()
    point = msg.extract_plain_text().strip()
    player1_name = event.from_.first_name
    if not point.isdigit():
        await blackjack.finish("请输入正确的积分数！")
    point = int(point)
    user_point = get_point(group_id, user_id)
    if user_point < point:
        await blackjack.finish("你的点数不够！")
    deck_id = await add_game(group_id, user_id, point, player1_name)
    if deck_id >= 0:
        await blackjack.finish(f"游戏添加成功 游戏id为{deck_id}")
    else:
        await blackjack.finish("出错了QwQ 对战添加失败")


@accept_blackjack.handle()
async def accept(event: GroupMessageEvent, msg: Message = CommandArg()):
    group_id = event.get_session_id().split('_')[1]
    user_id = event.get_user_id()
    battle_id = msg.extract_plain_text().strip()
    player2_name = event.from_.first_name
    user_point = get_point(group_id, user_id)
    if not battle_id.isdigit():
        await accept_blackjack.finish("请输入正确的游戏id！", at_sender=True)
    words = await start_game(int(battle_id), user_id, player2_name, group_id, user_point)
    await accept_blackjack.finish(words, at_sender=True)


@call.handle()
async def _call(event: GroupMessageEvent, msg: Message = CommandArg()):
    user_id = event.get_user_id()
    deck_id = msg.extract_plain_text().strip()
    if not deck_id.isdigit():
        await call.finish("请输入正确的游戏id！", at_sender=True)
    words = await call_card(int(deck_id), user_id)
    await call.finish(words, at_sender=True)


@stop.handle()
async def _stop(event: GroupMessageEvent, msg: Message = CommandArg()):
    user_id = event.get_user_id()
    deck_id = msg.extract_plain_text().strip()
    if not deck_id.isdigit():
        await call.finish("请输入正确的游戏id！", at_sender=True)
    words = await stop_card(int(deck_id), user_id)
    await stop.finish(words, at_sender=True)


@blackjack_list.handle()
async def accept(event: GroupMessageEvent):
    group_id = event.get_session_id().split('_')[1]
    words = await get_game_ls(group_id)
    await blackjack.finish(words)


@sign.handle()
async def sign_in(event: GroupMessageEvent):
    group_id = event.get_session_id().split('_')[1]
    user_id = event.get_user_id()
    words = sign_today(user_id, group_id)
    await sign.finish(words)




def add_dual(group: int, uid: int, point: int) -> int:
    if group not in battle_dic or not battle_dic[group]:
        battle_dic[group] = [[1, uid, point]]
        return 1
    battle_id = battle_dic[group][-1][0] + 1
    battle_dic[group].append([battle_id, uid, point])
    return battle_id


def get_battle_info(group: int, battle_id: int) -> list:
    if group not in battle_dic or battle_id <= 0:
        return []
    for i in battle_dic[group]:
        if i[0] == battle_id:
            return i
    return []

