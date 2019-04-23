# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os
import platform

# scada UI 服务器版本
__version__ = "v1.1 beta"

# 系统名称
system_name = platform.system().lower()


# 当前文件目录
_current_dir_path = os.path.dirname(os.path.abspath(__file__))
print("当前文件目录: {}".format(_current_dir_path, 0o777))

# 项目根目录
project_dir_path = os.path.dirname(_current_dir_path)
print("项目根目录: {}".format(project_dir_path, 0o777))

# 项目配置文件根目录
profile_dir_path = project_dir_path + '/data'
print("项目配置文件目录: {}".format(project_dir_path))
if not os.path.exists(profile_dir_path):
    os.mkdir(profile_dir_path, 0o777)


# 项目文档存放目录
documents_dir_path = project_dir_path + '/doc'
print("项目文档存放目录: {}".format(documents_dir_path))
if not os.path.exists(documents_dir_path):
    os.mkdir(documents_dir_path, 0o777)

# 日志文件存放目录
log_dir_path = os.path.dirname(project_dir_path) + '/log'
print("日志存放目录: {}".format(log_dir_path))
if not os.path.exists(log_dir_path):
    os.mkdir(log_dir_path, 0o777)

# 回收站目录
trash_dir_path = profile_dir_path + '/.trash'
print("回收站目录: {}".format(trash_dir_path))
if not os.path.exists(trash_dir_path):
    os.mkdir(trash_dir_path, 0o777)

# 静态文件存放目录
static_dir_path = _current_dir_path + '/static'
print("静态文件存放目录: {}".format(static_dir_path))

# 一次图方案静态资源存放根目录
linkage_source_path = static_dir_path + '/linkage'
print("一次图方案静态资源存放根目录: {}".format(linkage_source_path))
if not os.path.exists(linkage_source_path):
    os.mkdir(linkage_source_path, 0o777)
