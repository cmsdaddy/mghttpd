# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os

# scada UI 服务器版本
__version__ = "ui-v1.1"

_current_dir_path = os.path.dirname(os.path.abspath(__file__))

# 项目根目录
project_dir_path = os.path.dirname(_current_dir_path)

# 项目配置文件根目录
profile_dir_path = project_dir_path + '/data'

# 项目文档存放目录
documents_dir_path = project_dir_path + '/doc'
