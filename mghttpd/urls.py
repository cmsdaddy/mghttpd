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
from django.urls import path
from django.http import *
#from channels.routing import ProtocolTypeRouter
#from channels.auth import AuthMiddlewareStack
#from channels.routing import ProtocolTypeRouter, URLRouter

#import ui.wsapi as wsapi

import ui.views

import ui.page_history as history
import ui.page_bms as bms
import ui.page_main as main
import ui.page_pcs as pcs
import ui.page_collector as collector
import ui.page_ems as ems
import ui.page_doc as doc
import ui.page_settings as settings
import ui.page_error as error
import ui.page_report as report
import ui.page_aircondition as air
import ui.page_sample as sample
import ui.page_grid as grid
import ui.devel as devel


admin.site.site_header = '用户登录'

def redirect_root_index(request):
    return HttpResponseRedirect("/page/")


def mg_started(request):
    respons = HttpResponse('{}')
    respons['Access-Control-Allow-Origin'] = '*'
    return respons


# 将无索引目录定位至第一个索引位置
def redirect_to_zero_index(request, **args):
    return HttpResponseRedirect(request.path + "0/")


def pac(request):
    with open("ui/pac.js") as f:
        txt = f.read()

    respons = HttpResponse(txt)
    respons['Content-Type'] = 'application/x-ns-proxy-autoconfig'
    return respons


#websocket_urlpatterns = [
#    path('ws/chat/<str:room_name>/', wsapi.WsApiGateWay),
#]


#application = ProtocolTypeRouter({
#    # Empty for now (http->django views is added by default)
#    'websocket': AuthMiddlewareStack(
#        URLRouter(
#            websocket_urlpatterns
#        )
#    ),
#})

urlpatterns = [
    path('celery/test/', ui.views.celery_test),
    path('favicon.ico', lambda request: HttpResponseRedirect("/static/favicon.ico")),

    # 文档路由
    path('doc/', doc.show_index),
    path('doc/ems/settings/', doc.show_index),

    # 错误重定位
    path("error/noerror/", error.noerror),
    path("error/formok/", error.form_commit_success),
    path("error/formerror/", error.form_commit_fail),

    # 管理页面重定向
    path('admin/', admin.site.urls),
    # path('admin/login/',main.show_login_page),

    # 参数配置页重定向
    path("polls/settings/", settings.show_settings_warning_page),
    path('settings/', settings.show_settings_warning_page),
    path('settings/refresh/', settings.refresh_system_configure),

    path('settings/scada_com/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/cloud/', lambda request: settings.show_autmatic_page(request, settings.云平台参数)),
    path('settings/peripheral/', lambda request: settings.show_autmatic_page(request, settings.外设数量参数)),
    path('settings/video/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/firecontrol/', lambda request: settings.show_autmatic_page(request, settings.消防参数)),
    path('settings/airconditioner/', lambda request: settings.show_autmatic_page(request, settings.空调参数)),
    path('settings/gpio/', lambda request: settings.show_autmatic_page(request, settings.开入开出盒参数)),

    # 通用设备配置页
    path('settings/inv/', lambda request: settings.show_autmatic_page(request, settings.INV参数)),
    path('settings/pcs/', lambda request: settings.show_autmatic_page(request, settings.PCS参数)),
    path('settings/bms/', lambda request: settings.show_autmatic_page(request, settings.BMS参数)),
    #ems参数配置
    path('settings/ems/', lambda request: settings.show_autmatic_page(request, settings.EMS参数)),

    path('settings/battery/', lambda request: settings.show_autmatic_page(request, settings.电池参数)),
    path('settings/report/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/general/', lambda request: settings.show_autmatic_page(request, settings.系统通用参数)),
    path('settings/datetime/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/password/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/backup/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/bell/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),

    # 开发选项
    path('settings/dev/autorun/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),
    path('settings/dev/collector/', lambda request: settings.show_autmatic_page(request, settings.监控通讯参数)),

    # 系统启动标识
    path('mg-started.json', mg_started),

    # 首页重定向
    path("polls/main/1/", main.index),
    path('page/', main.index),
    path('', main.index),
    path('version/', main.version),
    # 退出系统选择页面

    path('logout/', main.show_logout_page),
    path('change_user/', main.show_change_page),

    # 显示BMS信息
    path('bms/', bms.urls),

    # 显示PCS信息
    path('pcs/', redirect_to_zero_index),
    path('pcs/<int:pcs_sn>/', pcs.show_pcs_page),
    path('pcs/<int:pcs_sn>/yaotiao/', pcs.show_pcs_yaotiao_page),
    path('pcs/<int:pcs_sn>/yaokong/', pcs.show_pcs_yaokong_page),
    path('pcs/<int:pcs_sn>/grid/', pcs.show_pcs_grid),

    # 历史事件过滤
    # 全部历史记录
    path('history/all/', history.show_history_all_records),
    # 当前故障
    path('history/current/all/', history.show_current_all_errors),
    # 全部历史故障
    path('history/errors/all/', history.show_history_all_errors),
    # 全部历史事件
    path('history/events/all/', history.show_history_all_events),
    # 全部遥控历史事件
    path('history/events/yaokong/all/', history.show_history_all_yaokong_events),
    # 全部遥调历史事件
    path('history/events/yaotiao/all/', history.show_history_all_yaotiao_events),

    path('history/show/', history.show_history_error_detail),
    path('history/confirm/', history.show_history_error_confirm),

    path('history/test/', history.show_history_error_test),

    path('history/doc/', history.show_document),
    path('history/export/', history.export_history),

    # 采集器事件
    path('collector/record/<int:cid>/data/', collector.data_record),
    path('collector/create/', collector.create_collector),

    # 能量管理系统事件
    path('ems/', ems.show_ems_index),
    path('ems/settings/', ems.show_ems_single_settings),
    path('ems/options/', ems.show_ems_advance_options),
    path('ems/settings/save/', ems.save_ems_setings),
    path('ems/settings/json/', ems.show_ems_json_setings),

    # 采样信息时间
    path("sample/location/",sample.show_location_info),
    path("sample/analog/",sample.show_analog_info),

    # 空调
    path('air-conditioner/', air.show_all_list),
    path('air-conditioner/<int:aid>/', air.show_aircondition),

    # 报表
    path('report/system/', report.show_system_report),
    path('report/days/<str:start_times>/<str:end_times>/', report.system_report_export),
    path('pac.py', pac),

    #功率曲线
    path('power/grid/', bms.show_bms_grid),

    path('grid/', grid.urls),
    path("dev/", devel.urls)
]

