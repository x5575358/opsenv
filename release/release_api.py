# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/27 10:46
# File  : release_api.py
# Software PyCharm
# import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_name.settings")# project_name 项目名称
# django.setup()
import os
import time
import json
import operator 
from celery import task
from api.open_api import bash, write_file, bash_exce_list
from mirrors.mirror_api import GetDayTime
from .models import *
from Ops.settings import JSON_DATA_DIR, HARBOR_NAME, HARBOR_PASSWD
from opslog.log_api import  logger
from mchange.models import ChangeRecorder

import docker
from pprint  import pprint

@task
def release_async_bash_exec(src_info, file_path, ip, pk, task_id, warehouse_tags, exec_head):
    GT = GetDayTime()
    NOW_DAY = GT.get_now_time("%Y-%m-%d %H:%M:%S")
    retinfo = bash(src_info)
    write_file(retinfo, file_path)
    end_word = "to %s closed."%ip
    print("--------retinfo---start--------\n%s"%retinfo)
    print("--------retinfo-end----------")
    if end_word in retinfo and "SUCCESS" in retinfo:
        print("------inin9inini-------------------")
        if "cat " in src_info:
            AffirmInfo.objects.filter(pk=pk).update(release_status=0)
            TaskInfo.objects.filter(pk=task_id).update(release_status=0, update_time=NOW_DAY)
            AsyncRecord.objects.filter(file_path=file_path).update(release_status=0, update_time=NOW_DAY)
        else:
            process_scanf = exec_head+"\"docker ps\"|grep %s"%warehouse_tags+"|wc -l"
            print(process_scanf)
            ret = bash(process_scanf)
            print("---------ret---------------------")
            print(ret)
            print(type(ret))
            print("---------ret-------------end---")
            if operator.gt(ret, str("0")):
                AffirmInfo.objects.filter(pk=pk).update(release_status=0)
                TaskInfo.objects.filter(pk=task_id).update(release_status=0, update_time=NOW_DAY)
                AsyncRecord.objects.filter(file_path=file_path).update(release_status=0, update_time=NOW_DAY)
            else:
                AffirmInfo.objects.filter(pk=pk).update(release_status=1)
                TaskInfo.objects.filter(pk=task_id).update(release_status=4, update_time=NOW_DAY)
                AsyncRecord.objects.filter(file_path=file_path).update(release_status=1, update_time=NOW_DAY)
    else:
        AffirmInfo.objects.filter(pk=pk).update(release_status=1)
        TaskInfo.objects.filter(pk=task_id).update(release_status=4, update_time=NOW_DAY)
        AsyncRecord.objects.filter(file_path=file_path).update(release_status=1, update_time=NOW_DAY)

    result = True
    return result

@task
def release_async_bash(src_info):
    bash(src_info)
    result = True
    return result
@task
def list_async_bash(src_list):
    bash_exce_list(src_list)
    result = True
    return result

@task
def async_list_bash(ip, user, pk, src):
    bash_exce_list(ip, user, pk, src)
    result = True
    return result

@task
def async_sealing_version(remote_ip, src_image, dest_image, version, unique_id, dest_image_version):
    docker_handle = DockerRemoteApi()
    docker_handle.by_image_to_tag_push(remote_ip, src_image, dest_image, version)
    ChangeRecorder.objects.filter(unique_tags=unique_id, after_warehouse_tags=dest_image_version).update(change_status=0)
    return True

def wirte_file(dest_path, data, flag=""):
    with open(dest_path,'a') as f:
        if flag == "D":
            for item, value in data.items():
                f.write("%s\n"%item)
                f.write("%s\n"%value)
        elif flag == "L":
            for value in data:
                f.write("%s"%value)
        else:
            f.write(data)

def update_ansible_host_file(last_json_id, need_add_data, need_object, add_user):
    logger.debug("-----------update_ansible_host_file--in-------------")
    name = str(time.time()).replace(".","")+".json"
    dest_file_path = "/etc/ansible/hosts"
    dest_json_file_path = os.path.join(JSON_DATA_DIR, name) 
    if last_json_id:
        logger.debug("len gt 0----->>>>type(last_json_id)===%s>>>last_json_id==%s"%(type(last_json_id), last_json_id))
        obj = AnsibleHostFile.objects.filter(relate_hostifo_key__id=last_json_id).values("json_file_path", "json_file_name")
        logger.debug("--obj--->>>>%s"%obj)
        json_file = os.path.join(obj[0]["json_file_path"], obj[0]["json_file_name"])
        data_dict = {}
        logger.debug("------json_file----%s"%json_file)
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                json_data = f.read()
                logger.debug("------json_data----------", json_data)
                data_dict.update(json.loads(json_data))
                logger.debug("------data_dict----------", data_dict)
        data_dict.update(need_add_data)
        logger.debug("------data_dict--end--------", data_dict)
        os.remove(dest_file_path)
        wirte_file(dest_file_path, data_dict, "D")
        wirte_file(dest_json_file_path, json.dumps(data_dict))
        logger.debug("-------st--AnsibleHostFile------------------")
        AnsibleHostFile.objects.create(relate_hostifo_key=need_object, json_file_name=name, add_user=add_user)
        logger.debug("-------ed--AnsibleHostFile------------------")
    else:
        logger.debug("-----delete-st--------")
        os.remove(dest_file_path)
        logger.debug("-----delete-ed--------")
        logger.debug("-----need_add_data--------%s"%need_add_data)
        wirte_file(dest_file_path, need_add_data, "D")
        logger.debug("-----write host file--------")
        wirte_file(dest_json_file_path, json.dumps(need_add_data))
        logger.debug("-----write json file--------")
        AnsibleHostFile.objects.create(relate_hostifo_key= need_object, json_file_name=name, add_user=add_user)

