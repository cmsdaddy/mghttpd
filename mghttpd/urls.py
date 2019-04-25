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
from django.urls import path, re_path, include
from django.http import *
import mimetypes
import os
import ui.page_bms as bms
import ui.page_report as report


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
    # favicon 路由
    path('favicon.ico', lambda request: HttpResponseRedirect("/static/favicon.ico")),
    # 系统启动标识
    path('mg-started.json', mg_started),

    # 系统状态控制展示区
    path("scada/", include('ui.page_scada')),
    # 错误重定位
    path("error/", include('ui.page_error')),
    # 日志管理
    path("log/", include('ui.page_log')),

    # 显示BMS信息
    path('bms/', include('ui.page_bms')),
    # 显示PCS信息
    path('pcs/', include('ui.page_pcs')),
    # 空调
    path('air-conditioner/', include('ui.page_aircondition')),
    # 采样信息页面
    path("sample/", include('ui.page_sample')),

    # 图形曲线
    path('grid/', include('ui.page_grid')),
    # 开发参数
    path("dev/", include('ui.page_devel')),
    # 历史记录
    path("history/", include('ui.page_history')),
    # 系统参数配置页面
    path("settings/", include('ui.page_settings')),
    # 系统一次图
    path("linkage/", include('ui.page_linkage')),

    # 操作系统管理页面
    path('linux/', include('ui.page_linux')),

    # 报表
    path('report/system/', report.show_system_report),
    path('report/days/<str:start_times>/<str:end_times>/', report.system_report_export),

    #功率曲线
    path('power/grid/', bms.show_bms_grid),

    path('svg/', include("ui.page_svg")),

    path('', include('ui.page_main')),
]

