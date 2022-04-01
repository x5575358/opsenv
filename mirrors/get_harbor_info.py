# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/11 15:08
# File  : open_api.py
# Software PyCharm

from Ops.settings import MIRROR_WAREHOUSE
from api.open_api import bash

ret = bash(MIRROR_WAREHOUSE)
print(ret)
