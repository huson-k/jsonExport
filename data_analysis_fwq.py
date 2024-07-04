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
jf = '203'
# fwq = ['AB', 'CD', 'EF', 'GH', 'JK', 'LM', 'NP']  # AB-0,CD-1,EF-2,GH-3,JK-4,LM-5,NP-6
fwq = ['AB', 'CD', 'EF', 'GH', 'JK']  # AB-0,CD-1,EF-2,GH-3,JK-4,LM-5,NP-6

# KT_toFwq_list_1 = [[12], [10, 11], [8, 9, ], [6, 7], [4, 5],
#                    [3], [1, 2]]
# KT_toFwq_list_2 = [[19, 20], [18, ], [17, ], [16, ], [15, ],
#                    [14, ], [13, ]]

KT_toFwq_list_1 = [[13], [12, 11], [10], [9], [8]]
KT_toFwq_list_2 = [[7], [6], [5, 4], [3], [2, 1]]

# 冷通道组上中下分区标号
up_site_nums = [1, 7]
mid_site_nums = [8, 12]
dw_site_nums = [13, 19]


def site_names(up_site_nums: list, mid_site_nums: list, dw_site_nums: list):
    up_sites = np.arange(up_site_nums[0], mid_site_nums[0])
    mid_sites = np.arange(mid_site_nums[0], dw_site_nums[0])
    dw_sites = np.arange(dw_site_nums[0], dw_site_nums[1]+1)
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
    # 压缩机容量，风机转速，送风温度，送风设定，回风温度，回风设定
    kt_list = KT_toFwq_list_1[fwq_index] + KT_toFwq_list_2[fwq_index]
    # kt_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    # 添加空调相关数据
    ysj1 = pd.DataFrame()
    ysj2 = pd.DataFrame()
    fj1 = pd.DataFrame()
    fj2 = pd.DataFrame()
    sf1 = pd.DataFrame()
    sfset = pd.DataFrame()
    hf_avg = pd.DataFrame()
    hfset = pd.DataFrame()
    for i in kt_list:
        ysj1 = pd.concat([ysj1, data['KT-' + str(i) + '-压缩机1容量']], axis=1)
        ysj2 = pd.concat([ysj2, data['KT-' + str(i) + '-压缩机2容量']], axis=1)
        fj1 = pd.concat([fj1, data['KT-' + str(i) + '-风机1转速']], axis=1)
        fj2 = pd.concat([fj2, data['KT-' + str(i) + '-风机2转速']], axis=1)
        sf1 = pd.concat([sf1, data['KT-' + str(i) + '-送风温度1']], axis=1)
        sfset = pd.concat([sfset, data['KT-' + str(i) + '-送风温度设定']], axis=1)
        # 回风温度，取全部平均
        hfwd_avg = []
        for j in range(len(data)):
            hfwd = []
            for hf_num in range(1, 5):
                if (data['KT-' + str(i) + '-回风温度' + str(hf_num)][j] > 0):
                    hfwd.append(data['KT-' + str(i) + '-回风温度' + str(hf_num)][j])
            hfwd_avg.append(np.mean(hfwd))
        hf_avg = pd.concat([pd.DataFrame(hf_avg), pd.DataFrame(hfwd_avg, columns=['KT-' + str(i) + '-回风温度'])],
                           axis=1)
        hfset = pd.concat([hfset, data['KT-' + str(i) + '-回风温度设定']], axis=1)

    sf1 = round(sf1, 2)
    sf_avg = round(sf1.apply(lambda x: x.mean(), axis=1), 2)
    env = data['室外环境温度']
    # 总有功：N；有功P
    # 总有功：H；有功：G

    # 冷通道温度分区域取：
    cold_temp1 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][0])]]  # 服务器列 左
    cold_temp2 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][1])]]  # 服务器列 右
    cold_temps = pd.concat([cold_temp1, cold_temp2], axis=1)
    up_site, mid_site, dw_site = site_names(up_site_nums, mid_site_nums, dw_site_nums)
    up_site = [col for col in cold_temps.columns if col[7:9] in up_site]
    mid_site = [col for col in cold_temps.columns if col[7:9] in mid_site]
    dw_site = [col for col in cold_temps.columns if col[7:9] in dw_site]
    cold_temps_up = cold_temps[up_site]
    cold_temps_mid = cold_temps[mid_site]
    cold_temps_dw = cold_temps[dw_site]
    cold_temps_up_min = round(cold_temps_up.apply(lambda x: x.min(), axis=1), 2)  # 服务器组上部分 最小
    cold_temps_mid_min = round(cold_temps_mid.apply(lambda x: x.min(), axis=1), 2)  # 服务器组中部分 最小
    cold_temps_dw_min = round(cold_temps_dw.apply(lambda x: x.min(), axis=1), 2)  # 服务器组下部分 最小
    cold_temps_up_avg = round(cold_temps_up.apply(lambda x: x.mean(), axis=1), 2)  # 服务器组上部分 平均
    cold_temps_mid_avg = round(cold_temps_mid.apply(lambda x: x.mean(), axis=1), 2)  # 服务器组中部分 平均
    cold_temps_dw_avg = round(cold_temps_dw.apply(lambda x: x.mean(), axis=1), 2)  # 服务器组下部分 平均
    cold_temps_up_max = round(cold_temps_up.apply(lambda x: x.max(), axis=1), 2)  # 服务器组上部分 最大
    cold_temps_mid_max = round(cold_temps_mid.apply(lambda x: x.max(), axis=1), 2)  # 服务器组中部分 最大
    cold_temps_dw_max = round(cold_temps_dw.apply(lambda x: x.max(), axis=1), 2) # 服务器组下部分 最大


    cold_temp1 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][0])]]  # 服务器列 左
    cold_avg1 = round(cold_temp1.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 左 平均温度
    # cold_avg1_up = cold_temp1[cold_temp1.columns[cold_temp1.columns.str.contains('上')]]  # 服务器列 左 上
    # cold_avg1_up_top = cold_avg1_up.iloc[:, :int(cold_avg1_up.shape[1] / 2)]  # 服务器列 左 上 上半部分
    # cold_avg1_up_top_avg = round(cold_avg1_up_top.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 左 上 上半部分 平均
    # cold_avg1_up_btm = cold_avg1_up.iloc[:, int(cold_avg1_up.shape[1] / 2):]  # 服务器列 左 上 下半部分
    # cold_avg1_up_btm_avg = round(cold_avg1_up_btm.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 左 上 下半部分 平均
    # cold_avg1_down = cold_temp1[cold_temp1.columns[cold_temp1.columns.str.contains('下')]]  # 服务器列 左 下
    # cold_avg1_down_top = cold_avg1_down.iloc[:, :int(cold_avg1_down.shape[1] / 2)]  # 服务器列 左 下 上半部分
    # cold_avg1_down_top_avg = round(cold_avg1_down_top.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 左 下 上半部分 平均
    # cold_avg1_down_btm = cold_avg1_down.iloc[:, int(cold_avg1_down.shape[1] / 2):]  # 服务器列 左 下 下半部分
    # cold_avg1_down_btm_avg = round(cold_avg1_down_btm.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 左 下 下半部分 平均

    cold_temp2 = data[data.columns[data.columns.str.contains('FT' + jf + '-' + fwq[fwq_index][1])]]  # 服务器列 右
    cold_avg2 = round(cold_temp2.apply(lambda x: x.mean(), axis=1))  # 服务器列 右 平均温度
    # cold_avg2_up = cold_temp2[cold_temp2.columns[cold_temp2.columns.str.contains('上')]]  # 服务器列 右 上
    # cold_avg2_up_top = cold_avg2_up.iloc[:, :int(cold_avg2_up.shape[1] / 2)]  # 服务器列 右 上 上半部分
    # cold_avg2_up_top_avg = round(cold_avg2_up_top.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 右 上 上半部分 平均
    # cold_avg2_up_btm = cold_avg2_up.iloc[:, int(cold_avg2_up.shape[1] / 2):]  # 服务器列 右 上 下半部分
    # cold_avg2_up_btm_avg = round(cold_avg2_up_btm.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 右 上 下半部分 平均
    # cold_avg2_down = cold_temp2[cold_temp2.columns[cold_temp2.columns.str.contains('下')]]  # 服务器列 右 下
    # cold_avg2_down_top = cold_avg2_down.iloc[:, :int(cold_avg2_down.shape[1] / 2)]  # 服务器列 右 下 上半部分
    # cold_avg2_down_top_avg = round(cold_avg2_down_top.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 右 下 上半部分 平均
    # cold_avg2_down_btm = cold_avg2_down.iloc[:, int(cold_avg2_down.shape[1] / 2):]  # 服务器列 右 下 下半部分
    # cold_avg2_down_btm_avg = round(cold_avg2_down_btm.apply(lambda x: x.mean(), axis=1), 2)  # 服务器列 右 下 下半部分 平均

    cold_avg = round((cold_avg1 + cold_avg2) / 2, 4)  # 该服务器组整体平均温度
    diff_avg = cold_avg - sf_avg

    cold_max1, cold_max1_location, cold_second1, cold_second1_location, cold_third1, cold_third1_location = cold_max_second(
        cold_temp1)
    cold_max2, cold_max2_location, cold_second2, cold_second2_location, cold_third2, cold_third2_location = cold_max_second(
        cold_temp2)

    cedian_wd1 = data[data.columns[data.columns.str.contains('FT'+jf+'-' + fwq[fwq_index][0])]]
    cedian_wd2 = data[data.columns[data.columns.str.contains('FT'+jf+'-' + fwq[fwq_index][1])]]
    cedian_wd = pd.concat([cedian_wd1, cedian_wd2], axis=1)
    cedian_wd_avg = round(cedian_wd.apply(lambda x: x.mean(), axis=1), 2)
    cedian_wd = round(cedian_wd.apply(lambda x: x - cedian_wd_avg, axis=0), 2)
    cedian_wd_bodong_sigma = round(cedian_wd.apply(lambda x: x.std(), axis=1), 2)

    diff_max_avg1 = round(max(cold_max1 - cold_avg1), 2)
    diff_max_avg2 = round(max(cold_max2 - cold_avg2), 4)
    # 测点波动标准差

    title = time_range + "\n服务器" + fwq[fwq_index][0] + "冷通道max与avg最大差值为" + str(diff_max_avg1) + \
            "，差值均值为:" + str(round(np.mean(cold_max1 - cold_avg1), 4)) + \
            "，差值标准差为:" + str(round(np.std(cold_max1 - cold_avg1), 4)) + '\n' + \
            "服务器" + fwq[fwq_index][1] + "冷通道max与avg最大差值为" + str(diff_max_avg2) + \
            "，差值均值为:" + str(round(np.mean(cold_max2 - cold_avg2), 4)) + \
            "，差值标准差为:" + str(round(np.std(cold_max2 - cold_avg2), 4))
    print(title)

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
            is_selected=False
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
        # .add_yaxis(
        #     series_name=fwq[fwq_index][0] + '冷通道温度次大值',
        #     # stack="总量",
        #     y_axis=cold_second1,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][1] + '冷通道温度次大值',
        #     # stack="总量",
        #     y_axis=cold_second2,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][0] + '冷通道温度第三大值',
        #     # stack="总量",
        #     y_axis=cold_third1,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][1] + '冷通道温度第三大值',
        #     # stack="总量",
        #     y_axis=cold_third2,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
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
        # .add_yaxis(
        #     series_name=fwq[fwq_index][0] + '冷通道温度次大值测点位置',
        #     # stack="总量",
        #     y_axis=cold_second1_location,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][1] + '冷通道温度次大值测点位置',
        #     y_axis=cold_second2_location,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][0] + '冷通道温度第三大值测点位置',
        #     # stack="总量",
        #     y_axis=cold_third1_location,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        # .add_yaxis(
        #     series_name=fwq[fwq_index][1] + '冷通道温度第三大值测点位置',
        #     y_axis=cold_third2_location,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
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
        # .add_yaxis(
        #     series_name=fwq[fwq_index] + '冷通道测点偏离平均值标准差',
        #     y_axis=cedian_wd_bodong_sigma,
        #     label_opts=opts.LabelOpts(is_show=False),
        #     is_selected=False
        # )
        .add_yaxis(
            series_name='送风平均温度',
            y_axis=sf_avg,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组上部分(1-7)min',
            y_axis=cold_temps_up_min,
            label_opts=opts.LabelOpts(is_show=False),
            is_selected=False,
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组中部分(8-12)min',
            y_axis=cold_temps_mid_min,
            is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组下部分(13-19)min',
            y_axis=cold_temps_dw_min,
            is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组上部分(1-7)avg',
            y_axis=cold_temps_up_avg,
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False,
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组中部分(8-12)avg',
            y_axis=cold_temps_mid_avg,
            # is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组下部分(13-19)avg',
            y_axis=cold_temps_dw_avg,
            # is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组上部分(1-7)max',
            y_axis=cold_temps_up_max,
            label_opts=opts.LabelOpts(is_show=False),
            # is_selected=False,
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组中部分(8-12)max',
            y_axis=cold_temps_mid_max,
            # is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name=fwq[fwq_index] + '冷通道组下部分(13-19)max',
            y_axis=cold_temps_dw_max,
            # is_selected=False,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name='冷通道组平均温度-送风平均温度',
            y_axis=diff_avg,
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
    html_path_name = "F:/data_analysis_html/" + time_range + '/'
    path_exists_make(html_path_name)

    for kt in range(len(kt_list)):
        c_ = (Line()
        .add_xaxis(xaxis_data=data['sampleTime'])
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
            # is_selected=False
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
            is_selected=False
        )
        )
        c.overlap(c_)
    g = (Grid(init_opts=opts.InitOpts(width='1400px', height='750px'))
         .add(c, grid_opts=opts.GridOpts(pos_top="25%"))
         .render(html_path_name + "服务器-" + str(fwq[fwq_index]) + ".html"))

    print(g)

    # sf_avg = pd.DataFrame(sf_avg).rename(columns={0: '送风温度平均'})
    # cold_avg1_up_top_avg = pd.DataFrame(cold_avg1_up_top_avg).rename(
    #     columns={0: fwq[fwq_index][0] + '列上测点 上半部分平均'})
    # cold_avg1_up_btm_avg = pd.DataFrame(cold_avg1_up_btm_avg).rename(
    #     columns={0: fwq[fwq_index][0] + '列上测点 下半部分平均'})
    # cold_avg1_down_top_avg = pd.DataFrame(cold_avg1_down_top_avg).rename(
    #     columns={0: fwq[fwq_index][0] + '列下测点 上半部分平均'})
    # cold_avg1_down_btm_avg = pd.DataFrame(cold_avg1_down_btm_avg).rename(
    #     columns={0: fwq[fwq_index][0] + '列下测点 下半部分平均'})
    # cold_avg2_up_top_avg = pd.DataFrame(cold_avg2_up_top_avg).rename(
    #     columns={0: fwq[fwq_index][1] + '列上测点 上半部分平均'})
    # cold_avg2_up_btm_avg = pd.DataFrame(cold_avg2_up_btm_avg).rename(
    #     columns={0: fwq[fwq_index][1] + '列上测点 下半部分平均'})
    # cold_avg2_down_top_avg = pd.DataFrame(cold_avg2_down_top_avg).rename(
    #     columns={0: fwq[fwq_index][1] + '列下测点 上半部分平均'})
    # cold_avg2_down_btm_avg = pd.DataFrame(cold_avg2_down_btm_avg).rename(
    #     columns={0: fwq[fwq_index][1] + '列下测点 下半部分平均'})
    #
    # sfNltdTemp = pd.concat(
    #     [data['sampleTime'], sf1, sf_avg, cold_avg1_up_top_avg, cold_avg1_up_btm_avg, cold_avg1_down_top_avg,
    #      cold_avg1_down_btm_avg, cold_avg2_up_top_avg, cold_avg2_up_btm_avg, cold_avg2_down_top_avg,
    #      cold_avg2_down_btm_avg], axis=1)
    # sfNltdTempNset = pd.concat([sfNltdTemp, sfset], axis=1)
    # csv_path_name = 'F:/dataNeeded/sfNltdTemp/' + time_range
    # path_exists_make(csv_path_name)
    # sfNltdTemp.to_csv(csv_path_name + '/' + fwq[fwq_index] + '.csv', encoding='utf_8_sig')
    # sfNltdTempNset.to_csv(csv_path_name + '/SFset_' + fwq[fwq_index] + '.csv', encoding='utf_8_sig')


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
    DATA_DIR = "data"
    # print(os.path.join(DATA_DIR, csv_file_name))
    data_df = pd.read_csv(os.path.join(DATA_DIR, csv_file_name))
    # print(data_df.columns)
    if ('Unnamed: 0' in list(data_df)):
        data_df = data_df.drop('Unnamed: 0', axis=1)
    # data_df = clean_data(data_df)
    return data_df


def all_csvs():
    csv_file_name = 'F:/dataNeeded/csvData4Html/'
    csv_data = []

    data_list = os.listdir(csv_file_name)
    for i in data_list[:]:
        csv_ = load_csvData(csv_file_name + i)
        if (len(csv_data)):
            csv_data = pd.concat([csv_data, csv_], axis=0)
        else:
            csv_data = csv_
    csv_data.reset_index(drop=True, inplace=True)

    print(csv_data.filter(regex="min"))
    # csv_data=csv_data
    # print(data_all.filter(regex="min"))
    data_all = csv_data.copy()
    # data_all = data_all.loc[
    #     data_all['KT-1-冷通道温度的min'] * data_all['KT-2-冷通道温度的min'] * data_all['KT-3-冷通道温度的min'] * data_all[
    #         'KT-4-冷通道温度的min'] * data_all['KT-5-冷通道温度的min'] * data_all['KT-6-冷通道温度的min'] * data_all['KT-7-冷通道温度的min'] *
    #     data_all['KT-8-冷通道温度的min'] * data_all['KT-9-冷通道温度的min'] * data_all['KT-10-冷通道温度的min'] * data_all[
    #         'KT-11-冷通道温度的min'] * data_all['KT-12-冷通道温度的min'] * data_all['KT-13-冷通道温度的min'] * data_all[
    #         'KT-14-冷通道温度的min'] * data_all['KT-15-冷通道温度的min'] * data_all['KT-1-冷通道温度的min'] * data_all[
    #         'KT-16-冷通道温度的min'] * data_all['KT-17-冷通道温度的min'] * data_all['KT-18-冷通道温度的min'] * data_all[
    #         'KT-19-冷通道温度的min'] * data_all['KT-20-冷通道温度的min'] != 0]
    data_all = data_all.reset_index(drop=True)
    # print(data_all.filter(regex="min"))
    csv_data = data_all
    # time.sleep(10000)
    # 处理为10min数据
    # csv_1 = csv_data[csv_data.columns.drop(['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes'])]
    #
    # csv_1 = csv_1.rolling(20).mean()
    # # 删除空值
    # csv_data = pd.concat([csv_data[['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes']], csv_1], axis=1)
    # csv_data = csv_data.dropna()
    # csv_data.reset_index(drop=True, inplace=True)
    # # #隔20行取一行
    # a = []
    # for i in range(0, len(csv_data), 20):
    #     a.append(i)
    # csv_data = csv_data.iloc[a]
    time_range = data_list[0].split('_')[0][:8] + '-' + data_list[-1].split('_')[0][:8]

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
