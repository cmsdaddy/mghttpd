# -*- coding: utf8 -*-

import os
import time
import csv
import sys
import re
import urllib2
import json
import codecs


if len(sys.argv) != 3:
    print('Usage: %s host root' % sys.argv[0])
    exit(-1)

host, root = sys.argv[1], sys.argv[2]


def read_bms(host, root, idx):
    uri = 'http://' + host + root + '/BMS数据块/%d' % idx
    print(uri)
    request = urllib2.urlopen(uri)
    obj = json.loads(request.read())
    return obj['data'] if obj['status'] == 'ok' else None


def get_lazy_format_and_unit(key):
    if key.find(u"ID") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u''
    elif key.find(u"ID号") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u''
    elif key.find(u"组号") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u''
    elif key.find(u"编号") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"字符串"
        unit = u''
    elif key.find(u"序号") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"字符串"
        unit = u''
    elif key.find(u"电量") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'kw.H'
    elif key.find(u"容量") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = 'A.h'
    elif key.find(u"电压") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'V'
    elif key.find(u"电流") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'A'
    elif key.find(u"温度") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'℃'
    elif key.find(u"SOC") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'%'
    elif key.find(u"SOH") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'%'
    elif key.find(u"节数") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'节'
    elif key.find(u"组数") >= 0:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u'组'
    else:
        k, b, mask, dot, _t = 1.0, 0.0, '0x7fffffff', 0, u"数字"
        unit = u''
    return k, b, mask, dot, unit, _t



def save_bms(bmsid, data):
    file_name = u'BMS-%d遥测信息.csv' % bmsid
    with codecs.open(file_name, "wb", "utf8") as csvfile:
        csvfile.write(",".join(['fullname','shortname','path','k','b','mask','dot','unit','type','records\n']))
        for key in data[u'BMS遥测信息']:
            k, b, mask, dot, unit, _t = get_lazy_format_and_unit(key)
            x = u",".join([u"%d#BMS-%s" % (bmsid+1, key), key, u"/BMS数据块/%d/BMS遥测信息/%s" % (bmsid, key), str(k), str(b), str(mask), str(dot), unit, _t, "1\n"])
            csvfile.write(x)

    
    for idx in xrange(len(data[u'BCMU遥测信息'])):
        file_name = u'BMS-%d-BCMU-%d遥测信息.csv' % (bmsid, idx)
        with codecs.open(file_name, "wb", "utf8") as csvfile:
            csvfile.write(",".join(['fullname','shortname','path','k','b','mask','dot','unit','type','records\n']))
            for key in data[u'BCMU遥测信息'][idx]:
                k, b, mask, dot, unit, _t = get_lazy_format_and_unit(key)
                x = u",".join([u"%d#BMS-%s" % (bmsid+1, key), key, u"/BMS数据块/%d/BCMU遥测信息/%d/%s" % (bmsid, idx, key), str(k), str(b), str(mask), str(dot), unit, _t, "1\n"])
                csvfile.write(x)


for idx in range(0, 1):
    bms = read_bms(host, root, idx)
    if bms is None:
        print("bms", idx, "fetch failed from", host, root)
    else:
        save_bms(idx, bms)



