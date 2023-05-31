# -*- coding:utf-8 -*-

import pygplates
import pandas as pd
from pyproj import Transformer
import os


# this function is used to calculate the finite rotation
def cal_rotation_value(position_lastTIME, position_thisTIME):
    rotation_adjustment = pygplates.FiniteRotation(position_lastTIME, position_thisTIME)
    rotation_value = rotation_adjustment.get_lat_lon_euler_pole_and_angle_degrees()
    return rotation_value


def main():
    # 这一步的目的是找到文件夹中所有控制点的csv进行合并，并将合并的excel修改成需要的样子
    data_list = []  # 创建一个列表
    obj = os.walk(r"C:\Users\zjj\Desktop\PMRB\PMRB_Control_Points")  # 遍历文件夹下的所有文件
    for in_folder, b, file_list in obj:
        for name in file_list:
            if name.startswith("control_points") and name.endswith(".csv"):
                file_abs_path = os.path.join(in_folder, name)  # 将前缀是“control”，后缀是“.csv”的文件进行路径拼接
                data_list.append(pd.read_csv(file_abs_path, header=None, skiprows=7, usecols=[0, 1, 6, 7],
                                             names=["UTM_X", "UTM_Y", "POINTS_NAME",
                                                    "LAYER"]))  # 读取找到的文件（没有表头，忽略前7行，用第0167列，命名），并赋值给创建的列表
    data_all = pd.concat(data_list)  # 将上面列表中的多个datafarm合并成一个
    df = pd.DataFrame(
        {'LAYER': ["T0", "T0-T20", "T0-T30", "T0-T40", "T0-T50", "T0-T60", "T20", "T30", "T40", "T50", "T60",
                   "T70", "T80", "T90", "T100", "Tg", "SD", "PD", "T71", "T55"],
         "LATITUDE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "LONGITUDE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "TIME": [0, 0, 0, 0, 0, 0, 2.6, 5.3, 11.6, 16, 23, 34, 39, 49, 66, 66, 45, 35, 30, 20],
         "EULER_LAT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "EULER_LON": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "ROT_ANGLE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "FIXED_ID": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "SYMBOL": ["!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!"]
         })  # 创建一个datafarm，目的是实现excel中vlookup的功能，将时间赋给每个地层，同时增加需要的几列。
    points_plate_id = pd.read_csv(r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\PMRB_Points_Merge.txt", header=None, skiprows=1, usecols=[3, 7],
                                  names=["POINTS_NAME",
                                         "PLATE_ID"])  # 文件来源：在arcgis中输入所有点的plate_id，导出了这个csv，目的是将plate_id赋给每个点
    data_path = r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\DATA_SUM.xlsx"  # 创建一个路径
    with pd.ExcelWriter(data_path) as write:  # 向创建的路径中写入数据
        data_all.to_excel(write, sheet_name="points", index=None)  # 将"data_all"写入目标excel中，sheet名为：points
        df.to_excel(write, sheet_name="seek_time", index=None)  # 将"df"写入目标excel中，sheet名为：seek_time
        points_plate_id.to_excel(write, sheet_name="plate_id",
                                 index=None)  # 将"points_plate_id"写入目标excel中，sheet名为：plate_id
    data1 = pd.read_excel(data_path, sheet_name="points")  # 读取表格中points的内容
    data2 = pd.read_excel(data_path, sheet_name="seek_time")  # 读取表格中seek_time的内容
    data3 = pd.read_excel(data_path, sheet_name="plate_id")  # 读取表格中plate_id的内容
    merge_data = pd.merge(data1, data2, on="LAYER", how="left")  # 将表格中的points和seek，通过共同的列（LAYER)进行合并，目的是把时间写进去，同时加几个新列
    merge_data.to_excel(data_path, index=None)  # 将合并的数据保存到excel中
    data4 = pd.read_excel(data_path)  # 读取表格中内容
    merge_data = pd.merge(data4, data3, on="POINTS_NAME", how="left")  # 将表格中内容通过“POINTS_NAME"与data3合并，目的是将PLATE_ID写进去
    merge_data.to_excel(data_path, index=None)  # 将合并的数据保存到excel中
    merge_data["DOI"] = merge_data["POINTS_NAME"].str.split('-').str[0]  # 将数据中"POINTS_NAME"这一列通过'-'拆分单元格中的内容，并取第1个值
    merge_data["SECTION_NAME"] = merge_data["POINTS_NAME"].str.split('_').str[
        0]  # 将数据中"POINTS_NAME"这一列通过'_'拆分单元格中的内容，并取第1个值
    merge_data["POINTS_ATTRIBUTE"] = merge_data["POINTS_NAME"].str.split('_').str[
        1]  # 将数据中"POINTS_NAME"这一列通过'_'拆分单元格中的内容，并取第2个值
    merge_data["PERIOD"] = merge_data["POINTS_NAME"].str.split('_').str[2]  # 将数据中"POINTS_NAME"这一列通过'_'拆分单元格中的内容，并取第3个值
    merge_data["POINTS_NUMBER"] = merge_data["POINTS_NAME"].str.split('_').str[
        3]  # 将数据中"POINTS_NAME"这一列通过'_'拆分单元格中的内容，并取第4个值
    merge_data.sort_values(by=["SECTION_NAME", "POINTS_NUMBER", "TIME"],
                           inplace=True)  # 将数据通过"SECTION_NAME"和"POINTS_NUMBER"和"TIME"进行排序，按从小到大

    # 这一步是进行坐标转化和计算旋转轴和角度
    for index, row in merge_data.iterrows():

        transformer = Transformer.from_crs("epsg:32650", "epsg:4326")
        a = merge_data.loc[index, 'UTM_X']
        b = merge_data.loc[index, 'UTM_Y']
        value_84 = transformer.transform(a, b)
        merge_data.loc[index, 'LATITUDE'] = value_84[0]
        merge_data.loc[index, 'LONGITUDE'] = value_84[1]
    for index, row in merge_data.iterrows():
        if row['TIME'] == 0:
            id = merge_data.loc[index, 'PLATE_ID']  # 读取0Ma时的PLATE_ID的值
            lat_at0Ma = merge_data.loc[index, 'LATITUDE']
            lon_at0Ma = merge_data.loc[index, 'LONGITUDE']
            position_at0Ma = (lat_at0Ma, lon_at0Ma)
        else:
            merge_data.loc[
                index, 'PLATE_ID'] = id  # 这里为什么还要对PLATE_ID这一列进行赋值呢？因为，从arcgis中导出的csv中的PLATE_ID只有0Ma的值，不同时间同一个点的名字并不相同
            lat_this_time = merge_data.loc[index, 'LATITUDE']
            lon_this_time = merge_data.loc[index, 'LONGITUDE']
            position_this_time = (lat_this_time, lon_this_time)
            rotation_value = cal_rotation_value(position_at0Ma, position_this_time)
            merge_data.loc[index, 'EULER_LAT'] = rotation_value[0]
            merge_data.loc[index, 'EULER_LON'] = rotation_value[1]
            merge_data.loc[index, 'ROT_ANGLE'] = rotation_value[2]
        if row['POINTS_ATTRIBUTE'] == "s":
            plateid = merge_data.loc[index, 'PLATE_ID']  # 如果点的属性是“s“，那么PLATE_ID就为0，否则为start点的PLATE_ID
            merge_data.loc[index, 'FIXED_ID'] = 000
        else:
            merge_data.loc[index, 'FIXED_ID'] = plateid

    merge_data.to_excel(r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\DATA_SUM.xlsx", index=False)  # 把最终的数据保存到表格
    # merge_data.to_csv(r"C:\Users\zjj\PycharmProjects\pythonProject\data\reconstruction\Rotfile.rot", index=False,
    #                   header=False,
    #                   sep=' ',
    #                   columns=["PLATE_ID", "TIME", "EULER_LAT", "EULER_LON", "ROT_ANGLE", "FIXED_ID", "SYMBOL"])
    data = pd.read_excel(r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\DATA_SUM.xlsx", dtype=object)
    data.to_csv(r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\Rotfile.rot", index=False,
                header=False,
                sep=' ',
                columns=["PLATE_ID", "TIME", "EULER_LAT", "EULER_LON", "ROT_ANGLE", "FIXED_ID", "SYMBOL"])
    pd.set_option('display.max_columns', None)
    print(merge_data.head())



if __name__ == "__main__":
    main()
    print('完成')
