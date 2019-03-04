# -*- coding: utf8 -*-
import codecs
import json


class ConfigureItem(object):
    def __init__(self, **args):
        print(args)


class ConfigureText(ConfigureItem):
    def __init__(self, **args):
        super(ConfigureText, self).__init__(**args)


class ConfigureInterger(ConfigureItem):
    def __init__(self, **args):
        super(ConfigureInterger, self).__init__(**args)


class ConfigureFloat(ConfigureItem):
    def __init__(self, **args):
        super(ConfigureFloat, self).__init__(**args)


class ConfigureSelect(ConfigureItem):
    def __init__(self, **args):
        super(ConfigureSelect, self).__init__(**args)


class ConfigureRadio(ConfigureItem):
    def __init__(self, **args):
        super(ConfigureRadio, self).__init__(**args)


# 参数配置组，组中的参数必须放置在一个组类
class ConfigureGroup:
    def __init__(self):
        pass


# 配置页
class ConfigurePage:
    def __init__(self, path):
        self.path = path
        self.configure_file_path = "data/configure/" + path.replace('/', '_') + ".json"

    # 从配置文件中加载配置数据表
    def _load(self):
        single_items_list = group_items_list = configure_page_title = value_maps_list = None

        with codecs.open(self.configure_file_path, 'r', encoding='utf8') as file:
            jobjs = json.load(file)

            try:
                single_items_list = jobjs['single_items_list']
            except:
                single_items_list = list()

            try:
                value_maps_list = jobjs['value_maps_list']
            except:
                value_maps_list = dict()

            try:
                group_items_list = jobjs['group_items_list']
            except:
                group_items_list = list()

            try:
                configure_page_title = jobjs['configure_page_title']
            except:
                configure_page_title = "配置页"

        self.single_items_list = single_items_list
        self.group_items_list = group_items_list
        self.configure_page_title = configure_page_title
        self.value_maps_list = value_maps_list