def read_cmp_delete_data(basic_data, cmp_file="/etc/ansible/hosts", dest_file="/etc/ansible/hosts"):
    logger.debug("-----read_cmp_delete_data--st------")
    st_flag = 0 
    ed_flag = 1
    list_json_data = []
    with open(cmp_file, 'r') as f:
        for line in f.readlines():
            mid_line = line.replace("[","").replace("]","").replace("\n","")
            logger.debug("-----line--%s--"%line, "----st_flag---%s-"%basic_data)
            if (mid_line != basic_data) and ((ed_flag-st_flag == 1) or (ed_flag-st_flag == 3)):
                list_json_data.append(line)
                st_flag = ed_flag 
                ed_flag = ed_flag + 1
            else:
                ed_flag = ed_flag + 1
    logger.debug("---write st---%s"%list_json_data)
    os.remove(dest_file)
    wirte_file(dest_file, list_json_data, flag="L")
    logger.debug("---write ed---")

class DockerRemoteApi:
    def docker_ps_list(self, remote_ip, ret_type):
        '''
        :param remote_ip: 操作服务器
        :param ret_type: list/dict
        :return: 
        '''
        container_list = []
        container_dict = {}
        try:
            url = "tcp://%s:2375"%remote_ip
            print("------url-------", url)
            client = docker.DockerClient(base_url=url)
            get_container_id_list = client.containers.list()
            for ids in get_container_id_list:
               # for version_name in ids.image.tags:
                version_name = ids.image.tags[0]
                pos = version_name.rfind("/")
                project_name = version_name[pos+1:]
                container_list.append(project_name)
                container_dict.update({project_name:ids.short_id})
            if ret_type == "dict":
                return container_dict
            elif ret_type == "list":
                return container_list
            else:
                return container_list
        except:
           print("-----error----")
           return container_list

    def get_run_container_list(self, remote_ip, host_name):
        print("---------get_run_container_list-------", remote_ip)
        st=time.time()
        #print(help(client))
        container_version_dict = {}
        container_data_dict = {}
        try:
            url = "tcp://%s:2375"%remote_ip
            print("------url-------", url)
            client = docker.DockerClient(base_url=url)
            client.ping()
            get_container_id_list = client.containers.list()
            for ids in get_container_id_list:
    #            for version_name in ids.image.tags:
                version_name = ids.image.tags[0]
                container_id_list = []
                pos = version_name.rfind(":")
                project_name = version_name[:pos+1]
                value = version_name[pos+1:]
                container_id_list.append(value)
                container_id_list.append(remote_ip)
                container_id_list.append(host_name)
                container_version_dict.update({project_name:container_id_list})
             #   container_id_list = container_id_list + ids.image.tags
            #pprint(container_id_list)
            #container_id_list.append(container_version_list)
            container_data_dict.update(container_version_dict)
            ed=time.time()
            print(ed-st)
            return container_data_dict
        except:
           print("-----error----")
           return container_data_dict

    def get_container_tree_data(self, remote_ip, host_name):
        st=time.time()
        container_data_dict = {}
        mid_data_list = []
        try:
            url = "tcp://%s:2375"%remote_ip
            print("------url-------", url)
            client = docker.DockerClient(base_url=url)
            get_container_id_list = client.containers.list()
            for ids in get_container_id_list:
                for version_name in ids.image.tags:
                    container_tag_dict = {}
                    container_tag_dict.update({"name":version_name, "value":version_name})
                    mid_data_list.append(container_tag_dict)
            mid_host_ip = "%s(%s)"%(host_name, remote_ip)
            print("--------mid_host_ip------",mid_host_ip)
            container_data_dict.update({"name":mid_host_ip, "children":mid_data_list})
            ed=time.time()
            print(ed-st)
            return container_data_dict
        except:
            print("-----error----")
            container_data_dict.update({"name":host_name, "children":mid_data_list})
            return container_data_dict

    def sealing_version_get_container(self, remote_ip):
        container_list = []
        try:
            url = "tcp://%s:2375"%remote_ip
            client = docker.DockerClient(base_url=url)
            get_container_id_list = client.containers.list()
            for ids in get_container_id_list:
                for version_name in ids.image.tags:
                    pos = str(version_name).rfind("/")
                    container_data_dict = {"id":ids.short_id, "warehouse":version_name[:pos+1], \
                                          "tag":version_name[pos+1:]}
                    container_list.append(container_data_dict)
            return container_list
        except:
            print("-----error----")
            return container_list

    def by_image_to_tag_push(self, remote_ip, src_image, dest_image, dest_version):
        '''
        :param remote_ip: 操作服务器
        :param src_image: 源标签
        :param dest_image: 目标标签
        :return: 
        '''
        try:
            url = "tcp://%s:2375"%remote_ip
            client = docker.DockerClient(base_url=url)
            print("!!!!!!!!!!!!!!!", remote_ip, dest_image, dest_version, HARBOR_NAME, HARBOR_PASSWD)
            image_obj = client.images
            image = image_obj.get(src_image)
            ret_status = image.tag(dest_image+":"+dest_version)
            print("----ret_status----", ret_status)
            push_status = image_obj.push(dest_image, dest_version, auth_config={"username":HARBOR_NAME, "password":HARBOR_PASSWD}, stream=True)
            for i in push_status:
                print("iiiiiiiiiiiiiii----",i)
            print("-------push_status-----", push_status)
        except:
            print("-----error----")
            return 


