# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/08/21 18:36
# File  : dingtalk_push_api.py
# Software PyCharm

import json
import requests

def dingtalk_send_message(token,messsage):
    program={"msgtype":"text", "text":{"content":messsage},\
            #"at":{"atMobiles":["18300009257"], "isAtAll": False}, \
            }
    headers={'Content-Type': 'application/json'}
    f=requests.post(token,data=json.dumps(program),headers=headers)
    print("------dingtalk_send_message-ret-----",f)

