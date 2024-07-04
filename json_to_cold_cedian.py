# 导出202冷通道测点csv
import os
import json
import re
from collections import defaultdict
import time
import numpy as np
import pandas as pd

# chosen_JF='202'
row202 = [[12, 19, 20], [10, 11, 18], [8, 9, 17], [6, 7, 16], [4, 5, 15], [3, 14], [1, 2, 13]]
row203 = [[7, 13], [6, 11, 12], [4, 5, 10], [3, 9], [1, 2, 8]]
row204 = [[1, 13], [2,3,14], [4,5,15], [6,7,16],[8,9,17],[10,11,18],[12,19,20]]


def powerKT(jf: str):
    row_first = []
    if jf == '202':
        row = row202
    if jf == '203':
        row = row203
    if jf == '204':
        row = row204
    for i in range(len(row)):
        row_first.append(str(row[i][0]).zfill(2))
    return row_first


def JFfwq(JFname: str):
    if JFname == '202':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK', 'LM', 'NP']
        fwq_payload = ['N', 'P', 'L', 'M', 'J', 'K', 'H', 'G', 'E', 'F', 'C', 'D', 'A', 'B']
    elif JFname == '203':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK']
        fwq_payload = ['J', 'K', 'H', 'G', 'E', 'F', 'C', 'D', 'A', 'B']
    elif JFname == '204':
        fwq = ['AB', 'CD', 'EF', 'GH', 'JK', 'LM', 'NP']
        fwq_payload = ['N', 'P', 'L', 'M', 'J', 'K', 'H', 'G', 'E', 'F', 'C', 'D', 'A', 'B']

    return fwq, fwq_payload


def read_data(JF: str, data):
    # 写入冷通道温度，送风温度1，
    row_first = powerKT(JF)
    data_need = {}
    total_cold_temp = {}
    total_dc_payload0 = []
    total_dc_payload = []
    data_detail = data['data']
    # 遍历所有空调
    for i in range(len(data_detail)):
        device_name = data_detail[i]['deviceName']
        params = data_detail[i]['params']
        total_dc_payload0.clear()
        # 遍历单台空调数据包中的每个数据
        for conditioner_data in params:  # 取每列服务器对应的数据 包括冷通道，负载功率(空调device_name后两位为空调编号)
            if device_name[-2:] in row_first:
                # 解决新数据中温度pointName的1006001001和冷通道温度重合引起的问题，新加入判断pointName必须是冷通道温度
                if str(conditioner_data['standardId']) == '1006001001' and '冷通道温度' in str(conditioner_data['pointName']):
                    total_cold_temp[conditioner_data['corePointId']] = round(float(conditioner_data['originalValue']),
                                                                             2)
                # elif str(conditioner_data['standardId']) == '201035001' and str(conditioner_data['pointName']) == '有功功率':
                elif str(conditioner_data['standardId']) == '201035001':
                    total_dc_payload0.append(round(float(conditioner_data['originalValue']), 2))  # 有功功率

        if (len(total_dc_payload0) != 0):
            dc_payload_1 = sum(total_dc_payload0[:2])  # 有功功率
            dc_payload_2 = sum(total_dc_payload0[2:])  # 总有功功率
            total_dc_payload.append(round(dc_payload_2, 2))
            total_dc_payload.append(round(dc_payload_1, 2))

    cold_cedian_data = cold_cedian('cold', total_cold_temp)
    payload_dataframe = {}
    fwq, fwq_payload = JFfwq(JF)
    for payload in range(len(total_dc_payload)):
        payload_dataframe['服务器' + fwq_payload[payload] + '功率'] = total_dc_payload[payload]
    payload_dataframe = pd.DataFrame([payload_dataframe])
    return data_need, cold_cedian_data, payload_dataframe


def cold_cedian(wd_type, origin_data):
    cedian_csv = pd.read_csv(wd_type + "_temp_cedian.csv")
    # 转换为二维list
    origin_data = pd.DataFrame(list(origin_data.items()), columns=['CorePointId', 'Value'])
    new_data = pd.merge(cedian_csv, origin_data, how="right", on=["CorePointId"])

    new_data = new_data[['EquipmentName', 'Value']]
    # 删除空值，重置索引
    new_data.dropna(inplace=True)
    new_data.reset_index(drop=True, inplace=True)
    return new_data


def write_csv(JF: str, data):
    data_need, cold_cedian_data, payload_dataframe = read_data(JF, data)
    data_need = pd.DataFrame([data_need])
    cold_cedian_data = cold_cedian_data.T  # 转置后，将第一行变为列名
    array = np.array(cold_cedian_data)  # 将df转换为list对象
    list = array.tolist()  # 将array转换为list
    list = list[0]  # 获取第一行的数据
    cold_cedian_data.columns = list  # 将列名改为指定列表中的元素
    cold_cedian_data.drop(['EquipmentName'], inplace=True)  # 删除df的第一行多余的数据
    cold_cedian_data.reset_index(drop=True, inplace=True)
    single_line = pd.concat([cold_cedian_data, data_need, payload_dataframe], axis=1)
    single_line = single_line.T
    return single_line
