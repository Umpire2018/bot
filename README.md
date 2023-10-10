[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

# 项目介绍

一个使用 Nonebot2 做为基础框架，使用 tortoise orm 做为数据库连接组件，用于在群组中支持28点游戏的 Telegram Bot.

## 安装

	# 项目使用 pdm 来管理依赖
	curl -sSL https://pdm.fming.dev/dev/install-pdm.py | python3 -
	pdm install

## 逻辑说明

1. start 按bot.py设定顺序载入插件
2. tortoise_orm start 在驱动器启动时连接数据库 检查数据库中有无记录，若无记录，则写入最新游戏。在驱动器关闭时关闭数据库连接。
   - 数据库定义如 model.py所示，其中 TwentyEightRecord 表中将小数点后三位保存在一个 str 中。SystemConfig 表仅存储一行来保存经常需要查询的倍率，期数等内容来保证内容一致。其他表的期数为查询此表的期数。
3. twenty_eight start 定义了命令与入群欢迎功能
   - 入群欢迎 当检测到新成员入群事件，则将新用户的信息写入user表，并给予默认积分
   - /magnification /设定倍率 数量  对传入倍率值进行检查，需要处于上下限中
   - /bet /下注 单 1 大 2 当前仅支持此格式。对格式进行检查，若不符合（格式、互斥、重复、其他），要求重新输入。将下注记录以json 格式保存形如
{"单":"1","大":"2"}  对用户下注积分与用户积分进行比较，若大于则不允许下注。对若下注时发现用户没有积分时，写入默认积分。
4. scheduler 使用 nonebot_plugin_apscheduler 定义了三个定时任务与一个在机器人启动时发送文字的普通任务。
   - 在每天八点时运行，在群里发送文字，结束群聊禁言。
   - 每小时08分开始，58分结束，每隔十分钟禁言并封盘，发送所有人的下注记录。
   - 每小时09分开始，59分结束，每隔十分钟获取当期结果，发送开奖结果，所有人的当期盈亏，对数据库将相关结果进行写入。当天时间为23：59分时，提示当天无法下注。

## Todo

1. 排行榜命令 /top 参数：num_day 当天下注次数最多用户; point 积分数量最多用户
2. 查看命令，响应私聊，/me 查看用户信息如积分、用户名等


## 改善

在代码中，有一些数据库操作可以进行优化：

批量操作: 在处理大量数据时，尽可能使用批量操作，例如 bulk_create，bulk_update 等，这样可以减少数据库的访问次数，提高效率。

避免重复查询: 在代码中，有些地方对同一数据进行了多次查询，这是不必要的。可以将查询结果保存在变量中，以便后续使用。

优化查询: 使用 select_related 或 prefetch_related 来优化关联查询，减少数据库查询次数。

索引: 对经常需要查询的字段建立索引，可以提高查询速度。


## 设计
1. 若中途有原因退出时，复用当前期数，如八点十分启动，八点十五分退出，十四点重启，使用八点十分的期数

## Documentation

- [Nonebot](https://v2.nonebot.dev/)
- [21点 Blackjack](https://hub.fgit.ml/yaowan233/nonebot-plugin-blackjack)
- [tortoise orm](https://tortoise.github.io/reference.html)
- [通用 ORM 数据库连接插件](https://hub.fgit.ml/kexue-z/nonebot-plugin-tortoise-orm/tree/master)
- [一个简单的 sqlite 在线查看网站](https://sqliteviewer.app)
- [plottable 简明教程](https://www.cnblogs.com/feffery/p/17086814.html)
- [PDM Doc](https://pdm.fming.dev/latest/)