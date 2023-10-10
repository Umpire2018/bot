import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from datetime import datetime
from hashlib import sha3_256  # use sha-3 instead of sha-1
from math import pow
from pathlib import Path
from pandas import DataFrame
from plottable import Table, ColumnDefinition
from plugins.tortoise_orm.model import TwentyEightRecord, TwentyEightRecordHistory, SystemConfig, Users
from pytz import timezone
from plugins.twenty_eight.async_hash_fetcher import AsyncHashFetcher
from nonebot.log import logger
from io import BytesIO
from nonebot.adapters.telegram.message import Entity


fontManager.addfont(str(Path("plugins/twenty_eight/fonts/LXGWWenKaiMono-Regular.ttf")))
plt.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]
plt.rcParams["axes.unicode_minus"] = False

pow_2_64 = pow(2, 64)

async def get_twenty_eight_result():
    async with AsyncHashFetcher() as fetcher:
        hash_raw = await fetcher.get_fastest_hash()
        
    hash_sha256 = sha3_256(hash_raw.encode("utf-8")).hexdigest()
    hash_10 = int(hash_sha256[0:16], 16)
    number_3_str = str(hash_10 / pow_2_64)[2:5]
    number_3_format: str = '{} + {} + {} = '.format(number_3_str[0], number_3_str[1], number_3_str[2])

    number_3_sum: int = sum(list(map(int, number_3_str)))
    number_3_format += str(number_3_sum)  # 形如 1 + 2 + 3 = 6

    number_3_sum_flag = {"大数小数": "", "单数双数": "", "组合": ""}

    if (number_3_sum % 2) == 0:
        number_3_sum_flag["单数双数"] = "双"
    elif (number_3_sum % 2) != 0:
        number_3_sum_flag["单数双数"] = "单"
    if number_3_sum < 14:
        number_3_sum_flag["大数小数"] = "小"
    elif number_3_sum > 13:
        number_3_sum_flag["大数小数"] = "大"
    number_3_sum_flag["组合"] = ''.join(number_3_sum_flag.values())
    send_str: str = '''
开奖时间：{} 
当天第 {} 期
开奖结果：{} {}
当前开奖区块哈希值：{}
        '''.format(datetime.now(timezone('Asia/Shanghai')).strftime("%m-%d %H:%M:%S"),
                   await SystemConfig.first().values_list("everyday_game_times", flat=True),
                   number_3_format,
                   number_3_sum_flag["组合"],
                   hash_raw)

    await TwentyEightRecord(period=await SystemConfig.first().values_list("newest_period", flat=True),
                            eth_hash=hash_raw, three=number_3_str,
                            period_result=number_3_sum_flag["组合"], period_info=number_3_format
                            ).save()

    return send_str, number_3_sum_flag["组合"]


async def handle_all_history() -> tuple[str, bool, BytesIO]:
    num = await SystemConfig.first().values_list("everyday_game_times", "newest_period")
    text = '''
游戏仅供娱乐，请勿沉迷，本游戏不涉及充值提现，不涉及任何金钱赌博行为。
当前时间：{}
当天第 {} 期封盘
群组禁言中
'''.format(datetime.now(timezone('Asia/Shanghai')).strftime("%m-%d %H:%M:%S"),
           num[0])
    data: list = []
    bet_history: list = await TwentyEightRecordHistory.filter(period=num[1]).all().values("tg_id", "bet_log")
    # [{'tg_id': '12345678', 'bet_log': {'单': '1'}}]
    if bet_history:
        for bet_history_value in bet_history:
            name = {
                "用户名": await Users.filter(tg_id=bet_history_value["tg_id"]).first().values_list("name", flat=True)}
            name.update(bet_history_value["bet_log"])
            data.append(name)  # [{'用户名': 'tele', '单': '1'}]

        columns = ['用户名', '大', '小', '单', '双']
        dataframe = DataFrame(columns=columns)._append(data).fillna('')
        dataframe.index.name = '序号'
        dataframe.index += 1

        fig, ax = plt.subplots(figsize=(10, 10))
        tab = Table(dataframe,
                    textprops={"ha": "center", "weight": "bold", 'fontsize': '20'},
                    odd_row_color='#f8f9fa',  # 设定表格奇数偶数行底色
                    even_row_color='white',
                    column_definitions=[
                        ColumnDefinition(name='用户名', width=5),
                        ColumnDefinition(name='序号', width=0.5),
                        ColumnDefinition(name='单', width=1.5),
                        ColumnDefinition(name='双', width=1.5),
                        ColumnDefinition(name='大', width=1.5),
                        ColumnDefinition(name='小', width=1.5)])
        buffer = BytesIO()
        fig.savefig(buffer, format="jpg", dpi=500)
        buffer.seek(0)
        send_photo_flag = True
        plt.close()
    else:
        text += '当期无人下注！'
        send_photo_flag = False
        buffer = None
        
    return text, send_photo_flag, buffer


