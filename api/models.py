from django.db import models

# Create your models here.
class AsyncOperationAudit(models.Model):
    exce_order = models.CharField(max_length=200,help_text="异步请求命令")
    file_name = models.CharField(max_length=50,help_text="命令执行结果文件名")
    file_path = models.CharField(max_length=200,help_text="文件绝对路径")
    unique_code=models.IntegerField(help_text="任务id",default=99999999)
    release_status = models.IntegerField(default=2,help_text="0为成功，1为失败，2为执行中,3其他")
    remote_ip = models.CharField(max_length=100,help_text="请求ip")
    user = models.CharField(max_length=30,help_text="操作者")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    class Meta:
        permissions = (
            ("scanf_asyncoperationaudit", u"查看异步日志"),
        )

