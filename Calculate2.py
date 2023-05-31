# -*- coding:utf-8 -*-

import os
import pygplates
import pandas as pd
from pyproj import Transformer
from geographiclib.geodesic import Geodesic


def cal_rotation_value(position_0Ma, position_this_time):
    rotation_adjustment = pygplates.FiniteRotation(position_0Ma, position_this_time)
    rotation_value = rotation_adjustment.get_lat_lon_euler_pole_and_angle_degrees()
    return rotation_value


def transformer_utm_to_wgs84(UTM_X, UTM_Y):
    transformer = Transformer.from_crs("epsg:32650", "epsg:4326")
    wgs84 = transformer.transform(UTM_X, UTM_Y)
    return wgs84


def main():
    points_plate_id = pd.read_csv(r"C:\Users\zjj\Desktop\PMRB\PMRB_Python\PMRB_Points_Merge.txt", header=None, skiprows=1, usecols=[3, 7],
                                  names=["POINTS_NAME", "PLATE_ID"])
    df = pd.DataFrame(
        {'LAYER': ["T0", "T0-T20", "T0-T30", "T0-T40", "T0-T50", "T0-T60", "T20", "T30", "T40", "T50", "T60",
                   "T70", "T80", "T90", "T100", "Tg", "SD", "PD", "T71"],
         "LATITUDE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "LONGITUDE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "TRANSLATION_LAT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "TRANSLATION_LON": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "TIME": [0, 0, 0, 0, 0, 0, 2.6, 5.3, 11.6, 16, 23, 34, 39, 49, 66, 66, 45, 35, 30],
         "EULER_LAT": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "EULER_LON": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "ROT_ANGLE": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "FIXED_ID": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         "SYMBOL": ["!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!", "!"]
         })
    x1 = int(input("请输入plate_id:"))
    x2 = int(input("请输入fixed_id:"))
    for index, row in points_plate_id.iterrows():
        if row["PLATE_ID"] == x1:
            point_name = points_plate_id.loc[index, "POINTS_NAME"]
            print(point_name)
            section_name = point_name.split('_')[0]
            print(section_name)
            file_name = "control_points_" + section_name + ".csv"
            print(file_name)
            obj = os.walk(r"C:\Users\zjj\Desktop\PMRB\PMRB_Control_Points")
            for in_folder, b, file_list in obj:
                for name in file_list:
                    if name == file_name:
                        file_abs_path = os.path.join(in_folder, name)
                        print(file_abs_path)
            data = pd.read_csv(file_abs_path, header=None, skiprows=7, usecols=[0, 1, 6, 7],
                               names=["UTM_X", "UTM_Y", "POINTS_NAME", "LAYER"])
            merge_data = pd.merge(data, df, on="LAYER", how="left")
            merge_data = pd.merge(merge_data, points_plate_id, on="POINTS_NAME", how="left")
            merge_data["SECTION_NAME"] = merge_data["POINTS_NAME"].str.split('_').str[0]
            merge_data["POINTS_ATTRIBUTE"] = merge_data["POINTS_NAME"].str.split('_').str[1]
            merge_data["PERIOD"] = merge_data["POINTS_NAME"].str.split('_').str[2]
            merge_data["POINTS_NUMBER"] = merge_data["POINTS_NAME"].str.split('_').str[3]
            merge_data.sort_values(by=["SECTION_NAME", "POINTS_NUMBER", "TIME"], inplace=True)
            merge_data.to_excel(r"C:\Users\zjj\Desktop\test3\test1.xlsx")

    for index, row in merge_data.iterrows():
        a = merge_data.loc[index, 'UTM_X']
        b = merge_data.loc[index, 'UTM_Y']
        wgs84 = transformer_utm_to_wgs84(a, b)
        merge_data.loc[index, 'LATITUDE'] = wgs84[0]
        merge_data.loc[index, 'LONGITUDE'] = wgs84[1]
    for index, row in merge_data.iterrows():
        if row['TIME'] == 0:
            id = merge_data.loc[index, 'PLATE_ID']  # 读取0Ma时的PLATE_ID的值

        else:
            merge_data.loc[index, 'PLATE_ID'] = id
    for index, row in merge_data.iterrows():
        if row['PLATE_ID'] == x1:
            merge_data.loc[index, 'FIXED_ID'] = x2
        else:
            merge_data.loc[index, 'FIXED_ID'] = x1
    for index, row in merge_data.iterrows():
        if row['PLATE_ID'] == x1 and row['TIME'] == 0:
            base_lat = merge_data.loc[index, 'LATITUDE']
            base_lon = merge_data.loc[index, 'LONGITUDE']
            merge_data.loc[index, 'TRANSLATION_LAT'] = base_lat
            merge_data.loc[index, 'TRANSLATION_LON'] = base_lon
        if row['PLATE_ID'] == x1 and not row['TIME'] == 0:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']

    merge_data.sort_values(by=["SECTION_NAME", "TIME", "POINTS_NUMBER"], inplace=True)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d1" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d1":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d2" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d2":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d3" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d3":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d4" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d4":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d5" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d5":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d6" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d6":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d7" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d7":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d8" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d8":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d9" and row['PLATE_ID'] == x1:
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            base_lat = merge_data.loc[index, 'TRANSLATION_LAT']
            base_lon = merge_data.loc[index, 'TRANSLATION_LON']
            x = Geodesic.WGS84.Inverse(lat, lon, base_lat, base_lon)
            direction = x['azi1']
            distance = x['s12']
            print(direction)
            print(distance)
    for index, row in merge_data.iterrows():
        if row['PERIOD'] == "d9":
            lat = merge_data.loc[index, 'LATITUDE']
            lon = merge_data.loc[index, 'LONGITUDE']
            y = Geodesic.WGS84.Direct(lat, lon, direction, distance)
            merge_data.loc[index, 'TRANSLATION_LAT'] = y['lat2']
            merge_data.loc[index, 'TRANSLATION_LON'] = y['lon2']

    merge_data.sort_values(by=["SECTION_NAME", "POINTS_NUMBER", "TIME"], inplace=True)
    for index, row in merge_data.iterrows():
        if row['TIME'] == 0:
            lat_at0Ma = merge_data.loc[index, 'TRANSLATION_LAT']
            lon_at0Ma = merge_data.loc[index, 'TRANSLATION_LON']
            position_at0Ma = (lat_at0Ma, lon_at0Ma)
        else:
            lat_this_time = merge_data.loc[index, 'TRANSLATION_LAT']
            lon_this_time = merge_data.loc[index, 'TRANSLATION_LON']
            position_this_time = (lat_this_time, lon_this_time)
            rotation_value = cal_rotation_value(position_at0Ma, position_this_time)
            merge_data.loc[index, 'EULER_LAT'] = rotation_value[0]
            merge_data.loc[index, 'EULER_LON'] = rotation_value[1]
            merge_data.loc[index, 'ROT_ANGLE'] = rotation_value[2]

    merge_data.to_excel(r"C:\Users\zjj\Desktop\test3\test1.xlsx")
    data = pd.read_excel(r"C:\Users\zjj\Desktop\test3\test1.xlsx")
    data.to_csv(r"C:\Users\zjj\Desktop\test3\Rotfile.rot", index=False,
                header=False,
                sep=' ',
                columns=["PLATE_ID", "TIME", "EULER_LAT", "EULER_LON", "ROT_ANGLE", "FIXED_ID", "SYMBOL"])


if __name__ == "__main__":
    main()
    print('完成')