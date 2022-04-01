from django.db import models
from release.models import HostsInfo 
# Create your models here.


class HostUnit(models.Model):
    name = models.CharField(max_length=50, help_text="组名")
#    relate_host_key = models.ForeignKey(HostsInfo,help_text="关联主机信息")
    host_tag = models.CharField(max_length=800, help_text="宿主机标签别名")
    add_user = models.CharField(max_length=50, help_text="添加人")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_hostunit", u"查看组"),
        )

class ContainerDist(models.Model):
    name = models.CharField(max_length=300, help_text="容器名")
    HostMachine = models.CharField(max_length=300, help_text="所属宿主机")
    class Meta:
        permissions = (
            ("scanf_containerdist", u"查看容器分布"),
        )



class ContainerEnv(models.Model):
    unique_flag = models.CharField(max_length=45,help_text="唯一标示")
    relation_hostinfo = models.ForeignKey(HostsInfo, help_text=("关联对应主机"))
    name = models.CharField(max_length=80,help_text="环境名")
    create_user = models.CharField(max_length=30,help_text="创建者")
    is_or_not_alert = models.IntegerField(help_text="0为不告警，1为告警", default=0)
    is_or_not_monitor = models.IntegerField(help_text="0为不监控，1为监控", default=0)
    env_code = models.IntegerField(help_text="平台环境code", default=0)
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_containerenv", u"查看容器环境"),
        )

class ContainerEnvGroup(models.Model):
    unique_flag = models.CharField(max_length=45,help_text="对应容器环境组唯一标示")
    #relate_env_flag = models.CharField(max_length=45,help_text="对应容器环境唯一标示")
    relation_env = models.ForeignKey(ContainerEnv, help_text=("关联容器环境"),default="")
    name = models.CharField(max_length=80,help_text="环境名")
    create_user = models.CharField(max_length=30,help_text="创建者")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_containerenvgroup", u"查看容器组"),
        )

class SetReleaseScriptBases(models.Model):
    env_name = models.IntegerField(help_text="1为ci环境、2为测试环境、\
    3为uat环境、4为预生产环境、5为生产环境、6为其他环境")
    mem_size = models.IntegerField(help_text="内存大小")
    config_url = models.CharField(max_length=30, help_text="config注册中心地址以及端口")
    add_user = models.CharField(max_length=30,help_text="修改人")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_setreleasescriptbases", u"查看修改配置记录"),
        )

class PlatmentBasicInfo(models.Model):
    env_name = models.CharField(max_length=100, help_text="环境名")
    env_code = models.AutoField(primary_key=True, help_text="系统自动增加")
    add_user = models.CharField(max_length=30, help_text="修改人")
    creation_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_platmentbasicinfo", u"查看平台基本信息"),
        )

class PlatmentInfo:
    add_user = models.CharField(max_length=80, help_text="创建者")
    platment_name = models.CharField(max_length=80, help_text="平台名")
    platment_code = models.IntegerField(primary_key=True, help_text="平台id")
    available_condition = models.CharField(max_length=18, help_text="True可用，False不可用", default="False")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_platmentinfo", u"查看平台信息"),
        )
