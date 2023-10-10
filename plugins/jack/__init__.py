from nonebot import on_command
from nonebot.adapters.telegram import Bot
from nonebot.adapters.telegram.event import GroupMessageEvent
from nonebot.params import Message, CommandArg

blackjack = on_command("21点", aliases={"发起21点"})