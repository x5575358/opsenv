from django.db import models

# Create your models here.
class RunContainer(models.Model):
    create_tags = models.CharField(max_length=30, help_text="唯一标示")
    hosts_name = models.CharField(max_length=20, help_text="主机名")
    hosts_ip = models.CharField(max_length=15, help_text="主机ip")
    container_id = models.CharField(max_length=12, help_text="容器short id", default="")
    container_name = models.CharField(max_length=100, help_text="容器名")
    create_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    excute_status = models.IntegerField(default=3,help_text="0为重启中,1为重启成功,2为重启失败，3为未选择重启")
    class Meta:
        permissions = (
            ("scanf_runcontainer", u"查看重启容器"),
        )

class AsyncFileInfo(models.Model):
    create_tags = models.CharField(max_length=30, help_text="唯一标示", default="")
    req_user = models.CharField(max_length=50, help_text="请求用户", default="")
 #   file_name = models.CharField(max_length=50, help_text="需要重启容器列表文件")
#    file_path = models.CharField(max_length=150, help_text="文件路径")
    hosts_name = models.CharField(max_length=20, help_text="主机名")
    excute_status = models.IntegerField(default=3,help_text="0为重启中,1为重启成功,2为重启失败，3为未选择重启")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_asyncfileinfo", u"查看重启结果"),
        )


class UploadFiles(models.Model):
    up_user  = models.CharField(max_length=50, help_text="上传用户")
    up_tags  = models.CharField(max_length=50, help_text="上传标示")
    file_name = models.CharField(max_length=150, help_text="文件名")
    file_save_path = models.CharField(max_length=500, help_text="文件存放路径")
    file_size = models.FloatField(help_text="文件大小,单位字节")
    remarks = models.CharField(max_length=800, help_text="备注", default="")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_uploadfiles", u"查看文件上传"),
        )

class ScriptGroup(models.Model):
    group_uniqu_tag =models.BigIntegerField(help_text="唯一标示")
    title_name = models.CharField(max_length=150, help_text="标题名")
    create_user = models.CharField(max_length=50, help_text="创建者")
    color_tags = models.CharField(max_length=20, help_text="颜色code",default="btn green")
    relate_id = models.ForeignKey(UploadFiles, help_text="关联脚本")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_scriptgroup", u"查看脚本组"),
        )

class ScriptGroupRelease(models.Model):
    group_uniqu_tag = models.BigIntegerField(help_text="组唯一标签")
    relate_script_group = models.ForeignKey(ScriptGroup, help_text="关联功能组")
    hosts_ip = models.CharField(max_length=20, help_text="目的主机")
    hosts_name = models.CharField(max_length=30, help_text="目的主机hosts")
    operator_user = models.CharField(max_length=30, help_text="操作用户")
    release_script_name = models.CharField(max_length=80, help_text="执行脚本名", default="")
    release_script_path = models.CharField(max_length=200, help_text="执行脚本路径", default="")
    release_status = models.IntegerField(help_text="0为执行中,1为执行成功,2为执行失败，3为创建自动化执行脚本失败，4为其他", default=0)
    log_path = models.CharField(max_length=200, help_text="日志文件路径", default="")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True, help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_scriptgrouprelease", u"查看脚本组"),
        )

class ScriptGroupExecSeq(models.Model):
    script_exce_order =  models.CharField(max_length=500, help_text="脚本执行顺序")
    script_group_tag = models.BigIntegerField(help_text="组唯一标签")
    create_time = models.DateTimeField(auto_now=True, help_text="创建时间")

