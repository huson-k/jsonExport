# 解压文件

import glob
import json
import os
import shutil
import time
import zipfile

from json2csv import dealFile


def unzip(filename):
    print('正在解压' + filename)
    zip_file = zipfile.ZipFile(filename)
    if not os.path.isdir(filename + "_dir"):
        os.mkdir(filename + "_dir")
    for names in zip_file.namelist():
        zip_file.extract(names, filename + "_dir/")
        print('-- 解压进度 ' + str(round(zip_file.namelist().index(names) / len(zip_file.namelist()), 4) * 100)+" % --")
    zip_file.close()
    print('解压完成，退出unzip')
    return filename + "_dir"


def jf_classify(files_dir):
    files_dir = files_dir + '/home/yons/server-1/data/'
    files_dir_tolist = files_dir.split('/')
    dir_name = files_dir_tolist[-2]
    fileList = os.listdir(files_dir)  # 读取文件路径下 所有json文件名
    fileList.sort(key=lambda fn: os.path.getmtime(files_dir + fn))  # 对 该文件路径 下的文件名 按照修改时间 进行 排序
    # print('\n===================================== sort' + chosen_JF + 'JF =====================================')
    print(dir_name, " path have", len(fileList), " JSON files.\n")

    nice_shutil = 0  # 定义 修改成功 一个JSON文件 次数
    JF = []

    for json_id in fileList:
        json_file_path = files_dir + json_id  # 定义 JSON文件 路径

        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                load_dict = json.load(f)

                if load_dict['aiGroup']:
                    jF_info = load_dict['aiGroup']
                    JF_name = jF_info['aiGroupName']
                    JF.append(JF_name)
                    chosen_JF = JF_name
                    if (chosen_JF == '202' or chosen_JF == '203' or chosen_JF == '204'):
                        export_fir = files_dir + 'data' + '_JF' + chosen_JF + "/"
                        # 分类库shutil
                        # if JF_name != chosen_JF:
                        #     print("it's", JF_name, ", PASS.")
                        # elif JF_name == chosen_JF:  # 选定特定机房分类
                        file_modification_time = os.path.getmtime(json_file_path)  # 定义当前JSON文件修改时间（返回“ float”类的浮点值）
                        file_local_time = time.ctime(file_modification_time)  # 转换为可读的日期
                        # 输出当前打开的 JSON 文件
                        print("open the ---", nice_shutil + 1, "th--- JSON file", "; time of file:", file_local_time)
                        # 即将export的路径名
                        # moveto_path = files_dir[:-1] + '_JF' + chosen_JF + "/"
                        moveto_path = export_fir
                        if not os.path.isdir(moveto_path):
                            os.makedirs(moveto_path)  # 输出路径若不存在，先创建好目录之后再输入
                        shutil.move(json_file_path, moveto_path)
                        print(chosen_JF + ' json successfully exported.')
                        nice_shutil += 1
            JF = list(set(JF))
        except:
            print("mac bug: .DS_Store")  # mac系统.DS_Store文件 可能 导致文件读取失败
    json_file_202 = files_dir + 'data' + '_JF202/'
    json_file_203 = files_dir + 'data' + '_JF203/'
    json_file_204 = files_dir + 'data' + '_JF204/'
    return json_file_202, json_file_203, json_file_204


if __name__ == '__main__':
    # JF_KT_num = [6, 20, 13, 20, 16]  # 201/202/203/205JF 对应的空调数目
    # data_jf = ['data_JF201', 'data_JF202', 'data_JF203', 'data_JF204', 'data_JF205']
    data_jf = ['data_JF203', 'data_JF204']
    JF_KT_num = [13, 20]  # 201/202/203/205JF 对应的空调数目
    # path = "F:\dataNeeded\zipData"
    path = 'F:\dataNeeded\zipData\preRun'
    file_lst = glob.glob(path + '/*')
    filename_lst = [os.path.basename(i) for i in file_lst]

    for filename in filename_lst:
        if '.' in filename:
            suffix = filename.split('.')[-1]
            if suffix == 'zip':
                # decom_filename:解压后的文件名
                decom_filename = unzip(path + "/" + filename)
            # if suffix == 'zip_dir':
            #     decom_filename=path+"/"+filename
                print('decom_filename', decom_filename)
                for data_jf_i in range(len(data_jf)): # 分机房导
                    name = decom_filename.split('/')[-1]
                    csv_name = name[0:8] + data_jf[data_jf_i]  # 导出为csv名称
                    print('csv_name:', csv_name)
                    output_path = 'F:/dataNeeded/preRunCSV/' + data_jf[data_jf_i] + '/'  # 导出的csv路径
                    # s_202 = dealFile(decom_filename+'/0520/', output_path, JF_KT_num[data_jf_i], data_jf[data_jf_i][-3:])
                    s_202 = dealFile(decom_filename + '\home\yons\server-1\data', output_path, JF_KT_num[data_jf_i],
                                     data_jf[data_jf_i][-3:])
                    # s_202 = dealFile(decom_filename + '\data', output_path, JF_KT_num[data_jf_i],
                    #                  data_jf[data_jf_i][-3:])
                    # s_202 = dealFile(decom_filename + '', output_path, JF_KT_num[data_jf_i],
                    #                  data_jf[data_jf_i][-3:])
                    s_202.start_(csv_name)  # 正式开始处理文件夹下的JSON文件
