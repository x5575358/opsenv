from django.db import models
from release.models import HostsInfo

# Create your models here.

class ChangeRecorder(models.Model):
    unique_tags = models.CharField(max_length=30,help_text="唯一标示")
    proposer = models.CharField(max_length=30,help_text="申请人")
    before_warehouse_tags = models.CharField(max_length=100,help_text="镜像标签")
    after_warehouse_tags = models.CharField(max_length=100,help_text="镜像标签")
    change_status = models.IntegerField(help_text="0为封版成功、1为封版失败，2为封版中，3其他")
    change_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    reason = models.CharField(max_length=1000,help_text="申请原因",default="NULL")
    hostsinfo = models.ForeignKey(HostsInfo,help_text="关联主机信息")
    class Meta:
        permissions = (
            ("scanf_changerecorder", u"查看变更记录"),
        )


class FailChangeDetailRecorder(models.Model):
    warehouse_tags = models.CharField(max_length=100,help_text="镜像标签")
    changerecorder = models.ForeignKey(ChangeRecorder,help_text="关联变更记录")

class ServerMirror(models.Model):
    repository = models.CharField(max_length=100,help_text="仓库名")
    tag = models.CharField(max_length=80,help_text="标签")
    image_id = models.CharField(max_length=20,help_text="镜像id")
    #size = models.CharField(max_length=20,help_text="大小")
    #mirror_time = models.CharField(max_length=30,help_text="镜像时间",default="NULL")
    create_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    hostsinfo = models.ForeignKey(HostsInfo,help_text="关联主机信息")

class ApplicationRecorder(models.Model):
    apply_user =  models.CharField(max_length=80,help_text="申请人")
    project_name = models.CharField(max_length=200,help_text="工程名")
    project_branch = models.CharField(max_length=100,help_text="工程版本")
    bug_id = models.CharField(max_length=20,help_text="禅道ID")
    reasons = models.CharField(max_length=500,help_text="变更原因")
    change_type = models.CharField(max_length=50,help_text="变更类型")
    apply_status = models.IntegerField(help_text="申请状态，1为新增、2为处理，3为关闭",default=1)
    application_time = models.DateTimeField(auto_now=True,help_text="申请时间")
    class Meta:
        permissions = (
            ("scanf_application_recorder", u"查看申请记录"),
        )
