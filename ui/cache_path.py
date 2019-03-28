# -*- coding: utf8 -*-

REDIS_DIVIDER = ':'
OBJ_BMS = 'bms'
OBJ_HEAP = 'heap'
OBJ_BATTERY = 'battery'
OBJ_GROUP = 'group'
OBJ_SCADA = 'SCADA'
OBJ_PCS = 'PCS'
OBJ_EMS = 'EMS'
OBJ_YC = 'yc'
OBJ_YX = 'yx'


def redis_path_of_graphic_preview(v_key):
    return REDIS_DIVIDER.join(['graphic', 'preview', v_key])


# return battery:heap:<heap_id>:group:<group_id>
def redis_path_of_battery_single_information(heap_id, group_id):
    return REDIS_DIVIDER.join([OBJ_BATTERY, OBJ_HEAP, str(heap_id), OBJ_GROUP, str(group_id)])


# return battery:heap:<heap_id>:group:<group_id>:voltage ==> [int x100 list]
def redis_path_of_battery_single_voltage(heap_id, group_id):
    return REDIS_DIVIDER.join([redis_path_of_battery_single_information(heap_id, group_id), 'voltage'])


# return battery:heap:<heap_id>:group:<group_id>:temperature ==> [int x100 list]
def redis_path_of_battery_single_temperature(heap_id, group_id):
    return REDIS_DIVIDER.join([redis_path_of_battery_single_information(heap_id, group_id), 'temperature'])


# return battery:heap:<heap_id>:group:<group_id>:soc ==> [int x100 list]
def redis_path_of_battery_single_soc(heap_id, group_id):
    return REDIS_DIVIDER.join([redis_path_of_battery_single_information(heap_id, group_id), 'soc'])


# return battery:heap:<heap_id>:group:<group_id>:soh ==> [int x100 list]
def redis_path_of_battery_single_soh(heap_id, group_id):
    return REDIS_DIVIDER.join([redis_path_of_battery_single_information(heap_id, group_id), 'soh'])
