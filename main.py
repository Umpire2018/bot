import os
from nonebot.adapters.telegram import Adapter as TelegramAdapter
from pathlib import Path
import nonebot

# Set the timezone
os.environ['TZ'] = 'Asia/Shanghai'

# 初始化 NoneBot
nonebot.init(_env_file=".env.prod")

app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(TelegramAdapter)

# nonebot_plugin_sentry
nonebot.load_plugin("nonebot_plugin_logpile")  
nonebot.load_plugin(Path("plugins/tortoise_orm"))
nonebot.load_plugin(Path("plugins/twenty_eight"))
nonebot.load_plugin(Path("plugins/scheduler"))

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")

    
