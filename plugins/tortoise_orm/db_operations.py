# db_operations.py
from tortoise.transactions import in_transaction
from plugins.tortoise_orm.model import Users, TwentyEightRecordHistory, SystemConfig

async def get_user(tg_id: int):
    return await Users.get(tg_id=tg_id)

async def get_or_create_user(name: str, tg_id: int):
    return await Users.get_or_create(name=name, tg_id=tg_id)

async def update_user(tg_id: int, allowance: bool, point: int):
    async with in_transaction() as connection:
        await Users.filter(tg_id=tg_id).using_connection(connection).update(allowance=allowance, point=point)

async def get_top_users(limit: int):
    return await Users.all().order_by('-point').limit(limit).values('name', 'point')

async def get_or_create_record(period: int, tg_id: int, bet_log: dict):
    return await TwentyEightRecordHistory.get_or_create(
        period=period,
        tg_id=tg_id,
        defaults={'bet_log': bet_log}
    )

async def get_newest_period():
    return await SystemConfig.first().values_list("newest_period", flat=True)