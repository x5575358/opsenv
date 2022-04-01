# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/26 16:59
# File  : tasks.py
# Software PyCharm

import time
from celery import task

@task(name="celery_demo.task")
def release_exec(src):
    print("release_exec")
    print("jobs[%s] is running "%src)
    print("++++++++++++++++++++++++++++++")
    result = True
    return result
