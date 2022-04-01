# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/11/9 16:14
# File  : jekins_remote_api.py
# Software PyCharm

import jenkins
from celery import task
from pprint import pprint
from Ops.settings import JEKINS_URL, USER_ID, TOKEN_ID
from api.open_api import bash
from api.send_mail_api import send_mail_message
from .models import UserGitlabCommit, JenkinsBuild

class RemoteJekinsApi:
    def __init__(self, url, username, userpasswd):
        self.handle = jenkins.Jenkins(url, username, userpasswd)
        print("-11111--handle----",self.handle)

    #获取所有job信息列表
    def get_job_info(self):
        return self.handle.get_info()

    def get_next_build_number(self, name):
        '''
        通过工程名获取下一个构建的编号
        :param name: job名称
        :return: 返回下一个构建工程的编号
        '''
        aim_job_obj = self.handle.get_job_info(name)
        next_Build_Number = aim_job_obj["nextBuildNumber"]
        return next_Build_Number

    def build_job(self, name, param):
        '''
        :param name: job 名，可以通过get_job_info接口去获取
        :param param: 字典
        :return: 构建队列
        '''
        print("---start-----build_job---", self.handle)
        print("---start-----build_job-----name--", name)
        print("---start-----build_job------param---", param)
        print("---start-----build_job------param---", type(param))
        build_ret = self.handle.build_job(name, param)
        #pprint(self.handle.get_build_info(name, 130))
        print("-----build_job------", build_ret)
        return build_ret


    #停止正在构建中的job
    def stop_build(self, name, build_number):
        '''
        停止正在构建的工程
        :param name: 正在运行的job名称
        :param build_number: 需要停止的构建编号
        :return:
        '''
        ret = self.handle.stop_build(name, build_number)
        print("---stop_build--", ret)
        return ret

    def get_build_console_output(self, name, number):
        console_ret = self.handle.get_build_console_output( name, number)
        return console_ret

@task
def async_run_pipeline(job_name, param_dict, commit_id):
    '''
     异步调用jenkins pipeline
    :param job_name: 工程名
    :param param_dict: 调用pipeline需要带的参数
    :param p_id: 外键id
    :return:
    '''
    
#    add_tag_ret = bash(add_tag_info)
#    print("-----add_tag_ret----", add_tag_ret)
    print("-----pipeline_name----", job_name)
    print("-----param_dict----", param_dict)
    req_handle = RemoteJekinsApi(JEKINS_URL, USER_ID, TOKEN_ID)
    print("-----start  pipeline----")
#        print("-----JEKINS_URL----", JEKINS_URL)
#        print("-----USER_ID----", USER_ID)
#        print("-----TOKEN_ID----", TOKEN_ID)
#        req_handle = jenkins.Jenkins(JEKINS_URL, USER_ID, TOKEN_ID)
    req_handle.build_job(job_name, param_dict)
    print("-----end  pipeline----")
#        aim_job_obj = req_handle.get_job_info(job_name)
#        next_Build_Number = aim_job_obj["nextBuildNumber"]
#        build_number = next_Build_Number
    build_number = req_handle.get_next_build_number(job_name)
    print("--async_run_pipeline----build_number-----", build_number)
    data = {"pipeline_name":job_name, "build_number":build_number, \
               "p_user_gitlab":UserGitlabCommit.objects.get(commit_id=commit_id), \
               "build_status":1}
    JenkinsBuild.objects.create(**data)
    print("--async_run_pipeline----over-----")
#    except: 
#        print("---async_run_pipeline--error------")

@task
def async_illegal_name_alert(dest_user, dest_email, alert_content):
    '''
    异步报错通知\告警
    :param dest_user: 告警\通知对象
    :param dest_email: 告警\通知对象邮箱
    :param alert_content: 告警\通知内容
    :return:
    '''
    alert_subject = "代码提交commit content不规范"
    send_mail_message(dest_email, alert_subject, alert_content)
