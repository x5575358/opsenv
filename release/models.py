from __future__  import unicode_literals

# from __future__  import unicode_literals
from django.db import models


from django.db import models
import django.utils.timezone as timezone
from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from Ops.settings import JSON_DATA_DIR
import django.utils.timezone as timezone
# Create your models here.

login_url = '/'
#上线任务发布表
class ReleaseInfo(models.Model):
    id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=50)
    service_version = models.CharField(max_length=50)
    release_status = models.CharField(max_length=2)
    config_modify_status = models.CharField(max_length=2)
    config_modify_content = models.CharField(max_length=2000)
    file_remain_status = models.CharField(max_length=2)
    file_remain = models.CharField(max_length=2000)
    dev_owner = models.CharField(max_length=50)
    test_owner = models.CharField(max_length=50)
    maint_owner = models.CharField(max_length=50)
    test_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10)
    release_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now=True)
    last_update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=50)
    update_user = models.CharField(max_length=50)
    info = models.CharField(max_length=2000)
    class Meta:
        permissions = (
            ("release_info", u"上线任务发布表"),
            ("edit_release_info", u"修改上线任务发布表"),
            ("add_release_info", u"新增上线任务发布表"),
            ("del_release_info", u"删除上线任务发布表"),
        )

class HostsInfo(models.Model):
    name = models.CharField(max_length=30)
    ip = models.CharField(max_length=20)
    private_key = models.CharField(max_length=50)
    ansible_user = models.CharField(max_length=15,default="ec2-user")
    creation_time = models.DateTimeField(auto_now=True)
    available_condition = models.CharField(max_length=18, help_text="True可用，False不可用", default="True")
    class Meta:
        permissions = (
            ("scanf_hostinfo", u"查看ansible的hosts"),
        )

class AnsibleHostFile(models.Model):
    relate_hostifo_key = models.ForeignKey(HostsInfo,help_text=("关联对应主机"))
    json_file_name = models.CharField(max_length=50,help_text="ansible host文件对应的json文件")
    json_file_path = models.CharField(max_length=300,help_text="文件存放路径", default=JSON_DATA_DIR)
    add_user = models.CharField(max_length=30,help_text="添加者")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")

class TaskInfo(models.Model):
    name = models.CharField(max_length=30,help_text="任务名称")
    # warehouse = models.CharField(max_length=50,help_text="所属仓库")
    # tags = models.CharField(max_length=50,help_text="镜像标签")
    history_warehouse = models.CharField(max_length=80, help_text="历史仓库名", default="")
    history_version = models.CharField(max_length=20, help_text="历史容器环境名", default="")
    warehouse_tags = models.CharField(max_length=150,help_text="要发布的仓库及镜像标签名",default=None)
    exscript = models.CharField(max_length=50,help_text="执行脚本")
    releaser = models.CharField(max_length=30,help_text="发布者",default=None)
    release_status = models.IntegerField(help_text="0为发布并执行且执行成功,1为\
    未发布,2发布但未执行,3为发布确认执行中，4为发布执行失败,5为其他")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    need_exce_param = models.CharField(max_length=500,help_text="预执行语句",default=None)
    task_source = models.IntegerField(default=0,help_text="0为任务发布新增任务,1为对比容器新增任务,2为变更申请发布")
    hostsinfo = models.ForeignKey(HostsInfo,help_text="关联主机信息")
    class Meta:
        permissions = (
            ("scanf_taskinfo", u"查看发布任务"),
        )


class AffirmInfo(models.Model):
    ip = models.CharField(max_length=20,help_text="目的ip")
    hosts_tags = models.CharField(max_length=20, help_text="hosts标签")
    order_param = models.CharField(max_length=500,help_text="需要执行的语句")
    releaser = models.CharField(max_length=30,help_text="发布者",default=None)
    release_status = models.IntegerField(help_text="0为成功，1为失败，2为未执行,3为其他")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    ftaskinfo  = models.ForeignKey(TaskInfo,help_text=("关联对应任务"))
admin.site.register(ReleaseInfo)

#ansible model
class AnsibleExceMode(models.Model):
    name =  models.CharField(max_length=30,help_text="模板名称")
    code = models.CharField(max_length=50,help_text="模板代码")
    create_user = models.CharField(max_length=15, default="system")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")

class BaseConfiguration(models.Model):
    name = models.CharField(max_length=30, help_text="名称")
    code = models.CharField(max_length=500,help_text="对应name的名称，由汉字首字母组成")
    remark = models.CharField(max_length=30, help_text="备注",default="")

class AsyncRecord(models.Model):
    file_name = models.CharField(max_length=50,help_text="命令执行结果文件名")
    file_path = models.CharField(max_length=200,help_text="文件绝对路径")
    affirm_id = models.ForeignKey(AffirmInfo,help_text=("关联确认任务"))
    release_status = models.IntegerField(default=2,help_text="0为成功，1为失败，2为执行中,3其他")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_asyncrecord", u"查看历史发布"),
        )


class ContrastOfResult(models.Model):
    test_name = models.CharField(max_length=100,help_text="测试容器名")
    test_container_hosts = models.CharField(max_length=20,help_text="测试容器所属主机名")
    uat_name = models.CharField(max_length=100,help_text="uat容器名")
    uat_container_hosts = models.CharField(max_length=20,help_text="uat容器所属主机名")
    status = models.IntegerField(help_text="0为未发布，1为发布中，2为发布完成")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_contrastofresult", u"查看容器对比"),
        )


class LastVersionRecord(models.Model):
    version_id=models.CharField(max_length=100,help_text="上个版本号")
    need_update_version=models.CharField(max_length=500,help_text="需要更新的版本号")
    user=models.CharField(max_length=20,help_text="操作者")
    ftaskinfo=models.ForeignKey(TaskInfo, help_text=("关联对应任务"))
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")


class ContrastResult(models.Model):
    unique_id = models.CharField(max_length=20, help_text="唯一标示")
    src_env_group_name = models.CharField(max_length=50, help_text="源容器环境组名")
    dest_env_group_name = models.CharField(max_length=50, help_text="目标容器环境组名")
    src_host_name = models.CharField(max_length=50, help_text="源容器主机名")
    src_warehouse_name = models.CharField(max_length=80, help_text="源仓库名")
    src_version = models.CharField(max_length=20, help_text="源容器环境名")
    dest_host_name = models.CharField(max_length=50, help_text="目标容器主机名", default="")
    dest_warehouse_name = models.CharField(max_length=80, help_text="目标仓库名", default="")
    dest_version = models.CharField(max_length=20, help_text="目标容器环境名", default="")
    current_status = models.IntegerField(help_text="0为版本不同,1为服务不存在,3为已发布,4为历史记录,5为其他")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_contrastresult", u"查看容器对比"),
        )
