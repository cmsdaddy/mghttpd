from django.shortcuts import render
from django.http import *
from ui.models import *
from django.db.models import *
import os
import ui.mg as mg
import random
import ui.api as api
import time
import ui.page_history as history
import json
import os
import sys


default_const_config_file = 'data/ems-config.const-default.json'
default_config_file = 'data/ems-config.default.json'


# 显示帮助文档
def show_ems_settings_doc(request):
    HttpResponseRedirect('/doc/ems/settings/')


# 加载ems配置参数文件
def load_ems_config_file(file_name):
    try:
        with open(file_name) as file:
            j = json.load(file)
            return j
    except:
        return None


# 将验证过的请求保存
def save_ems_config_file(file_name, pairs):
    try:
        old = dict()
        with open(file_name, 'r') as file:
            old = json.load(file)

        new = dict(old, **pairs)
        with open(file_name, "w") as file:
            json.dump(new, file, ensure_ascii=False, indent=4)
        return True
    except:
        return False


# 根据命令显示EMS页面
def show_eme_settting_page(request, cmd):
    if os.path.exists(default_config_file) is False:
        os.system("cp %s %s" % (default_const_config_file, default_config_file))

    config_file = default_config_file

    context = dict()
    context['request'] = request
    context['ems'] = load_ems_config_file(config_file)
    context['message'] = cmd

    return render(request, "ems/settings.html", context=context)


# 显示单个设置值
def show_ems_single_settings(request):
    return show_eme_settting_page(request, "show")


# 根据命令显示EMS页面
def show_ems_index(request):
    context = dict()
    return render(request, "ems/index.html", context=context)


# 提供ems的配置参数
def show_ems_json_setings(request):
    if os.path.exists(default_config_file) is False:
        os.system("cp %s %s" % (default_const_config_file, default_config_file))
    config_file = default_config_file

    try:
        with open(config_file) as file:
            j = json.load(file)
            j['status'] = 'ok'
            j['reason'] = ''
            j['售电经济利益化标识标志'] = [ j['售电经济利益化标识标志时长'], j['售电经济利益化标识标志价格'] ]
            j['Pcs充电计划起止时间'] = [ j['Pcs充电计划起始序列'], j['Pcs充电计划终止序列'] ]
            j['Pcs放电计划起止时间'] = [ j['Pcs放电计划起始序列'], j['Pcs放电计划终止序列'] ]
            resp = dict()
            resp['status'] = 'ok'
            resp['reason'] = ''
            resp['data'] = j
            r = json.dumps(resp, ensure_ascii=False)
            respons = HttpResponse(r)
            respons['Content-Type'] = 'application/json'
            return respons
    except Exception as e:
        print(e)
        respons = HttpResponse('{"status": "fail", "reason": "config file invalid!"}')
        respons['Content-Type'] = 'application/json'
        return respons


# 保存配置参数，POST方法
def save_ems_setings(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(request)

    save = dict()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        for x in request.POST:
            save[x] = eval(request.POST[x])
    except:
        history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS配置数据失败-表单错误！", request.user.username)
        return show_eme_settting_page(request, "fail")

    if os.path.exists(default_config_file) is False:
        os.system("cp %s %s" % (default_const_config_file, default_config_file))

    config_file = default_config_file
    if save_ems_config_file(config_file, save) is False:
        history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS配置数据失败-文件错误！", request.user.username)
        return show_eme_settting_page(request, "fail")

    history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS配置数据成功！", request.user.username)
    return show_eme_settting_page(request, "success")


# 显示应用场景选项
def show_ems_advance_options(request):
    if request.method == 'POST':
        save = dict()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            for x in request.POST:
                if x == '用户并网端的总功率':
                    save[x] = float(request.POST[x])
                else:
                    save[x] = request.POST[x]
        except Exception as e:
            history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS高级参数失败-表单错误！", request.user.username)
            return HttpResponseRedirect("/error/formerror/?code=100&next=/ems/options/")

        if os.path.exists(default_config_file) is False:
            os.system("cp %s %s" % (default_const_config_file, default_config_file))

        config_file = default_config_file
        if save_ems_config_file(config_file, save) is False:
            history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS高级参数失败-文件错误！", request.user.username)
            return HttpResponseRedirect("/error/formerror/?code=101&next=/ems/options/")

        history.do_record("system", history.CODE_YAOTIAO, now, 0, 0, "写EMS高级参数成功！", request.user.username)
        return HttpResponseRedirect("/error/formok/?code=0&next=/ems/options/")

    if os.path.exists(default_config_file) is False:
        os.system("cp %s %s" % (default_const_config_file, default_config_file))

    config_file = default_config_file
    context = dict()
    context['request'] = request
    context['ems'] = load_ems_config_file(config_file)

    return render(request, "ems/应用场景选项.html", context=context)
