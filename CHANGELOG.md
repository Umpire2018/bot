# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.7] - 2023-08-10

### Fixed 

- 修复夜间未封盘


## [0.3.7] - 2023-08-10

### Changed 

- 使用 bulk update 处理用户积分
- blackjack init.

### Fixed 

- 定时任务没有在早八点时运行
- /me 时 发生错误


## [0.3.6] - 2023-08-09

### Changed 

- 修改定时器设置方式


## [0.3.5] - 2023-08-08

### Fixed 

- 增加 /bet 双 的错误处理
- 修复封盘 error

### Changed

- 在处理用户下注与加群增加随机延迟以避免出现 429 报错

## [0.3.4] - 2023-08-07

### Changed

- 将 text_mention 更改为 发送 raw_str 以避免无法处理用户名中的非 acsii 字符
- 将下注利润更改为发送私聊信息
- 入群消息提示取消 text_mention

### Fixed

- 修复 /rankday 未正常显示


## [0.3.3] - 2023-08-07

**程序上线啦**

### Fixed

- 修复下注后用户积分未正确写入数据库
- 修复 /point 回复了错误的信息

## [0.3.2] - 2023-08-06

### Changed

- 增加 /低保 
- 增加低保相关逻辑
- Users 表增加低保字段
- 移除 bot.py 以适应多平台
- 重写处理用户积分


## [0.3.1] - 2023-08-05

### Changed

- 增加劝赌语句
- 增加若用户名过长，使用用户名 + '...'
- 使用 get 方法来获取数据库对象与用户名
- 删除设定倍率方法，设定默认倍率为 2
- 在 .prod 中增加相关信息

### Fixed

- 对 allin 增加错误处理
- 修复 allin 未写入下注记录
- 修复使用 user.id 的 typo.

## [0.3.0] - 2023-08-04

### Changed

- 删除测试阶段重置积分语句
- 更改发送利润图片为文本消息，取消使用机器人发送利润信息
- /start 防止用户多次使用

## [0.2.9] - 2023-08-03

### Changed

- 删除测试阶段重置积分语句
- 全局设定时区
- 增加开奖后判断当期时间时间，若距离23：59小于三分钟，暂停定时器
- 更新获取 hash
- 增加 /point /me 


## [0.2.8] - 2023-08-02

### Fixed

- 修复用户下注未被正确处理.
- 将每张图片保存为 500 dpi, 发送后关闭图片.
- 修复开奖后下注利润未被正确处理.
- 在获取hash中增加重试机制以规避error.

### Changed

- 更改机器人启动提示.

## [0.2.7] - 2023-08-01

### Changed

- 将图片保存到字节对象中以减少内存用量.
- 增加内存监控.
- 重写获取 eth hash 在 async_hash_fetcher.py.
- 精简发送图片的错误处理.
- 增加 nonebot-plugin-logpile 以保存日志到本地


## [0.2.6] - 2023-07-27

### Changed

- 重写重设期号方法
- 增加更多 eth endpoint.
- 更改禁言时间为30s.
- 防止用户多次下注.
- 增加Liux service 文件.
- 修改 dataframe 序号为1开始
- 用户下注时不乘以倍率，赌输时不乘以倍率。


### Fixed

- Fix wrong str in get_twenty_eight_result.
- 尝试修复发送图片时报错
- 用户积分没有在开奖时正确处理

## [0.2.5] - 2023-07-27

### Changed

- 当下注时，不应乘以倍率.
- 游戏间隔更改为三分钟
- 修复发送开奖提示时的显示错误
- 增加测试阶段在用户开奖后重新赋分
- try to fix tortoise.exceptions.IntegrityError: UNIQUE constraint failed: TwentyEightRecord.period.
- 修改profit photo size and other photo details.
- 当期开奖后增加可以下注的提示

## [0.2.4] - 2023-07-27

### Changed

- Use asyncio to get eth hash form different endpoint to avoid network failure.
- User need to be created by private message .

### Fixed

- Fix send str don't use BeiJing time.

## [0.2.3] - 2023-07-27

### Changed

- Modify send photo logic to avoid restart wirte-orm error.
- Use text mention to inform user bet.
- Send private message to inform user bet result.
- Add retry in get eth result to avoid IndexError.

## [0.2.2] - 2023-07-27

### Changed

- Change bet_history dataframe order.
- Add period_info to TwentyEightRecord to show better bet_history.
- Modify photo config and set column width.
- Add period time to period history photo.

### Fixed

- Fix No-one-bet condition.
- Fix wrong time save logic.

## [0.2.1] - 2023-07-26

### Fixed

- Fix send photo logic.

## [0.2.0] - 2023-07-25

### Fixed

- Fix wrong parameter place in bot.py .
- Fix wrong period time when saving.

### Changed

-  Use plottable and matplotlib to plot but waiting for fix bug.
-  Upload related doc.
-  Add blackjack and waiting for rebuild.

## [0.1.1] - 2023-07-23

### Changed

- Update README.md .
- Deleted can_send_media_messages bool value in start_bet_at_8.

### Fixed

- Fix wrong bool value in start_bet_at_8.

## [0.1.0] - 2023-07-23
* Initial release.