def env_group_get_container(group_name, single_obj, obj):
    '''
    :param single_obj: 选中的环境组对应的环境去重后对象
    :param obj: 选中的环境组未去重的环境对象
    :return: ["env_name":环境名,"container_data":{仓库名:[版本,对应所在服务ip，对应所在服务name]}]
    '''
    st_time=time.time()
    data_list = []
    DOCKER_API_OBJ = DockerRemoteApi()
    print("--------container_env_group_get_env---in--")
    print("--------single_obj--",single_obj)
    print("--------obj--", obj)
    for mid_single in single_obj:
        docker_run_info_dict = {}
        docker_run_info_list = []
        mid_data_dict = {}
        for mid in obj:
            if mid_single["relation_env__name"] == mid["relation_env__name"]:
                mid_ip = mid["relation_env__relation_hostinfo__ip"]
                mid_name = mid["relation_env__relation_hostinfo__name"]
                print("-------mid_ip------", mid_ip)
                run_docker_dict = DOCKER_API_OBJ.get_run_container_list(mid_ip, mid_name)
                if not run_docker_dict:
                    return
                else:
                    docker_run_info_dict.update(run_docker_dict)    
                    print("-----docker_run_info_dict------", docker_run_info_dict)
        mid_data_dict.update({"env_name":group_name,"container_data":docker_run_info_dict})
        data_list.append(mid_data_dict)
    ed_time = time.time()
    print("--spend--time---",ed_time-st_time)
    print("----data_list------", data_list)
    return data_list


def constrat_container_group(src_obj, dest_obj, unique_tag):
    src_env_name = src_obj[0]["env_name"]
    src_container_data =  src_obj[0]["container_data"]
    src_warehouse_list = list(src_container_data.keys())
    print("-----src_warehouse_list-----", src_warehouse_list)
    for dest in dest_obj:
        dest_env_name = dest["env_name"]
        dest_container_data = dest["container_data"]
        dest_warehouse_list = list(dest_container_data.keys())
        print("----dest_warehouse_list-----", dest_warehouse_list)
        for warehouse in src_warehouse_list:
            if (warehouse in dest_warehouse_list) and (src_container_data[warehouse][0] != dest_container_data[warehouse][0]):
                print("----differe--version----warehouse--",warehouse,"---src---", src_container_data[warehouse][0], "-----dest----", dest_container_data[warehouse][0])
                src_host_list = src_container_data[warehouse]
                dest_host_list = dest_container_data[warehouse]
                ContrastResult.objects.create(unique_id=unique_tag, src_env_group_name=src_env_name, \
                                dest_env_group_name=dest_env_name, src_host_name=src_host_list[2], \
                                src_warehouse_name=warehouse, src_version=src_host_list[0], \
                                dest_host_name=dest_host_list[2], dest_warehouse_name=warehouse, \
                                dest_version=dest_host_list[0], current_status=0)
            elif (warehouse not in dest_warehouse_list):
                print("----single---exit----",warehouse,"--src--", src_container_data[warehouse])
                src_host_list = src_container_data[warehouse]
                ContrastResult.objects.create(unique_id=unique_tag, src_env_group_name=src_env_name, \
                                dest_env_group_name=dest_env_name, src_host_name=src_host_list[2], \
                                src_warehouse_name=warehouse, src_version=src_host_list[0], \
                                current_status=1)
