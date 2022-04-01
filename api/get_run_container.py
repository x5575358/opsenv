# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/25 10:04
# File  : get_run_container.py
# Software PyCharm

from api.open_api import bash


def get_container_list(src_str):
    ret_dict={}
    container_list=[]
    for o in src_str:
        dict_value_list=[]
        exce_order = "ansible %s -m shell  -a  \"docker ps\"\
        |egrep  -v \"SUCCESS\"|egrep  -v \"CONTAINER ID\"|grep -v '|'|awk -F \" \" \'{print $2}\'"%o
        print(exce_order)
        str_run_container = bash(exce_order)
        run_container = str_run_container.replace('\n',' ',len(str_run_container)).split(' ')
        if len(run_container) > 1:
            container_list=container_list+run_container[:len(run_container)-1]
            dict_value_list=dict_value_list+run_container[:len(run_container)-1]
            ret_dict.update(dict({o:dict_value_list}))
    return container_list,ret_dict


def list_trans_dict(src):
    ret_dict={}
    for key, values in src.items():
        for o in values:
            midd=o.split(':')
            print("-----list_trans_dict----midd----",midd)
            ret_dict.update(dict({midd[0]:[midd[1], key]}))
    return ret_dict

def compare_dict(src_dict,dest_dict):
    ret_src_dict={}
    ret_dest_dict={}
    ret_list = []
    for o in src_dict.keys():
        mid_values = list(src_dict[o])
        if o not in dest_dict.keys():
             ret_values = str(o)+":"+str(mid_values[0])
             ret_src_dict.update({ret_values:mid_values[1]})
        else:
            mid_dest_values = list(dest_dict[o])
            if mid_values[0] != mid_dest_values[0]:
                ret_dest_values = str(o)+":"+mid_dest_values[0]
                ret_src_values = str(o)+":"+str(mid_values[0])
                dest_dict_ret = {ret_dest_values:mid_dest_values[1]}
                src_dict_ret = {ret_src_values:mid_values[1]}
                mid_ret_list = []
                mid_ret_list.append(dest_dict_ret)
                mid_ret_list.append(src_dict_ret)
                ret_list.append(mid_ret_list)
    print("------ret_src_dict---------",ret_src_dict)
    print("--------ret_list-------",ret_list)
    return ret_src_dict,ret_list

