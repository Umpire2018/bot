from pydantic import BaseModel
from nonebot import get_driver


class Config(BaseModel):
    allow_bet: bool = True


plugin_config = Config.parse_obj(get_driver().config)


async def reverse_allow_bet() -> bool:
    return not plugin_config.allow_bet


async def get_allow_bet() -> bool:
    return plugin_config.allow_bet
