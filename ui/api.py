# -*- coding: utf8 -*-
from urllib.request import *
import urllib
import urllib.parse
import json


# 从数据中心读取数据
def api_read(host_address, path, visitor=None, wait=None):
    if visitor is None:
        visitor = 'UI'
    return None

    quoted_path = urllib.parse.quote(path)
    url = "".join(['http://', host_address, quoted_path, '?', "visitor=", visitor])
    print("api read:", url)
    try:
        handle = urlopen(url)
        txt_bytes = handle.read()
        txt = txt_bytes.decode('utf8')
        txt_json = json.loads(txt)
    except Exception as e:
        print(e)
        return None

    if txt_json['status'] != 'ok':
        return None

    return txt_json['data']


# 向数据中心写数据
def api_write(host_address, path, data, visitor=None, wait=None):
    if visitor is None:
        visitor = 'UI'

    quoted_path = urllib.parse.quote(path)
    url = "".join(['http://', host_address, quoted_path, '?', "visitor=", visitor])
    print("api write:", url)
    try:
        data = json.dumps(data).encode('utf8')
        request = Request(url=url, data=data, method="POST")
        request.add_header("Content-Type", "application/json")
        respons = urlopen(request)
        txt_bytes = respons.read()
        txt = txt_bytes.decode('utf8')
        txt_json = json.loads(txt)
    except Exception as e:
        print(e)
        return False

    if txt_json['status'] != 'ok':
        print(txt_bytes.decode('utf8'))
        return False

    return True

