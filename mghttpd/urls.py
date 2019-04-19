"""mghttpd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.http import *
import mimetypes
import os

import ui.page_history as history
import ui.page_bms as bms
import ui.page_main as main
import ui.page_pcs as pcs
import ui.page_collector as collector
import ui.page_settings as app_settings
import ui.page_error as error
import ui.page_report as report
import ui.page_aircondition as air
import ui.page_sample as sample
import ui.page_grid as grid
import ui.page_devel as devel
import ui.page_linkage as linkage
import ui.page_scada as scada
import ui.page_linux as linux
import ui.page_log as log


def mg_started(request):
    respons = HttpResponse('{}')
    respons['Access-Control-Allow-Origin'] = '*'
    return respons


def sendback_static_file(request):
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    project_dir_path = os.path.dirname(current_dir_path)
    filename = project_dir_path + "/ui" + request.path

    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(filename, 1024))
    response['Content-Type'] = mimetypes.guess_type(filename)[0]

    return response


urlpatterns = [
    # 静态文件
    re_path('static/', sendback_static_file),
    path('favicon.ico', lambda request: HttpResponseRedirect("/static/favicon.ico")),

    # 管理页面重定向
    path('admin/', admin.site.urls),

    # 系统状态控制展示区
    path("scada/", scada.urls),

    # 错误重定位
    path("error/", error.urls),

    # 日志管理
    path("log/", log.urls),

    # 显示BMS信息
    path('bms/', bms.urls),

    # 显示PCS信息
    path('pcs/', pcs.urls),

    # 图形曲线
    path('grid/', grid.urls),

    # 开发参数
    path("dev/", devel.urls),

    # 历史记录
    path("history/", history.urls),

    # 系统参数配置页面
    path("settings/", app_settings.urls),

    # 系统一次图
    path("linkage/", linkage.urls),

    # 系统启动标识
    path('mg-started.json', mg_started),

    # 首页重定向
    path('', main.index),
    path('version/', main.version),

    # 操作系统管理页面
    path('linux/', linux.urls),
    path('logout/', lambda request: HttpResponseRedirect('/linux/logout/')),
    path('change_user/', lambda request: HttpResponseRedirect('/linux/change_user/')),
    path('reboot/', lambda request: HttpResponseRedirect('/linux/reboot/')),
    path('halt/', lambda request: HttpResponseRedirect('/linux/halt/')),

    # 采样信息页面
    path("sample/", sample.urls),

    # 空调
    path('air-conditioner/', air.show_all_list),
    path('air-conditioner/<int:aid>/', air.show_aircondition),

    # 报表
    path('report/system/', report.show_system_report),
    path('report/days/<str:start_times>/<str:end_times>/', report.system_report_export),

    #功率曲线
    path('power/grid/', bms.show_bms_grid),
]

