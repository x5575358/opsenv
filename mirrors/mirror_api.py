# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/6 14:06
# File  : mirror_api.py
# Software PyCharm


import datetime
from .models import *

import json
import urllib3
import requests
from pprint import pprint

# forbid InsecureRequestWarning
urllib3.disable_warnings()


def add_project(ret_param):
#	ret_list=[]
    print("------->>>>>>"+str(len(ret_param)))
    for o in ret_param:
        if "citest" == o["name"]:
            continue
        pro_instance = ProjectInfo.objects.filter(id=o["project_id"])
        print("------oooooooo---------",o)
        if len(pro_instance) == 0:
            ProjectInfo.objects.create(id=o["project_id"], name=o["name"], \
                       repo_count=o["repo_count"], creation_time=o["creation_time"], \
                       update_time=o["update_time"], metadata="1")
        else:
            ProjectInfo.objects.filter(id=o["project_id"]).update(repo_count=o["repo_count"], \
                        creation_time=o["creation_time"], update_time=o["update_time"])
#            print("数据存在,无需插入.")

def add_warehouse(ret_param):
    for o in ret_param:
        ware_instance = MirrorWarehouse.objects.filter(id=o["id"])
        if len(ware_instance) == 0:
            MirrorWarehouse.objects.create(id=o["id"], name=o["name"], tags_count=o["tags_count"],\
                creation_time=o["creation_time"], update_time=o["update_time"], \
                projecter=ProjectInfo.objects.get(id=o["project_id"]))
        else:
            MirrorWarehouse.objects.filter(id=o["id"]).update(tags_count=o["tags_count"], \
                            creation_time=o["creation_time"], update_time=o["update_time"], \
                            projecter=ProjectInfo.objects.get(id=o["project_id"]))
#            print("warehouse数据存在,无需插入.")

def add_tags(ret_param, warehouse_id):
    for o in ret_param:
        tags_instance = MirrorTags.objects.filter(name=o["name"])
        if len(tags_instance) == 0:
            MirrorTags.objects.create(digest=o["digest"], name=o["name"], size=\
                       round(int(o["size"])/1024/1024, 2), os=o["os"], docker_version=\
                       o["docker_version"], created=o["created"], warehouser=\
                       MirrorWarehouse.objects.get(id=warehouse_id))
        else:
            MirrorTags.objects.filter(name=o["name"]).update(digest=o["digest"], name=o["name"], \
                       size=round(int(o["size"])/1024/1024, 2), os=o["os"], docker_version=\
                       o["docker_version"], created=o["created"], warehouser=\
                       MirrorWarehouse.objects.get(id=warehouse_id))
#            print("tags数据存在,无需插入.")

class GetDayTime:
    def __init__(self):
        self.time_handle = datetime.datetime.now()

    def get_now_time(self, time_formart):
        now = self.time_handle.strftime(time_formart)
        return now
	
    def get_pre_later_time(self, day, time_formart):
        self.pltime = datetime.timedelta(day) + datetime.datetime.now()
        result_pltime = self.pltime.strftime(time_formart)
        return result_pltime


class HarborApi(object):
    def __init__(self, url, username, passwd, protocol="https"):
        '''
        init the request
        :param url: url address or doma
        :param username:
        :param passwd:
        :param protect:
        '''
        self.url = url
        self.username = username
        self.passwd =passwd
        self.protocol = protocol


    def login_get_session_id(self):
        '''
        by the login api to get the session of id
        :return:
        '''
        harbor_version_url = "%s://%s/api/systeminfo"%(self.protocol, self.url)
        header_dict = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0', \
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data_dict = {
            "principal": self.username,
            "password": self.passwd
        }
        v_req_handle = requests.get(harbor_version_url, verify=False)
        self.harbor_version = v_req_handle.json()["harbor_version"]
        if self.harbor_version.startswith("v1.4"):
            req_url = "%s://%s/login" % (self.protocol, self.url)
            self.session_id_key = 'beegosessionID'
        elif self.harbor_version.startswith("v1.7"):
            req_url = "%s://%s/c/login" % (self.protocol, self.url)
            self.session_id_key = "sid"
        else:
            raise ConnectionError("the %s version is not to supply!"%self.harbor_version)
        req_handle = requests.post(req_url, data=data_dict, headers=header_dict, verify=False)
        if 200 == req_handle.status_code:
            self.session_id = req_handle.cookies.get(self.session_id_key)
            return self.session_id
        else:
            raise Exception("login error,please check your account info!"+ self.harbor_version)


    def logout(self):
        requests.get('%s://%s/logout' %(self.protocol, self.url),
                     cookies={self.session_id_key: self.session_id}, verify=False)
        print("successfully logout")

    def project_info(self):
        project_url = "%s://%s/api/projects" %(self.protocol, self.url)
        req_handle = requests.get(project_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            print("-------project_info------req_handle==",req_handle.json(), "---type---",type(req_handle.json()))
            return req_handle.json()
        else:
            raise Exception("Failed to get the project info。")

    def repository_info(self, project_id):
        repository_url = '%s://%s/api/repositories?project_id=%s' %(self.protocol, self.url, project_id)
        req_handle = requests.get(repository_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            return req_handle.json()
        else:
            raise Exception("Failed to get the repository info。")

    def tags_info(self, repository_name):
        tags_url = '%s://%s/api/repositories/%s/tags' %(self.protocol, self.url, repository_name)
        req_handle = requests.get(tags_url, cookies={self.session_id_key: self.session_id}, verify=False)
        if 200 == req_handle.status_code:
            return req_handle.json()
        else:
            raise Exception("Failed to get the tags info。")

