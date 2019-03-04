# -*- coding: utf8 -*-
import sys
import time
import json
import urllib.request, urllib.parse
import threading


api_host = '192.168.2.110:8083'
root = '/v1.0/realtime'
www_host = '127.0.0.1:8000'


# API模型
class Api:
    def __init__(self, id, access_path, ref, k, b, mask, dot):
        self.id, self.access_path, self.ref = id, access_path, ref
        self.k, self.b, self.mask, self.dot = k, b, mask, dot
        self.value = "0"

    def path(self):
        return self.access_path

    def parent_path(self):
        idx = self.access_path.rfind('/')
        return self.access_path[:idx]

    def index(self):
        idx = self.access_path.rfind('/') + 1
        try:
            return int(self.access_path[idx:])
        except:
            return self.access_path[idx:]

    def setvalue(self, value):
        value_type = type(value)

        if value_type == type(''):
            self.value = value
        elif value_type == type(1):
            fmt = "%%.%df" % self.dot
            self.value = fmt % ((value & self.mask) * self.k + self.b)
        elif value_type == type([]) and len(value) > 0 and type(value[0]) == type(1):
            fmt = "%%.%df" % self.dot
            self.value = json.dumps([fmt % ((x & self.mask) * self.k + self.b) for x in value])
        else:
            self.value = json.dumps(value)

    def postvalue(self):
        return [self.id, self.value]


# API分组
class ApiGroup:
    def __init__(self, listen_path):
        self.api_list = {}
        # 这个分组的监听路径
        self.listen_path = listen_path

    def append(self, api):
        self.api_list[api.index()] = api

    def path(self):
        return self.listen_path

    def make_post_form(self):
        form = []
        for _, api in self.api_list.items():
            form.append(api.postvalue())
        return form

    def __setitem__(self, key, value):
        try:
            self.api_list[ key ].setvalue(value)
        except Exception as e:
            print(e)


# 从www_host获取采集器数据信息
def fetch_collectors(host):
    url = 'http://' + host + '/collector/collector.json'
    handle = urllib.request.urlopen(url)
    txt = handle.read()
    collectors = json.loads(txt.decode('utf8'))
    c_list = []
    for c in collectors:
        api = Api(c['id'], c['access_path'], c['ref'], c['k'], c['b'], c['mask'], c['dot'])
        c_list.append(api)
    return c_list


# 将获取到的API按照相同父节点进行分组
def fetch_api_groups(collector_list):
    api_group = {}

    for x in collector_list:
        try:
            api_group[x.parent_path()].append(x)
        except:
            group = ApiGroup(x.parent_path())
            group.append(x)
            api_group[x.parent_path()] = group

    return [group for _, group in api_group.items()]


c = fetch_collectors(www_host)
api_joined_group = fetch_api_groups(c)


# 组监听函数
def api_query_forever(www, api, group):
    www_url = u'http://' + www + u'/collector/record/'
    wait_in_seconds = 10 # 30min
    api_url = u'http://' + api + root + urllib.parse.quote(group.path()) + u'?visitor=collector&wait=%d' % wait_in_seconds
    try:
        print("listen url:", urllib.parse.unquote(api_url))
        while True:
            handle = urllib.request.urlopen(api_url)
            jobj_origin = handle.read()
            jobj = jobj_origin.decode('utf8')
            jobj_json = json.loads(jobj)
            if jobj_json['status'] != u'ok':
                break

            for idx in jobj_json['data']:
                group[ idx ] = jobj_json['data'][idx]

            post_data = group.make_post_form()
            post_form_json = json.dumps({'tsp': time.strftime("%Y-%m-%d %H:%M:%S"), 'data': post_data})
            print("POST:", post_form_json)
            handle = urllib.request.urlopen(www_url, ("data="+post_form_json).encode('utf8'))
            handle.read()

    except Exception as e:
        print("**", e)

    print("poll thread terminated du to data crash!")


first = api_joined_group.pop()
for g in api_joined_group:
    th = threading.Thread(target=api_query_forever, name=g.path(), args=(www_host, api_host, g,))
    th.start()

api_query_forever(www_host, api_host, first)
