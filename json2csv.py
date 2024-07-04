import json
import os
import pandas as pd
import numpy as np
from json_to_cold_cedian import *


class dealFile():
    '''
        类dealfile：处理JSON文件
    '''

    def __init__(self, input_path: str, output_path: str, KT_num: int, chosen_JF: str):
        '''
            初始化 类dealFile

            :param input_path: 需要处理某机房(chosen_JF)JSON文件所在路径
            :param output_path: 生成的CSV文件路径
            :param KT_num: chosen_JF所选机房 空调数量
            :param chosen_JF: 所选需要导出成CSV的机房名
        '''
        self.input_path = input_path
        self.output_path = output_path
        self.KT_num = KT_num
        self.chosen_JF = chosen_JF
        self.count = 0

        # JSON原始数据映射 所需变量文件-inference.json 路径
        self.infe = './new_inference.json'

    def sortJsonList(self, filepath):  # 对读入文件夹内所有的JSON按照时间排序
        '''
            :param filepath: JSON文件名字列表
            :return: 按时间排序的 JSON文件名字列表
        '''
        filesList = os.listdir(filepath)
        filesList.sort(key=lambda fn: os.path.getmtime(filepath + '/' + fn))
        return filesList

    def readJson(self, file_path):
        '''
            读入json load出并返回df表；JSON空、非JSON 返回False

            :param file_path: 需要 读取JSON文件 的路径
            :return: JSON文件内容
        '''
        try:
            # 根据输入JSON文件路径load得到JSON文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        # try 时候
        except json.decoder.JSONDecodeError:
            print(file_path, " The Json Is Empty!")
            return False
        except UnicodeDecodeError:
            print(file_path, ' This Is Not A Json')
            return False

    def readCols(self):
        '''
            根据 inference.json 读取需要制作成CSV的列名，并返回列名列表

            :param JF_name: 选取的机房名(202/203/205 可选)
            :return: 列名list
        '''
        index = self.infe
        index0 = self.readJson(index)
        cols = ['sampleTime', 'year', 'mon', 'day', 'hours', 'minutes', 'seconds']  # 时间7列

        '''
            inference文件 提取 kt_params_multi/environment_params/kt_params_single/kt_all_yggl 4个大变量
        '''
        # inference JSON文件  空调冷热通道温湿度 kt_params_multi
        kt_params_multi = list(map(int, index0["kt_params_multi_" + self.chosen_JF].keys()))
        # inference JSON文件 environment_params_(202/203...
        environment_params = list(map(int, index0["environment_params_" + self.chosen_JF].keys()))
        # inference JSON文件  空调冷热通道温湿度 kt_params_multi
        kt_params_single = list(map(int, index0["kt_params_single_" + self.chosen_JF].keys()))
        # inference JSON文件 空调总有功功率（由于stdID总有功功率和有功功率冲突，所以单列一项）
        if self.chosen_JF != '201':  # 只有 201机房 没有总有功功率
            kt_all_yggl = list(map(int, index0["kt_all_yggl"].keys()))

        '''
            4个大变量 分别迭代生成CSV列名，并extend到cols内
        '''
        # 循环迭代产生 JF_name机房内 每台空调 kt_params_multi 列名 avg/max/min
        for param in kt_params_multi:
            for i in range(self.KT_num):
                avg = 'KT-' + str(i + 1) + '-' + index0["kt_params_multi_" + self.chosen_JF][str(param)] + '的avg'
                max = 'KT-' + str(i + 1) + '-' + index0["kt_params_multi_" + self.chosen_JF][str(param)] + '的max'
                min = 'KT-' + str(i + 1) + '-' + index0["kt_params_multi_" + self.chosen_JF][str(param)] + '的min'
                col = [avg, max, min]
                cols.extend(col)
        # print(self.chosen_JF + "JF kt_params_multi len(cols):", len(cols))
        # print(self.chosen_JF + "JF kt_params_multi cols:\n", cols)

        # 循环迭代产生 JF_name机房内 每台空调 kt_params_single 列名
        for param in kt_params_single:
            for i in range(self.KT_num):
                col = ['KT-' + str(i + 1) + '-' + index0["kt_params_single_" + self.chosen_JF][str(param)]]
                cols.extend(col)
        # print(self.chosen_JF + "JF kt_params_multi + kt_params_single len(cols):", len(cols))
        # print(self.chosen_JF + "JF kt_params_multi + kt_params_single cols:\n", cols)

        # 循环迭代产生 JF_name机房内 environment_params 列名
        for param in environment_params:
            col = [index0["environment_params_" + self.chosen_JF][str(param)]]
            cols.extend(col)
        print(self.chosen_JF + "JF kt_params_multi + kt_params_single + environment_params len(cols):", len(cols))
        # print(self.chosen_JF + "JF kt_params_multi + kt_params_single + environment_params cols:\n", cols)

        # 目前201机房无总有功功率
        if self.chosen_JF != '201':
            # 循环迭代产生 JF_name机房内 每台空调 kt_all_yggl 列名
            for param in kt_all_yggl:
                for i in range(self.KT_num):
                    col = ['KT-' + str(i + 1) + '-' + index0["kt_all_yggl"][str(param)]]
                    cols.extend(col)
            # print(
            #     self.chosen_JF + "JF kt_params_multi + kt_params_single + environment_params + kt_all_yggl len(cols):",
            #     len(cols))
            # print(self.chosen_JF + "JF kt_params_multi + kt_params_single + environment_params + kt_all_yggl cols:\n",
            #       cols)

        '''
            4个大变量extend到cols成功，返回 cols列表
        '''
        print(self.chosen_JF + "JF export csv len of cols:", len(cols))
        return cols

    def json_time(self, kt_time):
        '''
            :param kt_time: 整个JSON文件所有测点时间
            :return: 整个JSON文件出现频率最高的测点时间认为是该JSON采集时间
        '''
        kt_time = [i for i in kt_time if i != '1970-01-01 00:00:00']  # 筛选异常时间1970-01-01 00:00:00
        try:
            time = max(set(kt_time), key=kt_time.count)  # 选取该JSON文件中 测点数据时间最多的一项 作为 该JSON文件的时间

            print("\n" + str(self.count) + " ------------- JF" + self.chosen_JF, time, 'is writing', "-------------")

            # 2022/11/14 时间优化为 原始JSON数据 获取数量最多的
            year_month_day, hour_minute_second = time.split(' ')  # 分割年月日、时秒分数据
            year, month, day = year_month_day.split('-')  # 分割年、月、日数据
            hour, minute, second = hour_minute_second.split(':')  # 分割时、秒、分数据
            time_temp = [time, year, month, day, hour, minute, second]
            return time_temp
        except:
            return False

    def writeData(self, data0, index0):
        '''
            将数据按照 格式写入并合并

            :param data0: JSON原始数据
            :param index0: 需要提取成CSV的列名
            :return: 该JSON文件制作成的一行CSV数据(sum_out)
        '''
        sum_out = []
        clos = []
        col_need = ['standardId', 'originalValue', 'pointName']  # JSON文件 需要每台空调 测点数据名
        col_time = ['sampleTime']  # JSON文件 需要每台空调 测点数据时间
        kt_sum = []  # JSON文件的 所有空调 测点col_need数据
        kt_time = []  # JSON文件的 所有空调 测点数据col_time时间

        '''
            循环迭代从JSON文件中找到 所选机房每台空调 所需列字段col_need 测点数据
        '''
        for arr in index0["kt_arr_" + self.chosen_JF]:
            # 取到 JSON数据data中 第arr台空调 params测点 col_need数据（'standardId', 'originalValue', 'pointName'）
            temp_params_kt = [pd.DataFrame(data0['data'][arr]['params'], columns=col_need)]
            # 取到 JSON数据data中 第arr台空调 params测点 col_time数据（sampleTime）
            temp_time_kt = pd.DataFrame(data0['data'][arr]['params'], columns=col_time).values.tolist()
            kt_time.extend(sum(temp_time_kt, []))
            kt_sum.append(temp_params_kt)
        time_temp = self.json_time(kt_time)  # 计算该JSON时间
        if time_temp:  # 时间无误
            sum_out.extend(time_temp)  # [time, year, month, day, hour, minute, second]
            clos.extend(['sampleTime', 'year', 'mon', 'day', 'hour', 'minute', 'second'])
        else:  # 时间有错直接放弃这条json
            return sum_out

        '''
            inference文件 提取 kt_params_multi/environment_params_(202/203/205)/kt_params_single/kt_all_yggl 4个大变量
        '''
        kt_params_multi = list(map(int, index0["kt_params_multi_" + self.chosen_JF].keys()))
        environment_params = list(map(int, index0["environment_params_" + self.chosen_JF].keys()))
        kt_params_single = list(map(int, index0["kt_params_single_" + self.chosen_JF].keys()))
        if self.chosen_JF != '201':
            kt_all_yggl = list(map(int, index0["kt_all_yggl"].keys()))

        '''
            kt_params_multi 空调的服务器参数
        '''
        for param in kt_params_multi:
            value = []  # 该机房所有空调的id值
            # 取每台空调multi参数，分别取参数max、min、avg
            for kt in kt_sum:  # 遍历每个json，找到param对应stdid数据
                kt = kt[0]
                sid = kt.iloc[:, 0]
                # 2022.11.14,若是有功功率（一台空调绑定所在组服务器2台服务器），求sum和 返回；其余参数mean平均
                if len(kt[(sid == param)]):
                    temp = kt[(sid == param)]['originalValue'].astype(float)
                    if(param=='1006001001'):
                        temp = temp[temp > 0]
                        temp = temp[temp < 40]
                    if (len(temp) == 0):
                        a = [0, 0, 0]
                        # print('冷通道温度异常 平均/最大/最小温度 都定义为0', a)
                    else:
                        a = [round(temp.mean(), 1), temp.max(), temp.min()]
                        # print('冷通道平均/最大/最小温度', a)
                    value.extend(a)

            sum_out.extend(value)
            # 验证ID
            value0 = pd.DataFrame(value)
            if int(value0.isnull().sum()) == 60:
                # 检查ID
                print(param, index0["kt_params_multi"][str(param)], 'changed,')
                try:
                    # 查找ID
                    point_name = kt_sum[0][(kt_sum[0].pointName[0:3] == index0["kt_params_multi"][str(param)][0:3])]
                    newparam = point_name['standardId'].values[0]
                    print('Now its ID is:', newparam)

                    ##########################################################################
                    print(str(param) + index0["kt_params_multi"][str(param)] + 'changed,')
                    print('Now its ID is:' + str(newparam))

                    # 更新ID
                    for kt in kt_sum:
                        temp = kt[(kt.standardId // 10 == int(newparam) // 10) & (kt.originalValue.astype(float) > 0)][
                            'originalValue'].astype(float)
                        a = [round(temp.mean(), 1), temp.max(), temp.min()]
                        value.extend(a)
                except IndexError:  # 找不到ID则告诉一声
                    print('Do Not Find This New StandardId\n')

        '''
            kt_params_single 空调单参数（特殊处理 stdID冲突 且 多数据 "有功功率"：求和sum）
        '''
        for param in kt_params_single:
            value = []
            for kt in kt_sum:  # 遍历每个json，找到param对应stdid数据
                kt = kt[0]
                sid = kt.iloc[:, 0]
                pname = kt.iloc[:, 2]
                # 2022.11.14,若是有功功率（一台空调绑定所在组服务器2台服务器），求sum和 返回；其余参数mean平均
                index_tOf = (sid == param)
                pname_i = pname[index_tOf]
                if len(kt[index_tOf]):  # 有param参数
                    temp = kt[index_tOf]['originalValue'].astype(float)
                    index_yggl = (pname_i.values == '有功功率')
                    if len(temp[index_yggl]):
                        temp = temp[index_yggl].astype(float)
                        a = [round(temp.sum(), 1)]  # 一台空调2个有功功率数据，加和
                    else:
                        a = [round(temp.mean(), 1)]  # single其余参数，为保持结构一致求平均（实质上对一个求平均，得到的还是这个值）
                else:
                    a = [0]
                value.extend(a)

            sum_out.extend(value)
            # 验证ID
            value0 = pd.DataFrame(value)
            ##没找到该value值
            if int(value0.isnull().sum()) == 20:
                try:
                    print(param, index0["kt_params_single"][str(param)], 'changed,')

                    point_name = kt_sum[0][(kt_sum[0].pointName == index0["kt_params_single"][str(param)])]
                    newparam = point_name['standardId'].values[0]

                    print('Now its ID is:', newparam)
                    print(str(param) + index0["kt_params_single"][str(param)] + 'changed,')
                    print('Now its ID is:' + str(newparam))  # 记录

                    value = [round(kt[(kt.standardId == int(newparam))]['originalValue'].astype(float).mean(), 1) for kt
                             in kt_sum]  # 修改ID再查找

                except IndexError:  # 找不到ID则告诉一声
                    print('Do Not Find This New StandardId\n')

        '''
            environment_params 环境参数
        '''
        # 2022.11.14.环境参数取法：所在机房全部空调平均
        for param in environment_params:
            value = []  # 13台空调的id值
            for kt in kt_sum:  # 遍历每个json，找到param对应stdid数据
                kt = kt[0]  # 转换kt格式从list为DataFrame
                sid = kt.standardId  # 取到kt
                index_tOf = (sid == param)
                temp = kt[index_tOf]['originalValue'].astype(float)
                value.append(temp.mean())
            avg_value = np.mean(value)
            sum_out.append(round(avg_value, 1))  # 获得该机房所有空调的环境参数均值

            # 验证ID
            value0 = pd.DataFrame(value)
            if int(value0.isnull().sum()) == 1 & len(value0) == 1:
                print(param, index0["environment_params_" + self.chosen_JF][str(param)], 'changed,')
                point_name = kt[(kt.pointName == index0["environment_params_" + self.chosen_JF][str(param)])]

                try:
                    # print(point_name)
                    newparam = point_name['standardId'].values[0]
                    print('Now its ID is:', newparam)

                    #################################################
                    print(str(param) + index0["environment_params_" + self.chosen_JF][str(param)] + 'changed,')
                    print('Now its ID is:' + str(newparam))
                    #
                    if newparam == param:
                        print('Find just mssing the value\n')
                    # 更新ID
                    value = [round(kt[(kt.standardId == int(param)) & (kt.originalValue.astype(float) > 0)][
                                       'originalValue'].astype(float).mean(), 1)]
                except IndexError:
                    print('Do Not Find This New StandardId\n')

        '''
            kt_all_yggl 总有功功率
        '''
        if self.chosen_JF != '201':
            for param in kt_all_yggl:
                value = []
                for kt in kt_sum:  # 遍历每个json，找到param对应stdid数据
                    kt = kt[0]
                    sid = kt.iloc[:, 0]
                    pname = kt.iloc[:, 2]
                    # 2022.11.14,若是有功功率（一台空调绑定所在组服务器2台服务器），求sum和 返回；其余参数mean平均
                    index_tOf = (sid == param)
                    pname_i = pname[index_tOf]
                    if len(kt[index_tOf]):  # 有param参数
                        temp = kt[index_tOf]['originalValue'].astype(float)
                        index_yggl = (pname_i.values == '总有功功率')
                        if len(temp[index_yggl]):
                            temp = temp[index_yggl].astype(float)
                            a = [round(temp.sum(), 1)]  # 一台空调2个有功功率数据，加和
                        else:
                            a = [0]  # single其余参数，为保持结构一致求平均（实质上对一个求平均，得到的还是这个值）
                    else:
                        a = [0]
                    value.extend(a)
                sum_out.extend(value)

        return pd.DataFrame(sum_out)

    def readData(self, json_file, indexs):
        one_json = pd.DataFrame()
        cedian_one_json = pd.DataFrame()
        data0 = self.readJson(json_file)
        try:
            if data0:  # json 正常读入
                json_JF = data0['aiGroup']['aiGroupName']
                if json_JF == self.chosen_JF:
                    index0 = self.readJson(indexs)
                    if data0 != False:
                        one_json = self.writeData(data0, index0)
                        # one_json = pd.DataFrame(one_json)
                        # if (self.chosen_JF == '202'): // 导出所有机房冷通道各个测点温度
                        cedian_one_json = write_csv(self.chosen_JF, data0)

                    return one_json, cedian_one_json
                else:
                    print("It's JF" + json_JF + " JSON, not chosen JF" + self.chosen_JF + ".")
                    return one_json, cedian_one_json
            else:  # json文件异常读入
                return one_json, cedian_one_json
        except:
            return pd.DataFrame(), pd.DataFrame()

    def Writefile(self, csv_name):
        if not os.path.isdir(self.input_path):
            print('input path not exist!')

        out_csvNeed = pd.DataFrame()
        fileList = os.listdir(self.input_path)  # 读取文件路径下 所有json文件名
        fileList.sort(key=lambda fn: os.path.getmtime(self.input_path + '/' + fn))  # 对 该文件路径 下的文件名 按照修改时间 进行 排序
        for day in fileList[:]:
            path = self.input_path + "/" + day  # 单个JSON文件的path
            print('当前json路径： ', path)
            one_json, cedian_one_json = self.readData(path, self.infe)

            if len(one_json):  # 不为空写入
                one_json = pd.concat([one_json, pd.DataFrame(cedian_one_json.values)])

                out_csvNeed = out_csvNeed.reset_index(drop=True)
                one_json = one_json.reset_index(drop=True)
                out_csvNeed = pd.concat([out_csvNeed, one_json], axis=1)
                cedian_one_json_col = list(cedian_one_json.index)
                self.count += 1

                col = self.readCols()
                col = col + cedian_one_json_col
                # print("Writefile, len of col", len(col))
                if len(col) == out_csvNeed.shape[0]:
                    out_csvNeed.index = col
                    print("out_csvNeed's index:", out_csvNeed)
                    self.generate_Csv(out_csvNeed, csv_name)  # 导出为csv文件
                else:
                    continue
        return out_csvNeed

    def start_(self, csv_name):
        self.output = self.Writefile(csv_name)

    def generate_Csv(self, out, name):
        out = out.transpose()
        # 合并冷通道温度

        # 2022.12.16 输出路径不存在则 新创建
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)
        out = out.sort_values('sampleTime', ascending=True)

        out.to_csv(self.output_path + name + '.csv', index=False, encoding='utf-8-sig')
