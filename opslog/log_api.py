# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/8 11:31
# File  : log_api.py
# Software PyCharm

import os
import stat
import logging

from Ops.settings import *
from mirrors.mirror_api import GetDayTime
from .models import *

def set_log(level, filename='ops.log'):
    """
    return a log file object
    """
    log_file = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(log_file):
        # os.mknod(log_file,mode=0777)
        # os.chmod(log_file, )
        mk_file(filename)
    log_level_total = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARN, 'error': logging.ERROR,
                       'critical': logging.CRITICAL}
    logger_f = logging.getLogger('ops')
    logger_f.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    print(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger_f.addHandler(fh)
    return logger_f



def mk_file(filename):
    with open(filename,"w") as f:
        f.close()


#add exe log
def create_execLog(**kwargs):
    user = kwargs.pop("user")
    host=kwargs.pop("host")
    cmd=kwargs.pop("cmd")
    remote_ip=kwargs.pop("remote_ip")
    result=kwargs.pop("result")
    op_time=kwargs.pop("op_time")
    try:
        ExecLog.objects.create(user=user,host=host,cmd=cmd,remote_ip=remote_ip,result=result,datetime=op_time)
    except Exception as err:
        print(err)

#get client ip
def request_client_ip(request):
    #remote_ip = request.META["REMOTE_HOST"]
    #if remote_ip == "":
    remote_ip = request.META["REMOTE_ADDR"]
    return remote_ip
#    return  ""

def execlog_log_list():
    GT = GetDayTime()
    THREE_DAY_AGO = GT.get_pre_later_time(-3, "%Y-%m-%d %H:%M:%S")
    return  ExecLog.objects.filter(create_time__gt=THREE_DAY_AGO).values("id", "user", "cmd", \
            "remote_ip", "log_level", "create_time").order_by("-id")

logger = set_log(LOG_LEVEL)
