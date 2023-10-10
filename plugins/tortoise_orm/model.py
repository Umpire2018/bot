from tortoise import fields
from tortoise.models import Model
from nonebot import get_driver

global_config = get_driver().config


class Users(Model):
    # 若不设定主键，ORM自动创建 id 自增主键列
    name = fields.TextField(description="telegram 用户名")
    tg_id = fields.CharField(description="telegram 用户id",max_length=20, index=True)
    point = fields.IntField(description="积分数量", default=global_config.default_point)
    overall_game_times = fields.IntField(description="游戏总次数", default=0)  # TODO
    allowance = fields.BooleanField(description="当日是否领取低保", default=False)

    class Meta:
        table = "Users"
        table_description = "用户"


class TwentyEightRecord(Model):
    period = fields.CharField(pk=True, max_length=12, description="当期", index=True)  # 形如20230705001
    lottery_date = fields.DatetimeField(description="当期开奖时间", auto_now=True, null=True)  # 创建对象时即设置时间
    eth_hash = fields.TextField(description="开奖时ETH最新区块高度", null=True)
    # 改为仅存储小数点后三位
    three = fields.IntField(description="小数点后三位", null=True)
    period_info = fields.TextField(description="当期加和提示", null=True)
    period_result = fields.TextField(description="当期开奖结果", null=True)
    head_count = fields.IntField(description="当期参与人数", null=True)

    class Meta:
        table = "TwentyEightRecord"
        table_description = "28 游戏开奖记录"


class TwentyEightRecordHistory(Model):
    period = fields.CharField(max_length=12, description="周期")
    tg_id = fields.CharField(description="telegram 用户id",max_length=20, index=True)
    bet_log = fields.JSONField(description="用户下注记录", null=True)
    bet_time = fields.DatetimeField(description="下注时间", auto_now_add=True)
    bet_profit = fields.IntField(description="本次游戏盈亏", null=True)

    class Meta:
        table = "TwentyEightRecordHistory"
        table_description = "28 游戏下注记录"


class SystemConfig(Model):
    twentyeight_magnification = fields.IntField(description="游戏倍率", default=2)
    newest_period = fields.IntField(description="游戏最新周期", default=1)
    everyday_game_times = fields.IntField(description="当天游戏次数", default=1)

    class Meta:
        table = "SystemConfig"
        table_description = "游戏相关全局配置"
