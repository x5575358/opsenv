from django.db import models

# Create your models here.
from django.db import models


class Log(models.Model):
    user = models.CharField(max_length=20, null=True)
    host = models.CharField(max_length=200, null=True)
    remote_ip = models.CharField(max_length=100)
    login_type = models.CharField(max_length=100)
    log_path = models.CharField(max_length=100)
    start_time = models.DateTimeField(null=True)
    pid = models.IntegerField()
    is_finished = models.BooleanField(default=False)
    end_time = models.DateTimeField(null=True)
    class Meta:
        permissions = (
            ("scanf_log", u"查看日志"),
        )

    def __unicode__(self):
        return self.log_path


class Alert(models.Model):
    msg = models.CharField(max_length=20)
    time = models.DateTimeField(null=True)
    is_finished = models.BigIntegerField(default=False)


class TtyLog(models.Model):
    log = models.ForeignKey(Log)
    datetime = models.DateTimeField(auto_now=True)
    cmd = models.CharField(max_length=200)


class ExecLog(models.Model):
    user = models.CharField(max_length=100)
    host = models.TextField()
    cmd = models.TextField()
    remote_ip = models.CharField(max_length=100)
    log_level = models.IntegerField(help_text="0为初级,1为中级，2为高级，3为其他",default=3)
    result = models.TextField(default='')
    create_time = models.DateTimeField(auto_now=True)


class FileLog(models.Model):
    user = models.CharField(max_length=100)
    host = models.TextField()
    filename = models.TextField()
    type = models.CharField(max_length=20)
    remote_ip = models.CharField(max_length=100)
    result = models.TextField(default='')
    datetime = models.DateTimeField(auto_now=True)

class LoginRecorder(models.Model):
    user_name = models.CharField(max_length=40, help_text="登陆用户名")
    login_ip = models.CharField(max_length=20, help_text="登陆IP")
    creation_time = models.DateTimeField(auto_now=True, help_text="登陆时间")
    login_status = models.IntegerField(help_text="0为登陆成功，1为登陆失败")
    class Meta:
        permissions = (
            ("scanf_loginrecorder", u"查看查看登录日志"),
        )
