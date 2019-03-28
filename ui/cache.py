# -*- coding: utf8 -*-
import redis
import json
import uuid
from datetime import datetime
import ui.cache_path as cpath


pool = redis.ConnectionPool(host='192.168.1.107', port=6379)


def get_now_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


class GraphicPreviewCache(object):
    def __init__(self):
        self.r = redis.Redis(connection_pool=pool, db=4)

    def set(self, str_obj, ex=None):
        if ex is None:
            ex = 300 # 5 min

        v_key = str(uuid.uuid4())
        path = cpath.redis_path_of_graphic_preview(v_key)
        self.r.set(name=path, value=str_obj, ex=ex)

        return str(v_key)

    def get(self, v_key):
        path = cpath.redis_path_of_graphic_preview(v_key)
        result = self.r.get(name=path)
        try:
            return json.loads(result.decode())
        except:
            return None


class BatterySingleVoltageCache(object):
    def __init__(self):
        self.r = redis.Redis(connection_pool=pool, db=4)

    def set(self, heap_id, group_id, voltage_array, ex=None):
        if ex is None:
            ex = 300 # 5 min

        pack = {
            'payload': voltage_array,
            'tsp': get_now_time_str()
        }
        cache_path = json.dumps(pack, ensure_ascii=False)

        path = cpath.redis_path_of_battery_single_voltage(heap_id, group_id)
        self.r.set(name=path, value=cache_path, ex=ex)

    def get(self, heap_id, group_id):
        path = cpath.redis_path_of_battery_single_voltage(heap_id, group_id)
        result = self.r.get(name=path)
        try:
            cache_pack = json.loads(result.decode())
            return cache_pack['payload']
        except:
            return None
