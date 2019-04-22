import os
import random
import time
import json
from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import ui.page_history as history
import ui.mg as mg
from django.urls import path
from django.shortcuts import render
from django.http import *
import ui.scada as scada
import codecs
import xlrd
import re
import uuid

profile_path = scada.profile_dir_path + '/collector.json'


def read_collector_profile_without_error():
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = {
            'unit_list': dict()
        }

    return profile


def write_collector_profile_without_error(new_profile):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = {
            'unit_list': dict()
        }

    profile = dict(profile, **new_profile)

    with codecs.open(profile_path, mode='w', encoding='utf8') as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)

    return profile


def read_collector_unit_without_error():
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')['unit_list']
    except:
        profile = dict()

    return profile


def merge_collector_unit_without_error(unit_profile):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = {
            'unit_list': dict()
       }

    profile['unit_list'] = dict(profile['unit_list'], **unit_profile)

    with codecs.open(profile_path, mode='w', encoding='utf8') as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)

    return profile


def write_collector_unit_without_error(unit_profile):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = {
            'unit_list': dict()
       }

    profile['unit_list'] = unit_profile

    with codecs.open(profile_path, mode='w', encoding='utf8') as file:
        json.dump(profile, file, ensure_ascii=False, indent=2)

    return profile


def show_general_collector_profile_page(request):
    if request.method == 'GET':
        profile = read_collector_profile_without_error()
        return render(request, "93-采集器控制管理/01-采集器基本信息.html", context=profile)

    profile = {key: values[0] for key, values in dict(request.POST).items()}
    write_collector_profile_without_error(profile)
    return HttpResponseRedirect(request.path)


def show_collector_env_page(request):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = {
            'unit_list': dict()
        }

    if 'env' not in profile:
        profile['env'] = ""

    if request.method == 'POST':
        profile['env'] = request.POST['env'].split('\r\n')

        with codecs.open(profile_path, mode='w', encoding='utf8') as file:
            json.dump(profile, file, ensure_ascii=False, indent=2)

        return HttpResponseRedirect(request.path)

    context = dict()
    context['env'] = "\r\n".join(profile['env'])
    return render(request, "93-采集器控制管理/03-采集器环境变量.html", context=context)


def send_back_env_matcher(request):
    try:
        with codecs.open(profile_path, encoding='utf8') as file:
            profile = json.loads(file.read(), encoding='utf8')
    except:
        profile = dict()

    if 'env' not in profile:
        profile['env'] = ""

    match = [env.split('=')[0] for env in profile['env']]
    return JsonResponse(match, safe=False)


def show_collector_unit_list_page(request):
    context = dict()
    context['unit_list'] = read_collector_unit_without_error()
    return render(request, "93-采集器控制管理/02-采集单元列表.html", context=context)


def delete_collector_unit(request):
    try:
        id = request.GET['id']
        units = read_collector_unit_without_error()
        del units[id]
        write_collector_unit_without_error(units)
    except:
        pass

    return HttpResponseRedirect('/dev/collector/list/')


def show_define_collector_unit_page(request):
    if request.method == 'GET':
        context = dict()
        user_list = list()
        name_list = list()

        try:
            profile = read_collector_unit_without_error()

            for id, unit in profile.items():
                user_list.append(unit['user'])
                name_list.append(unit['name'])
            id = request.GET['id']
            unit = profile[id]
        except:
            unit = {
                'id': uuid.uuid4()
            }
        context['unit'] = unit

        context['unit_user_template'] = set(user_list) - {'default-collector'}
        context['unit_name_template'] = set(name_list) - {'collector'}
        return render(request, "93-采集器控制管理/04-采集单元定义表单.html", context=context)
    else:
        unit = dict()

        unit['id'] = request.POST['id']
        unit['name'] = request.POST['name']
        unit['user'] = request.POST['user']
        unit['type'] = request.POST['type']
        unit['ttw'] = request.POST['ttw']
        unit['root'] = request.POST['root']
        unit['path'] = request.POST['path']

        unit_profile = {
            unit['id']: unit
        }
        merge_collector_unit_without_error(unit_profile)

        return HttpResponseRedirect(request.path.replace('define', 'list'))


def show_all_matched(excel, sheet_name, node_list):
    try:
        sheet = excel.sheet_by_name(sheet_name)
    except:
        return list()

    # 匹配环境变量
    r = re.compile(r'\$\(\S+\)')

    if len(node_list) > 0 and r.match(node_list[0]):
        prefix = node_list.pop(0) + '/'
    else:
        prefix = ''

    if len(node_list) == 0:
        nodes = list()
        for line, row in enumerate(sheet.get_rows()):
            if line == 0:
                continue

            if row[2].value in {'int', 'float', 'string'}:
                if int(row[1].value) > 1:
                    nodes.append(prefix + row[0].value + '/[{}]'.format(int(row[1].value)))
                else:
                    nodes.append(prefix + row[0].value)
            else:
                if int(row[1].value) > 1:
                    nodes.append(prefix + row[0].value + '/$')
                else:
                    nodes.append(prefix + row[0].value)

        return nodes
    else:
        try:
            next_node_list = node_list[1:]
        except IndexError:
            next_node_list = list()

        sheet_name = '不可能产生的表名称234nnjkndf'
        for row in sheet.get_rows():
            if row[0].value == node_list[0]:
                sheet_name = row[2].value
                break

        nodes = show_all_matched(excel, sheet_name, next_node_list)
        return [prefix + node_list[0] + '/' + node for node in nodes]


databus_profile = scada.profile_dir_path + '/' + '实时中心数据 V1.0T1-20181219(对外版).xlsx'
_excel = xlrd.open_workbook(databus_profile)


def send_back_path_matcher(request):
    node_list = request.GET['q'].rstrip().lstrip().split('/')

    while '' in node_list:
        node_list.remove('')

    try:
        excel = _excel
        sheet_name = '实时数据总集'
        paths_list = ['/' + p for p in show_all_matched(excel, sheet_name, node_list)]
    except Exception as e:
        print(e)
        paths_list = list()

    return JsonResponse(paths_list, safe=False)


urlpatterns = [
    path('', show_general_collector_profile_page),

    path('env/', show_collector_env_page),
    path('define/', show_define_collector_unit_page),

    path('define/hotpath/', send_back_path_matcher),
    path('define/hotenv/', send_back_env_matcher),

    path('list/', show_collector_unit_list_page),
    path('list/delete/', delete_collector_unit),
]
urls = (urlpatterns, 'collector', 'collector')
