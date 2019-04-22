# -*- coding: utf8 -*-

# 系统框图模型处理文件


class BaseUnit(object):
    """基础模型单元"""
    def __init__(self, name, width=None, height=None):
        self.name = name
        if width is None:
            width = 100
        if height is None:
            height = 100

        self.width, self.height = width, height