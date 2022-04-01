from django.shortcuts import render

# Create your views here.
from Ops.settings import DINGTALK_WEBHOOK_TOKEN

from .dingtalk_push_api import dingtalk_send_message
from .send_mail_api import send_mail_message
from  opslog.models import ExecLog
from  opslog.log_api import request_client_ip
from django.http import  HttpResponse

def dingtalk_machine_api(message):
    dingtalk_send_message(DINGTALK_WEBHOOK_TOKEN, message)

def send_mail_msg(rec, subject, send_msg):
    pass
    send_mail_message(rec, subject, send_msg)

def log_decor(func):
    def _func(request, *args, **kargs):
        log_dict = {"index":[u"访问首页",0], "user":[u"访问用户列表",0], \
                "add_user":[u"新增用户",2], "edit_user":[u"修改用户",1], \
                "del_user":[u"删除用户",2], "set_user_permission":[u"设置用户权限",1], \
                "clear_user_permission":[u"清空用户权限",2],  \
                "user_add_group":[u"新增用户组",2], \
                "set_group_permission":[u"设置用户组权限",2], \
                "user_bind_group":[u"绑定用户组",1], "edit_password":[u"修改用户密码",1], \
                "del_group":[u"删除用户组",2], "group":[u"访问用户组",0], \
                "group": [u"访问用户组", 0], "asset_list":[u"访问资产管理",0], \
                "get_ec2_info":[u"更新EC2信息",2], "host_unit_list":[u"查看容器分布",0], \
                "add_host_unit":[u"新增容器组",1], "edit_host_unit":[u"修改容器组",1], \
                "get_container_by_group":[u"获取容器组容器",1], \
                "del_host_unit":[u"删除容器组",2], "project_list":[u"查看仓库项目",0], \
                "update_project":[u"更新仓库项目",1], "warehouse_list":[u"查看镜像仓库",0], \
                "update_warehouse":[u"更新镜像仓库",1], "tags_list":[u"查看镜像标签",0], \
                "update_tags":[u"更新镜像标签",1], "get_difference_container":[u"查看对比容器",0], \
                "update_difference_container":[u"执行对比容器",1], "exec_synchronization_container":\
                [u"执行发布",1], "constrast_check_network":[u"发布前网络检查",0], \
                "cancel_check_network":[u"取消发布",1], "load_exce_data":[u"网络检查后发布",1], \
                "hosts_list":[u"查看ansible hosts信息",0], "add_hosts":[u"新增ansible hosts信息",2], \
                "task_list":[u"查看发布任务列表",0], "add_task":[u"新增发布任务",1], \
                "history_task_list":[u"查看发布日志",0], "change_recoder":[u"查看封版列表",0], \
                "add_change":[u"申请封版",1], "sealing_release":[u"发布封版",1], \
                "apply_change_list":[u"查看变更申请列表",0], "apply_change":[u"新增变更申请",2], \
                "login_log_list":[u"查看登录日志",0], "sacnf_async_log":[u"查看发布执行日志",0], \
                "async_log_list":[u"查看异步封版日志",0], "loglist":[u"查看操作日志",0], \
                "tools_list": [u"查看工具列表", 0], "exce_docker_restart": [u"重启docker容器", 1], \
                "async_result_ret": [u"异步执行结果api调用", 1], "restart_tools_log": [u"查看重启容器日志", 0], \
                "up_file":[u"上传文件", 1],"save_upfiles": [u"保存上传文件", 2], \
                "cancle_upfiles":[u"取消上传文件", 2], \
                "delete_files": [u"删除上传文件", 2], "down_files": [u"下载文件", 2],\
                "script_group_list": [u"查看脚本组", 0], "create_group_script":[u"创建脚本组", 2], \
                "del_group_info": [u"删除封装脚本组", 2], "edit_group_info":[u"修改脚本组", 2],\
                "create_group_script": [u"创建脚本组", 2], "get_hosts_exec_script": [u"执行脚本组", 2], \
                "async_exce_script_ret":[u"执行脚本组结果api调用", 2], "exec_script_group": [u"查看脚本组日志", 0], \
                "container_env_list":[u"查看容器环境列表", 0], "add_container_env":[u"新增容器环境", 1], \
                "del_container_env":[u"删除容器环境", 1], "edit_container_env":[u"修改容器环境", 1], \
                "container_env_group":[u"查看容器环境组列表", 0], "add_container_env_group":[u"新增容器组环境", 1], \
                "del_container_env_group":[u"删除容器组环境", 1], "edit_container_group_env":[u"修改容器组环境", 1],
                "gitlab_commit_api":[u"gitlab webhook调用通知", 2], "gitlab_commit_list":[u"查看git webhook列表", 1], \
                "retry_run_pipeline":[u"重试调用pipeline", 2], "build_over_alert":[u"提交异常告警", 1], \
                "jenkins_build_list":[u"构建列表查询", 1], "jenkins_build_detail":[u"构建日志查询", 1], \
                "show_alb_info":[u"查询alb信息", 1], "show_rds_info":[u"查询rds信息", 1], \
                "gitlab_config_commit_api":[u"查询gitconfig提交信息", 1], "gitlab_config_commit":[u"查询gitconfig提交信息", 1]}
        remote_ip = request_client_ip(request)
        user = request.user
        cmd = str(log_dict["%s"%func.__name__][0])
        level = log_dict["%s"%func.__name__][1]
        ExecLog.objects.create(user=user, host="", cmd=cmd, remote_ip=remote_ip, log_level=level)
        return func(request, *args, **kargs)
    return _func

def gitlab_notification_api(request):
    print("IIIIIIIIIIIIIIII")
    req_handle = request.POST
    print(req_handle)
    print(help(req_handle))
    return HttpResponse("sss")
