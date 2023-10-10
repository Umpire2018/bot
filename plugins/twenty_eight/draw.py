import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from pathlib import Path
from pandas import DataFrame
from plottable import Table, ColDef

fontManager.addfont(str(Path("plugins/twenty_eight/fonts/LXGWWenKaiMono-Regular.ttf")))
plt.rcParams["font.sans-serif"] = ["LXGW WenKai Mono"]
plt.rcParams["axes.unicode_minus"] = False

a = [{'用户名': 'norman_tele', '单': '1'}, {'用户名': '七七', '单': '1'}]
b = [{'期数': '20230726001', '大': '大', '单': '单'},{'期数': '20230726001', '大': '大', '双': '双'}]
c = [{'用户名': '77', '利润': 2}]
new = []
fig, ax = plt.subplots(figsize=(6, 4)) # 宽度，高度
columns = ['期数', '大', '小', '单','双','开奖结果']
data = DataFrame(columns=columns)._append(b).fillna('')
dict1 = {}

for i in columns[1:-1]:
    dict1.update({i:data[i].value_counts().values[0]})

#dict1.update({'期数':'合计'})
new.append(dict1)
print(new)

data = data._append(dict1, ignore_index=True)
print(data)

'''tab = Table(data,
            index_col='期数',
            textprops={"ha": "center", "weight": "bold"},
            column_definitions=[
                ColDef(name='用户名', width=4)
            ])


fig.savefig("a.png", dpi=300)
plt.show()'''
