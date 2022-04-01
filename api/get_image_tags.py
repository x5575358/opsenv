#!/bin/pyhton3
#coding=utf-8

import os
import json

def bash(cmd):
    """
    run a bash shell command
    执行bash命令
    """
    return os.popen(cmd).read()


ret = bash('curl -u "xxxx:xxxx" -X GET -H "Content-Type: application/json" \
     "https://reg.xxxxxx.net/api/projects" -k -s')
ret_json = json.loads(ret)

def project_info(ret_param):
    ret_list = []
    for i in ret_param:
        data = {}
        data["id"] = i["project_id"]
        data["name"] = i["name"]
        data["repo_count"] = i["repo_count"]
        data["creation_time"] = i["creation_time"]
        data["update_time"] = i["update_time"]
        data["metadata"] = "1"
        ret_list.append(data)
    return ret_list
