# -*- coding: utf8 -*-
import ui.mg as mg
from ui.models import *
import datetime
import ui.page_linux as linux
import codecs
import os
import ui.scada as scada


try:
    profile_dir = scada.project_dir_path + '/data'
    logo_title_file_path = profile_dir + '/logo-title.txt'
    with codecs.open(logo_title_file_path, encoding='utf8') as file:
        logo_title = file.read().rstrip()
except:
    logo_title = 'SCADA'


# for template
def global_vars(request):
    content = dict()

    login_list = linux.get_login_on_display_list()
    if len(login_list):
        request.user = login_list[0]
    else:
        # keep django anonymous user
        pass

    if request.path.find("/settings") >= 0:
        content['pageclass'] = 'settings'
    else:
        content['pageclass'] = 'normal'

    content["theme"] = 'default'
    content['logo_title'] = logo_title

    content['bms_count'] = mg.get_bms_count()
    content['bms_id_list'] = [x for x in range(mg.get_bms_count())]
    content['pcs_count'] = mg.get_pcs_count()
    content["pcs_id_list"] = [x for x in range(mg.get_pcs_count())]
    content["air_count"] = mg.get_aircondition_count()

    content['current_errors_count'] = CurrentError.objects.filter(elevel__lte=1).count()
    content['current_warnings_count'] = CurrentError.objects.filter(elevel=2).count()
    content['current_messages_count'] = CurrentError.objects.filter(elevel=4).count()

    content['system_launch_datetime'] = datetime.datetime.strptime("2019-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    content['hour_segments'] = [str(x) for x in range(24)]
    content['select_durations'] = [
        "1-Hour",
        "5-Hours",
        "8-Hours",
        "10-Hours",
        "15-Hours",
        "20-Hours",
        "1-Day",
        "2-Days",
        "5-Days",
        "1-Week",
        "2-Weeks",
        "4-Weeks",
    ]
    content['project_dir_path'] = scada.profile_dir_path
    content['profile_dir_path'] = scada.profile_dir_path
    content['documents_dir_path'] = scada.documents_dir_path
    content['log_dir_path'] = scada.log_dir_path

    content['system_name'] = scada.system_name
    content['server_version'] = scada.__version__
    return content
