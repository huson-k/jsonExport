import pyecharts.options as opts
from pyecharts.charts import Line, Grid
import re

"""
Gallery 使用 pyecharts 1.1.0
参考地址: https://echarts.apache.org/examples/editor.html?c=line-stack

目前无法实现的功能:

暂无
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def jfNfwq(jf: str):
    if jf == '202':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK', 'LM', 'NP']  # AB-0,CD-1,EF-2,GH-3,JK-4,LM-5,NP-6
        KT_toFwq_list_1 = [[12], [10, 11], [8, 9, ], [6, 7], [4, 5],
                           [3], [1, 2]]
        KT_toFwq_list_2 = [[19, 20], [18, ], [17, ], [16, ], [15, ],
                           [14, ], [13, ]]
        ktNum = 20
    if jf == '203':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK']  # 203 AB-0,CD-1,EF-2,GH-3,JK-4,LM-5,NP-6
        KT_toFwq_list_1 = [[13], [12, 11], [10], [9], [8]]
        KT_toFwq_list_2 = [[7], [6], [5, 4], [3], [2, 1]]
        ktNum = 13
    if jf == '204':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK', 'LM', 'NP']  # 203 AB-0,CD-1,EF-2,GH-3,JK-4,LM-5,NP-6
        KT_toFwq_list_1 = [[1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [12]]
        KT_toFwq_list_2 = [[13], [14], [15], [16], [17], [18], [19, 20]]
        ktNum = 20
    return fwq, KT_toFwq_list_1, KT_toFwq_list_2, ktNum


jf = '203'
fwq, KT_toFwq_list_1, KT_toFwq_list_2, ktNum = jfNfwq(jf)
ifMean = True  # 是否在时间维度上做10min平均
# 冷通道组上中下分区标号
up_site_nums = [1, 9]
mid_site_nums = [10, 14]
dw_site_nums = [15, 23]


def createPowerName(fwqs: list, ktnum: int):
    fwqNames = []
    ktNames = []
    for fwq in fwqs:
        fwqNames.append('服务器' + fwq[0] + '功率')
        fwqNames.append('服务器' + fwq[1] + '功率')
    for kt in range(ktnum):
        ktNames.append('KT-' + str(kt + 1) + '-空调总有功功率')
    return fwqNames, ktNames


def createKTName(ktnum: int):
    Names = []
    for i in range(ktnum):
        i = i + 1
        Names.append('KT-' + str(i) + '-空调总有功功率')
        Names.append('KT-' + str(i) + '-压缩机1容量')
        Names.append('KT-' + str(i) + '-压缩机2容量')
        Names.append('KT-' + str(i) + '-冷凝风机1转速')
        Names.append('KT-' + str(i) + '-冷凝风机2转速')
        Names.append('KT-' + str(i) + '-风机1转速')
        Names.append('KT-' + str(i) + '-风机2转速')
        Names.append('KT-' + str(i) + '-送风温度1')
        Names.append('KT-' + str(i) + '-送风温度设定')
        for hf_num in range(1, 5):
            Names.append('KT-' + str(i) + '-回风温度' + str(hf_num))
        Names.append('KT-' + str(i) + '-回风温度设定')
    return Names


def site_names(up_site_nums: list, mid_site_nums: list, dw_site_nums: list):
    up_sites = np.arange(up_site_nums[0], mid_site_nums[0])
    mid_sites = np.arange(mid_site_nums[0], dw_site_nums[0])
    dw_sites = np.arange(dw_site_nums[0], dw_site_nums[1] + 1)
    up_sites = fillZero(up_sites)
    mid_sites = fillZero(mid_sites)
    dw_sites = fillZero(dw_sites)
    return up_sites, mid_sites, dw_sites


def fillZero(originalList: list):
    newList = [str(item).zfill(2) for item in originalList]
    return newList


def getFwqIndex(value, row):
    """根据空调号获取服务器索引"""
    index = []
    for i in range(len(row)):
        for j in range(len(row[i])):
            if ((row[i][j]) == value):
                index.append(i)
    return index


def cold_max_second(cold_temp):
    max_value, max_cedian, second_value, second_cedian, third_value, third_cedian = [], [], [], [], [], []

    for i in range(len(cold_temp)):
        temp = cold_temp.iloc[i, :]
        temp = temp.sort_values(ascending=False)
        max_value.append(temp[0])
        second_value.append(temp[1])
        third_value.append(temp[2])
        res = r'[A-Z](.*?)-'

        max_cedian.append(int(re.findall(res, temp.index[0][6:])[0]) + cedian_location(temp.index[0][-1]))
        second_cedian.append(int(re.findall(res, temp.index[1][6:])[0]) + cedian_location(temp.index[1][-1]))
        third_cedian.append(int(re.findall(res, temp.index[2][6:])[0]) + cedian_location(temp.index[2][-1]))

    return max_value, max_cedian, second_value, second_cedian, third_value, third_cedian


def cedian_location(x):
    # 上：小数点后为1
    # 下：小数点后为2
    if (x == '上'):
        return 0.1
    elif (x == '下'):
        return 0.2


def fwq_plot(data, fwq_index, time_range):
    data.reset_index(drop=True, inplace=True)
    # 压缩机容量，风机转速，送风温度，送风设定，回风温度，回风设定
    kt_list = KT_toFwq_list_1[fwq_index] + KT_toFwq_list_2[fwq_index]
    # 添加空调相关数据
    ysj1 = pd.DataFrame()
    ysj2 = pd.DataFrame()
    fj1 = pd.DataFrame()
    fj2 = pd.DataFrame()
    lnfj1 = pd.DataFrame()
    lnfj2 = pd.DataFrame()
    sf1 = pd.DataFrame()
    ktgl = pd.DataFrame()
    sfset = pd.DataFrame()
    hf_avg = pd.DataFrame()
    hfset = pd.DataFrame()
    pue = pd.DataFrame()
    for i in kt_list:
        ysj1 = pd.concat([ysj1, data[['KT-' + str(i) + '-压缩机1容量']]], axis=1)
        ysj2 = pd.concat([ysj2, data[['KT-' + str(i) + '-压缩机2容量']]], axis=1)
        fj1 = pd.concat([fj1, data[['KT-' + str(i) + '-风机1转速']]], axis=1)
        fj2 = pd.concat([fj2, data[['KT-' + str(i) + '-风机2转速']]], axis=1)
        lnfj1 = pd.concat([lnfj1, data[['KT-' + str(i) + '-冷凝风机1转速']]], axis=1)
        lnfj2 = pd.concat([lnfj2, data[['KT-' + str(i) + '-冷凝风机2转速']]], axis=1)
        sf1 = pd.concat([sf1, data[['KT-' + str(i) + '-送风温度1']]], axis=1)
        ktgl = pd.concat([ktgl, data[['KT-' + str(i) + '-空调总有功功率']]], axis=1)
        sfset = pd.concat([sfset, data[['KT-' + str(i) + '-送风温度设定']]], axis=1)
        # 回风温度，取全部平均
        hfwd_avg = []
        hfwd = []
        for hf_num in range(1, 5):
            hfwd.append(data[['KT-' + str(i) + '-回风温度' + str(hf_num)]])
            hfwd_avg.append(np.mean(hfwd))
        hf_avg = pd.concat([pd.DataFrame(hf_avg), pd.DataFrame(hfwd_avg, columns=['KT-' + str(i) + '-回风温度'])],
                           axis=1)
        hfset = pd.concat([hfset, data[['KT-' + str(i) + '-回风温度设定']]], axis=1)

    sf1 = round(sf1, 2)
    sf_avg = round(sf1.apply(lambda x: x.mean(), axis=1), 2)
    env = data['室外环境温度']

    fwqpower_columns, ktpower_columns = createPowerName(fwq, ktNum)
    # 只保留匹配的列
    df_fwqpower = data[fwqpower_columns]
    df_ktpower = data[ktpower_columns]
    # 计算PUE
    pue['服务器总功率'] = df_fwqpower.sum(axis=1)
    pue['空调总功率'] = df_ktpower.sum(axis=1)
    pue['机房总功率'] = pue.sum(axis=1)
    pue['pue'] = (pue['机房总功率'] / pue['服务器总功率']).round(4) * 10

    # 冷通道温度分区域取：
    if jf == '203':
        # 203测点相关
        cold_temp1 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][0])]]  # 服务器列 左
        cold_temp2 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][1])]]  # 服务器列 右
    if jf == '204':
        # 204 测点相关
        cold_temp1 = data[data.columns[data.columns.str.contains('FT-' + jf + '-' + fwq[fwq_index][0])]]  # 服务器列 左
        cold_temp2 = data[data.columns[data.columns.str.contains('FT-' + jf + '-' + fwq[fwq_index][1])]]  # 服务器列 右

    cold_avg1 = round(cold_temp1[cold_temp1 > 10].mean(axis=1), 2)

    cold_avg2 = round(cold_temp2[cold_temp2 > 10].mean(axis=1), 2)  # 服务器列 右 平均温度

    cold_avg = round((cold_avg1 + cold_avg2) / 2, 2)  # 该服务器组整体平均温度

    cold_max1, cold_max1_location, cold_second1, cold_second1_location, cold_third1, cold_third1_location = cold_max_second(
        cold_temp1)
    cold_max2, cold_max2_location, cold_second2, cold_second2_location, cold_third2, cold_third2_location = cold_max_second(
        cold_temp2)

    title = time_range
    print('所导html 时间跨度：' + title)

    c = (
        Line(
            # init_opts=opts.InitOpts(width='1500px',height='700px')
        )
        # .add_xaxis(xaxis_data=range(0,len(ysj)))
        .add_xaxis(xaxis_data=data['sampleTime'])

        .add_yaxis(
            series_name="室外环境温度",
            # stack="总量",
            y_axis=env,
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False
        )
        .add_yaxis(
            series_name="PUE",
            y_axis=pue['pue'],
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False
        )
        .add_yaxis(
            series_name='服务器' + fwq[fwq_index][0] + '功率',
            # stack="总量",
            y_axis=data['服务器' + fwq[fwq_index][0] + '功率'],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name='服务器' + fwq[fwq_index][1] + '功率',
            # stack="总量",
            y_axis=data['服务器' + fwq[fwq_index][1] + '功率'],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][0] + '冷通道温度平均值',
            # stack="总量",
            y_axis=cold_avg1,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][1] + '冷通道温度平均值',
            # stack="总量",
            y_axis=cold_avg2,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][0] + fwq[fwq_index][1] + '冷通道组温度平均值',
            # stack="总量",
            y_axis=cold_avg,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][0] + '冷通道温度最大值',
            # stack="总量",
            y_axis=cold_max1,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][1] + '冷通道温度最大值',
            # stack="总量",
            y_axis=cold_max2,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][0] + '冷通道温度最大值测点位置',
            y_axis=cold_max1_location,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][1] + '冷通道温度最大值测点位置',
            y_axis=cold_max2_location,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][0] + '冷通道最大值与平均值差值',
            y_axis=cold_max1 - cold_avg1,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index][1] + '冷通道最大值与平均值差值',
            y_axis=cold_max2 - cold_avg2,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name='送风平均温度',
            y_axis=sf_avg,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, pos_top='18%', pos_left='20%'),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            datazoom_opts=[opts.DataZoomOpts()],
            xaxis_opts=opts.AxisOpts(type_="category"),
        )
    )
    if (ifMean):
        html_path_name = "F:/csv2Html/" + time_range + '/' + jf + '-已平均/'
    else:
        html_path_name = "F:/csv2Html/" + time_range + '/' + jf + '-未平均/'

    path_exists_make(html_path_name)

    for kt in range(len(kt_list)):
        c_ = (Line()
        .add_xaxis(xaxis_data=data['sampleTime'])
        .add_yaxis(
            series_name=ktgl.columns[kt],
            y_axis=ktgl.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=ysj1.columns[kt],
            y_axis=ysj1.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=ysj2.columns[kt],
            y_axis=ysj2.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=lnfj1.columns[kt],
            y_axis=lnfj1.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=lnfj2.columns[kt],
            y_axis=lnfj2.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fj1.columns[kt],
            y_axis=fj1.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fj2.columns[kt],
            y_axis=fj2.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=sf1.columns[kt],
            y_axis=sf1.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=sfset.columns[kt],
            y_axis=sfset.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False
        )

        .add_yaxis(
            series_name=hf_avg.columns[kt],
            y_axis=hf_avg.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=hfset.columns[kt],
            y_axis=hfset.iloc[:, kt],
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False
        )
        )
        c.overlap(c_)
    g = (Grid(init_opts=opts.InitOpts(width='1400px', height='750px'))
         .add(c, grid_opts=opts.GridOpts(pos_top="25%"))
         .render(html_path_name + "机房" + jf + "-服务器-" + str(fwq[fwq_index]) + ".html"))

    print(g)


def path_exists_make(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)


def load_csvData(csv_file_name):
    '''
        以绝对路径 加载数据，并按照clean_data清理数据、新增间隔时间列

        :param csv_file_name: csv文件路径
        :return: 经过数据清洗的csv文件路径下的Dataframe数据
    '''
    # DATA_DIR = "data"
    # print(os.path.join(DATA_DIR, csv_file_name))
    data_df = pd.read_csv(csv_file_name, encoding='utf-8')
    # print(data_df.columns)
    if ('Unnamed: 0' in list(data_df)):
        data_df = data_df.drop('Unnamed: 0', axis=1)
    # data_df = clean_data(data_df)
    return data_df


def all_csvs():
    csv_file_name = r'F:\dataNeeded\preRunCSV\data_JF' + jf + '\\new\\'
    csv_data = pd.DataFrame()
    data_list = os.listdir(csv_file_name)
    for i in data_list[:]:
        try:
            csv_ = pd.read_csv(csv_file_name + i, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                csv_ = pd.read_csv(csv_file_name + i, encoding='latin1')
            except UnicodeDecodeError:
                csv_ = pd.read_csv(csv_file_name + i, encoding='cp1252')
        csv_data = pd.concat([csv_data, csv_], axis=0)

    # 只取html需要的列名，再删空
    ktNames = createKTName(ktNum)
    fwqpower_columns, ktpower_columns = createPowerName(fwq, ktNum)
    timeNames = ['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes', 'seconds', '室外环境温度']
    timeNktNames = timeNames + ktNames + fwqpower_columns
    cold_temps = pd.DataFrame()
    for fwq_index in range(len(fwq)):
        if jf == '203':
            # 203测点名
            clm1s = csv_data.columns[csv_data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][0])]
            clm2s = csv_data.columns[csv_data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][1])]
        if jf == '204':
            # 204测点名
            clm1s = csv_data.columns[csv_data.columns.str.contains('FT-' + jf + '-' + fwq[fwq_index][0])]
            clm2s = csv_data.columns[csv_data.columns.str.contains('FT-' + jf + '-' + fwq[fwq_index][1])]
        cold_temp1 = csv_data[clm1s]  # 服务器列 左
        cold_temp2 = csv_data[clm2s]  # 服务器列 左
        cold_temps = pd.concat([cold_temps, cold_temp1, cold_temp2], axis=1)

    csv_data = csv_data[timeNktNames]
    csv_data = pd.concat([csv_data, cold_temps], axis=1)

    csv_data = csv_data.dropna()
    csv_data.reset_index(drop=True, inplace=True)
    ifmeanName = '-未'
    if (ifMean):
        # # 处理为10min数据
        csv_1 = csv_data[csv_data.columns.drop(['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes', 'seconds'])]
        # 处理十分钟数据：隔20行取一行
        csv_1 = csv_1.rolling(20).mean()
        # 删除空值
        csv_data = pd.concat([csv_data[['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes']], csv_1], axis=1)
        csv_data = csv_data.dropna()
        csv_data.reset_index(drop=True, inplace=True)

        a = []
        for i in range(0, len(csv_data), 20):
            a.append(i)
        csv_data = csv_data.iloc[a]
        ifmeanName = '-已'

    time_range = data_list[0].split('_')[0][:8] + '-' + data_list[-1].split('_')[0][:8]
    temp_csv_path = 'F:/dataNeeded/preRunCSV/' + 'htmlData_JF' + jf + '/'
    path_exists_make(temp_csv_path)

    csv_data.to_csv(temp_csv_path + time_range + ifmeanName + '平均.csv', index=False, encoding='gbk')

    return csv_data, time_range


if __name__ == '__main__':
    all, time_range = all_csvs()
    all = all.sort_values('sampleTime', ascending=True)
    all = all.reset_index(drop=True)  # [6453:]
    all = all.drop_duplicates(['sampleTime'])
    all = all.reset_index(drop=True)
    # all=all.iloc[:,1:]
    print(all)

    for i in range(len(fwq)):
        fwq_plot(all, i, time_range)
        pass
