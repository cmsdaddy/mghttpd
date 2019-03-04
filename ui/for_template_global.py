# -*- coding: utf8 -*-
import ui.mg as mg
from ui.models import *


# for template
def global_vars(request):
    content = dict()


    if len(request.GET) >= 1:
        for key, value in request.GET.items():
            if key == '蜂鸣器遥控点':
                success = mg.set_bee_yaokong(key, int(value), str(request.user))
                content['success'] = success
                break

    yaokong = mg.get_bee_yaokong()

    for name in yaokong:
        if name == '蜂鸣器遥控点':
            if yaokong[name] == 0:
                content['bee'] = 0
            elif yaokong[name] == 1:
                content['bee'] = 1

    if request.path.find("/settings") >= 0:
        content['pageclass'] = 'settings'
    else:
        content['pageclass'] = 'normal'

    content['bms_count'] = mg.get_bms_count()
    content['bms_id_list'] = [x for x in range(mg.get_bms_count())]
    content['pcs_count'] = mg.get_pcs_count()
    content["pcs_id_list"] = [x for x in range(mg.get_pcs_count())]
    content["air_count"] = mg.get_aircondition_count()

    content['current_errors_count'] = CurrentError.objects.filter(elevel__lte=1).count()
    content['current_warnings_count'] = CurrentError.objects.filter(elevel=2).count()
    content['current_messages_count'] = CurrentError.objects.filter(elevel=4).count()

    return content
