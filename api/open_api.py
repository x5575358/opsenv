# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/11 15:01
# File  : q.py
# Software PyCharm

import os
import time
import socket
import pymysql
from .models import AsyncOperationAudit
from Ops.settings import ANSY_RET_DIR
from  mchange.models import ChangeRecorder

def bash(cmd):
    """
    run a bash shell command
    执行bash命令
    """
    return os.popen(cmd).read()

def get_server_ip():
    try:
        socket_handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_handle.connect(('8.8.8.8', 80))
        server_ip = socket_handle.getsockname()[0]
    finally:
        socket_handle.close()
    return server_ip

def async_restart_container(src_hosts,src_file_path, src_file_name, dest_path):
    ip = get_server_ip()
    cmd_order = "sudo ansible  %s -m copy -a \"src=%s dest=%s\""%(src_hosts, src_file_path, dest_path)
    dest_file_path = os.path.join(dest_path,src_file_name)
    start_remote_exce = "ansible %s -a \"/home/ec2-user/upfile/opsserver/call_restart.sh %s %s %s\""%(\
                        src_hosts, src_file_name, dest_file_path, ip)
    ret = bash(cmd_order)
    print("----------ret==-------",ret)
    ret_w = bash(start_remote_exce)
    print("----------ret_w-------",ret_w)


def bash_exce_list(ip,user,pk,cmd_list):
    """
    run a bash shell command
    执行bash命令
    """
    ret_list=[]
    for cmd in cmd_list:
        ret=os.popen(cmd).read()
        ret_list.append(ret)
        file_name=str(pk)+"_"+str(time.time()).replace(".","")+".log"
        file_path_name = os.path.join(ANSY_RET_DIR, file_name)
        status=ansible_result_status(ret)
        write_file(ret,file_path_name)
        ChangeRecorder.objects.filter(pk=pk).update(change_status=0)
        AsyncOperationAudit.objects.create(exce_order=cmd,file_name=file_name,remote_ip=ip,user=user,\
                                           file_path=file_path_name,unique_code=pk,release_status=status)
    return ret_list


class DbOperator:
    def __init__(self,DB_HOST,DB_DATABASE,DB_PORT,DB_USER,DB_PASSWORD):
        self.db = pymysql.connect(host=DB_HOST,user=DB_USER,password=DB_PASSWORD,database=DB_DATABASE, port=DB_PORT)

    def query_result(self,param):
        try:
            cur = self.db.cursor()
            cur.execute(param)
            results = cur.fetchall()
            return results
        except Exception as e:
            raise e
            return "error"

    def update_or_delete_param(self,param):
        try:
#            print(param)
            cur = self.db.cursor()
            cur.execute(param)
            self.db.commit()
        except Exception as e:
            self.db.rollback()

    def close_db(self):
        self.db.close()

def read_file(filename):
    if os.path.exists(filename):
        with open(filename,'r') as f:
            return  f.read()
    else:
        return  "%s文件不存在"%filename

def write_file(src,filename):
    with open(filename, 'a') as f:
        f.writelines(src)
    #    print(src)
     #   print(type(src))
      #  print("--------------src----en-----")
    return True

def ansible_result_status(ret):
    if "SUCCESS" in ret:
        return 0
    else:
        return 1

def dict_add_serial_number(src_dict):
    cnt = 1
    for  o  in src_dict:
        o.update({'only_sign': '%8d' % cnt})
        cnt = cnt + 1
    return src_dict
