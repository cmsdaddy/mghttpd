# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os

# scada UI 服务器版本
__version__ = "ui-v1.1"


# 当前文件目录
_current_dir_path = os.path.dirname(os.path.abspath(__file__))
print("当前文件目录: {}".format(_current_dir_path))

# 项目根目录
project_dir_path = os.path.dirname(_current_dir_path)
print("项目根目录: {}".format(project_dir_path))

# 项目配置文件根目录
profile_dir_path = project_dir_path + '/data'
print("项目配置文件目录: {}".format(project_dir_path))

# 项目文档存放目录
documents_dir_path = project_dir_path + '/doc'
print("项目文档存放目录: {}".format(documents_dir_path))

# 日志文件存放目录
log_dir_path = os.path.dirname(project_dir_path) + '/log'
print("日志存放目录: {}".format(log_dir_path))