async def handle_user_point(result: str):
    current_period = await SystemConfig.first().values_list("newest_period", flat=True)
    bet_history: list = await TwentyEightRecordHistory.all().filter(
        period=current_period).values("tg_id","bet_log")  # [{'tg_id': '5872091317', 'bet_log': {"单":"50","大":"100"}}]

    if bet_history:
        profit_message = "用户当期利润 \n"
        send_user_message = []
        users_to_update = []

        # Fetch all users in one query
        user_ids = [bet_history_dict['tg_id'] for bet_history_dict in bet_history]
        users = await Users.filter(tg_id__in=user_ids)
        user_dict = {user.tg_id: user for user in users}

        for i, bet_history_dict in enumerate(bet_history, start=1):
            user = user_dict[bet_history_dict['tg_id']]
            bet_profit = 0
            for x, y in bet_history_dict['bet_log'].items():
                if x in result:
                    bet_profit += int(y) 
                else:
                    bet_profit -= int(y)

            await TwentyEightRecordHistory.filter(tg_id=bet_history_dict['tg_id'], period=current_period).update(bet_profit=bet_profit)
            user.point += bet_profit
            user.overall_game_times += 1
            users_to_update.append(user)

            profit_message += f'{i}. ' + user.name
            if bet_profit > 0 :
                profit_message += f' 赢得了 {bet_profit} 分 '
                send_user_message.append({'tg_id': bet_history_dict['tg_id'],"message":f'恭喜！您猜中了 {current_period} 期 \n赢得了 {bet_profit} 分 \n当前积分 {user.point}'})
            if bet_profit < 0 :
                profit_message += f' 输掉了 {abs(bet_profit)} 分'
                send_user_message.append({'tg_id': bet_history_dict['tg_id'],"message":f'抱歉！您未猜中 {current_period} 期 \n输掉了 {abs(bet_profit)} 分 \n当前积分 {user.point}'})
            
            profit_message += f' 当前积分：{user.point}\n'

        # Update all users in one operation
        await Users.bulk_update(users_to_update, fields=['point', 'overall_game_times'])

        return profit_message, send_user_message
    else:
        pass


async def handle_history_period():
    result_list: list = await TwentyEightRecord.all().order_by("-period").limit(15).values("period", "period_result",
                                                                                           "period_info",
                                                                                           'lottery_date')
    # [{"period":"123","period_result":"大单"}]
    history = []
    for x in result_list:
        empty_dict = {}
        empty_dict.update({"期数": x["period"]})
        for a in x["period_result"]:
            empty_dict.update({a: a})
        empty_dict.update({"开奖结果": x["period_info"], "开奖时间": x["lottery_date"].strftime("%m-%d %H:%M")})
        history.append(empty_dict)  # [{'期数': '20230726001', '大': '大', '单': '单'}]

    fig, ax = plt.subplots(figsize=(14, 4))  # 宽度，高度
    # dataframe = DataFrame(dataframe)[['期数', '大', '小', '单','双']].fillna('') # 转换为 pandas DataFrame 对象，重新设定列顺序，对列中 NAN 值使用 '' 进行填充
    columns = ['期数', '大', '小', '单', '双', '开奖结果', '开奖时间']
    temp_empty_dict = {}
    dataframe = DataFrame(columns=columns)._append(history)
    for columns_value in columns[1:-2]:
        try:
            temp_empty_dict.update({columns_value: dataframe[columns_value].value_counts().values[0]})
        except IndexError:
            pass


    temp_empty_dict.update({'期数': '合计'})
    dataframe = dataframe._append(temp_empty_dict, ignore_index=True).fillna('')
    dataframe.index += 1
    fig, ax = plt.subplots(figsize=(12, 8))
    tab = Table(dataframe,
                textprops={"ha": "center", 'fontsize': '20', "weight": "bold"},
                index_col='期数',
                odd_row_color='#f8f9fa',  # 设定表格奇数偶数行底色
                even_row_color='white',
                column_definitions=[
                    ColumnDefinition(name='大', width=0.8),
                    ColumnDefinition(name='小', width=0.8),
                    ColumnDefinition(name='单', width=0.8),
                    ColumnDefinition(name='双', width=0.8),
                    ColumnDefinition(name='期数', width=2),
                    ColumnDefinition(name='开奖结果', width=2.5),
                    ColumnDefinition(name='开奖时间', width=2)]
                )

    tab.columns['大'].set_fontcolor("red")
    tab.columns['小'].set_fontcolor("blue")
    tab.columns['单'].set_fontcolor("green")
    tab.columns['双'].set_fontcolor("purple")
    buffer = BytesIO()
    fig.savefig(buffer, format="jpg")
    buffer.seek(0)
    plt.close()
    return buffer