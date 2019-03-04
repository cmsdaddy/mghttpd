# -*- coding: utf8 -*-
import sys
import time
import json
import urllib.request, urllib.parse
import threading
import re
import time


api_host = '192.168.2.106:8083'
root = '/v1.0/realtime'
www_host = '127.0.0.1:8000'


# 合并一个范围内的整数
# 1,2,3,4,5 --> ['1-5']
# 1,2,3,6,7 --> ['1-3', '6,7']
def merge_range(iterable_object):
    # 从小到大排序
    sorted(iterable_object)

    # 长度小于5个
    if len(iterable_object) <= 5:
        return [",".join([str(x) for x in iterable_object])]


# 监听BMS电池组历史信息
def listen_bms_group_history(bms_id, group_id):
    # 5号电池电压_下限重度告警状态_1
    # 18#从控失联_电池组各项告警_1
    type1 = re.compile(r'^(\d+)([^\d]+)(\d+)')
    type2 = re.compile(r'^([^\d]+)(\d+)([^\d]+)(\d)')
    # 电池组各项告警_组端电压下限中度告警_1
    type3 = re.compile(r'^([^\d]+)(\d)')

    X = {}

    event_list = []

    '''
    for key in (
                '5号电池电压_下限重度告警状态_1',
                '6号电池电压_下限重度告警状态_1',
                '7号电池电压_下限重度告警状态_1',
                '6号电池电压_下限重度告警状态_1',
                '7号电池电压_下限重度告警状态_1',
                '电池组各项告警_从控18#失联_1',
                '电池组各项告警_组端电压下限中度告警_1',
                '5号电池电压_下限重度告警状态_0',
                '6号电池电压_下限重度告警状态_0',
                '7号电池电压_下限重度告警状态_0',
                '5号电池电压_下限重度告警状态_1',
                '6号电池电压_下限重度告警状态_1',
                '7号电池电压_下限重度告警状态_1',
                '6号电池电压_下限重度告警状态_1',
                '7号电池电压_下限重度告警状态_1',
    ):
    '''
    while True:
        url = 'http://' + api_host + root + urllib.parse.quote('/BMS数据块/1/BCMU遥信信息/0/BCMU遥信故障告警') + "?wait=-1"
        handle = urllib.request.urlopen(url)
        txt = handle.read()
        data = json.loads(txt.decode('utf8'))
        key = data['data']
        if type1.match(key) is not None:
            idx, txt, value = type1.subn(r'\1 \2 \3', key)[0].split(' ')
            idx, value = int(idx), int(value)

            try:
                #print(txt, idx, value)
                if value == 0 and idx in X[txt]:
                    X[txt].remove(idx)
                elif value != 0 and -idx in X[txt]:
                    X[txt].remove(-idx)

                if value == 0 and -idx not in X[txt]:
                    print(idx, txt, "++++++恢复++++++")
                    X[txt].add(-idx)

                    event_list.append((str(idx)+txt+"恢复"))
                elif value != 0 and idx not in X[txt]:
                    print(idx, txt, "------产生------")
                    X[txt].add(idx)

                    event_list.append((str(idx)+txt+"产生"))
            except:
                if value == 0:
                    X[txt] = set([-idx])
                    print(idx, txt, "++++++恢复++++++")

                    event_list.append((str(idx)+txt+"恢复"))
                else:
                    X[txt] = set([idx])
                    print(idx, txt, "------产生------")

                    event_list.append((str(idx)+txt+"产生"))
        elif type2.match(key) is not None:
            idx, txt, name, value = type2.subn(r'\1 \2 \3 \4', key)[0].split(' ')
            #print(txt, idx, value)
        elif type3.match(key) is not None:
            txt, value = type3.subn(r'\1 \2', key)[0].split(' ')
            X[txt] = value
            #print(txt, value)
        else:
            #print(key)
            x = None

    for evt in event_list:
        print(evt)



# 监听BMS历史信息
def listen_bms_history(bms_id):
    pass


listen_bms_group_history(0, 0)

