# 默认安装数据点
import csv
from ui.models import *


data_point_type_list = {}
element_type_list = {}


# 安装电池堆的数据点
def install_battery_heap_datapoints(heap_page, heap):
    csv_template = "data/电池堆数据点-模板.csv"
    count = 0

    with open(csv_template, ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                obj = DataPoint.objects.get(access_path=row['path'])
            except Exception as e:
                try:
                    datatype = data_point_type_list[ row['type'] ]
                except:
                    datatype = DataPointType.objects.get(name=row['type'])
                    data_point_type_list[row['type']] = datatype

                obj = DataPoint(
                    full_name=row['fullname'] % (heap + 1),
                    short_name=row['shortname'],
                    datatype = datatype,
                    access_path=row['path'] % heap,
                    k=float(row['k']),
                    b=float(row['b']),
                    mask=int(row['mask'], 16),
                    dot=int(row['dot']),
                    unit=row['unit'],
                    max_record=int(row['records']),
                    refer_count = 1,
                    )
                obj.save()
                count += 1

    return count


# 安装电池组首页数据点
def install_battery_group_main_datapoints(page, heap, group):
    csv_template_list = [
        (u"摘要", u"data/电池组数据点摘要-模板.csv"),
        (u"遥测", u"data/电池组数据点遥测-模板.csv"),
        (u"遥信", u"data/电池组数据点遥信-模板.csv"),
    ]
    count = 0
    grid_dps = {}
    for typename, csv_template in csv_template_list:
        with open(csv_template, ) as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                eletype = element_type_list[ typename ]
            except:
                eletype = ElementType.objects.get(name=typename)

            for row in reader:
                try:
                    obj = DataPoint.objects.get(access_path=row['path'])
                except Exception as e:
                    try:
                        datatype = data_point_type_list[row['type']]
                    except:
                        datatype = DataPointType.objects.get(name=row['type'])
                        data_point_type_list[row['type']] = datatype

                    obj = DataPoint(
                        full_name = row['fullname'] % (heap + 1, group + 1),
                        short_name = row['shortname'],
                        datatype = datatype,
                        access_path = row['path'] % (heap, group),
                        k = float(row['k']),
                        b = float(row['b']),
                        mask = int(row['mask'], 16),
                        dot = int(row['dot']),
                        unit = row['unit'],
                        max_record = int(row['records']),
                        refer_count=1,
                    )
                    obj.save()
                count += 1

                ele = Element(page=page, name=row['shortname'], type=eletype)
                ele.save()
                ele.datapoint.add(obj)
                ele.save()

    grid_obj_list = []
    with open('data/电池组数据点图表-模板.csv', ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                obj = DataPoint.objects.get(access_path=row['path'])
            except Exception as e:
                try:
                    datatype = data_point_type_list[ row['type'] ]
                except:
                    datatype = DataPointType.objects.get(name=row['type'])
                    data_point_type_list[row['type']] = datatype

                obj = DataPoint(
                    full_name = row['fullname'] % (heap + 1, group + 1),
                    short_name = row['shortname'],
                    datatype = datatype,
                    access_path = row['path'] % (heap, group),
                    k = float(row['k']),
                    b = float(row['b']),
                    mask = int(row['mask'], 16),
                    dot = int(row['dot']),
                    unit = row['unit'],
                    max_record = int(row['records']),
                    refer_count=1,
                )
                obj.save()
            grid_obj_list.append(obj)

    if len(grid_obj_list):
        try:
            eletype = element_type_list[ "图表x12" ]
        except:
            eletype = ElementType.objects.get(name="图表x12")

        ele = Element(page=page, name="电池充放电曲线", type=eletype)
        ele.save()
        for obj in grid_obj_list:
            ele.datapoint.add(obj)
        ele.save()

    return count + 1


# 安装电池组的遥调数据点
def install_battery_group_yaotiao_datapoints(page, heap, group):
    csv_template = "data/电池组数据点遥调-模板.csv"
    count = 0
    with open(csv_template, ) as csvfile:
        reader = csv.DictReader(csvfile)

        try:
            eletype = element_type_list["遥测"]
        except:
            eletype = ElementType.objects.get(name="遥测")

        for row in reader:
            try:
                obj = DataPoint.objects.get(access_path=row['path'])
            except Exception as e:
                try:
                    datatype = data_point_type_list[ row['type'] ]
                except:
                    datatype = DataPointType.objects.get(name=row['type'])
                    data_point_type_list[row['type']] = datatype

                obj = DataPoint(
                    full_name = row['fullname'] % (heap + 1, group + 1),
                    short_name = row['shortname'],
                    datatype = datatype,
                    access_path = row['path'] % (heap, group),
                    k = float(row['k']),
                    b = float(row['b']),
                    mask = int(row['mask'], 16),
                    dot = int(row['dot']),
                    unit = row['unit'],
                    max_record = int(row['records']),
                    refer_count=1,
                )
                obj.save()
            count += 1

            ele = Element(page=page, name=row['shortname'], type=eletype)
            ele.save()
            ele.datapoint.add(obj)
            ele.save()

    return count


# 安装电池组的单体数据点
def install_battery_group_danti_datapoints(page_V, page_T, page_SOC, page_SOH, heap, group):
    csv_template_list = [
        (page_V, "data/电池组数据点单体电压-模板.csv"),
        (page_T, "data/电池组数据点单体温度-模板.csv"),
        (page_SOC, "data/电池组数据点单体SOC-模板.csv"),
        (page_SOH, "data/电池组数据点单体SOH-模板.csv"),
    ]
    count = 0
    for page, csv_template in csv_template_list:
        with open(csv_template, ) as csvfile:
            reader = csv.DictReader(csvfile)

            try:
                eletype = element_type_list["遥测"]
            except:
                eletype = ElementType.objects.get(name="遥测")

            for row in reader:
                try:
                    obj = DataPoint.objects.get(access_path=row['path'])
                except Exception as e:
                    try:
                        datatype = data_point_type_list[row['type']]
                    except:
                        datatype = DataPointType.objects.get(name=row['type'])
                        data_point_type_list[row['type']] = datatype

                    obj = DataPoint(
                        full_name = row['fullname'] % (heap + 1, group + 1),
                        short_name = row['shortname'],
                        datatype = datatype,
                        access_path = row['path'] % (heap, group),
                        k = float(row['k']),
                        b = float(row['b']),
                        mask = int(row['mask'], 16),
                        dot = int(row['dot']),
                        unit = row['unit'],
                        max_record = int(row['records']),
                        refer_count = 1,
                    )
                    obj.save()
                count += 1

                ele = Element(page=page, name=row['shortname'], type=eletype)
                ele.save()
                ele.datapoint.add(obj)
                ele.save()

    return count
