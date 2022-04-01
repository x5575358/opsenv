# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/9/26 16:17
# File  : opstools_api.py
# Software PyCharm

from celery import task
from api.open_api import bash, write_file
from .models import ScriptGroupRelease
from mirrors.mirror_api import GetDayTime
from Ops.settings import LOCAL_VISTOR_IP
import os

@task
def async_exec_script_group(log_file_path, dest_host, script_tag, src_path_list, \
                            src_file_list, dest_file_path, auto_create_script):
    '''
    :param log_file_path:
    :param dest_host:
    :param script_tag:
    :param src_path_list:
    :param src_file_list: the queue of the script exce
    :param dest_file_path:
    :return:
    '''
    # (file_path, hosts_name, tags, src_path_list, src_file_list, DEST_FILE_PATH)
    GT = GetDayTime()
    NOW_TIME = GT.get_now_time("%Y-%m-%d %H:%M:%S")
    if not check_network(log_file_path ,dest_host):
        ScriptGroupRelease.objects.filter(group_uniqu_tag=\
                            script_tag).update(update_time=NOW_TIME, release_status=2)
        return
    write_file("检查远端是否存在功能组脚本.\n",log_file_path)
    check_file_isornot_exit(dest_host, log_file_path, src_path_list, src_file_list, dest_file_path)
    write_file("执行功能组脚本123.\n", log_file_path)
    write_file(dest_file_path, log_file_path)
    write_file(auto_create_script, log_file_path)
    dest_exce_file_path = os.path.join(dest_file_path, auto_create_script)
    exce_order = "ansible %s -m raw -a \"sh %s\""%(dest_host, dest_exce_file_path)
    write_file("-----开始执行功能组脚本----\n", log_file_path)
    write_file(exce_order, log_file_path)
    bash(exce_order)
    write_file("-----执行完功能组脚本----\n", log_file_path)
    

def check_network(log_file, hosts):
    cmd = "ansible -m ping %s" % hosts
    ret_content = bash(cmd)
    write_file("-----网络检查----\n", log_file)
    write_file(ret_content, log_file)
    if "UNREACHABLE" in ret_content:
        ret = False
    elif "SUCCESS" in ret_content:
        ret = True
    else:
        ret = False
    return ret

def check_file_isornot_exit(dest_host, log_file, src_path_list, src_file_list, dest_file_abs_path):
    '''
    脚本文件不允许重名传入ops平台，一旦传入平台不允许多个不同脚本同时使用
    :param dest_host:
    :param log_file:
    :param src_path_list:
    :param src_file_list:
    :param dest_file_abs_path:
    :return:
    '''
    cmd = "ansible %s -a \"ls %s\""%(dest_host, dest_file_abs_path)
    write_file("-----目标主机文件检查----\n", log_file)
    ret = bash(cmd)
    write_file(ret, log_file)
    write_file(src_file_list, log_file)
    for mid_nb in range(len(src_file_list)):
        if src_file_list[mid_nb] not in ret:
            write_file("-----拷贝%s文件到远端服务器----\n"%mid_nb, log_file)
            write_file("-----拷贝%s文件到远端服务器----\n"%src_file_list, log_file)
            copy_cmd ="ansible %s -m copy -a \"src=%s dest=%s backup=yes \n\""%(\
                dest_host, src_path_list[mid_nb], dest_file_abs_path)
            write_file("-----拷贝命令为：\t%s----"%copy_cmd, log_file)
            bash(copy_cmd)


def auto_create_exce_group_script(function_scriptlist, save_file_abs_path, group_tag, log_file, dest_path):
    write_file("#!bin/bash\nPY_ORDER=`which python`\nSH_ORDER=`which sh`\n\
              HTTP_ORDER=`which http`\nif [ $? -ne 0 ];then\n\tsudo yum install httpie -y\nfi\n", save_file_abs_path)
    try:
        for sc_file in function_scriptlist:
            file_abs_path = os.path.join(dest_path, sc_file) 
            if sc_file.endswith(".py"):
                write_file("${PY_ORDER} %s\n"%file_abs_path, save_file_abs_path)
            elif sc_file.endswith(".sh"):
                write_file("${SH_ORDER} %s\nret_code=2\nif [ $? -eq 0 ];then\nret_code=1\nfi\n" %file_abs_path, save_file_abs_path)
    #    RET_STATUS_ORDER = "curl -H  \"Content-Type:application/json\" -X \
    #    POST -d '{\"group_tag\":%s, \"ret\":1}' %s"%(group_tag, os.path.join(LOCAL_VISTOR_IP, \
     #   "opstools/async_exce_script_ret"))
        RET_STATUS_ORDER ="${HTTP_ORDER} -f POST %s  group_tag:='%s' ret:=$ret_code"%(os.path.join(LOCAL_VISTOR_IP,\
                        "opstools/async_exce_script_ret"), group_tag)
        write_file(RET_STATUS_ORDER , save_file_abs_path)
    except:
        write_file("自动创建执行%s脚本失败.\n"%save_file_abs_path, log_file)
        return False
    write_file("自动创建执行%s脚本成功.\n" % save_file_abs_path, log_file)
    return True
