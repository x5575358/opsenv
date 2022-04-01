from django.db import models

# Create your models here.

class UserGitlabCommit(models.Model):
    user_name = models.CharField(max_length=30,help_text="编码人")
    user_email = models.EmailField(help_text="用户邮箱")
    repository_name = models.CharField(max_length=20,help_text="仓库名")
    git_http_url = models.CharField(max_length=150, help_text="git代码http url")
    commit_id = models.CharField(max_length=50, help_text="提交commit id")
    commit_content = models.CharField(max_length=500, help_text="提交内容")
    defined_version = models.CharField(max_length=50, help_text="预制版本", default="error_commit")
    project_id = models.IntegerField(help_text="工程id")
    is_or_not_build = models.IntegerField(help_text="是否构建，0为未构建、1为构建中、2为构建成功、3为构建失败、4为其他", default=0)
    isornot_configuration = models.CharField(max_length=500, help_text="是否需要修改配置")
    isornot_db = models.CharField(max_length=500, help_text="是否需要执行数据库脚本")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_usergitlabcommit", u"查看开发提交代码记录"),
        )

class JenkinsBuild(models.Model):
    pipeline_name = models.CharField(max_length=40, help_text="pipeline工程名")
    build_number = models.IntegerField(help_text="构建编号")
    p_user_gitlab = models.ForeignKey(UserGitlabCommit, help_text="外键gitlabcommit")
    harbor_mirror = models.CharField(max_length=280, default="", help_text="镜像仓库名")
    build_status = models.IntegerField(help_text="构建状态,0为未构建、1为构建中、2为构建成功、3为构建是吧、4维为其他", default="0")
    release_status = models.IntegerField(help_text="发布状态,0为未发布、1为发布中、2为发布成功、3为发布失败、4为其他", default="4")
    creation_time = models.DateTimeField(auto_now=True,help_text="构建开始时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="构建结束时间")
    class Meta:
        permissions = (
            ("scanf_jenkinsbuild", u"查看构建"),
        )

class UserGitlabConfigCommit(models.Model):
    edit_user = models.CharField(max_length=30,help_text="修改人")
    user_email = models.EmailField(help_text="用户邮箱")
    repository_name = models.CharField(max_length=20,help_text="仓库名")
    git_http_url = models.CharField(max_length=150, help_text="git代码http url")
    commit_id = models.CharField(max_length=50, help_text="提交commit id")
    commit_content = models.CharField(max_length=500, help_text="提交内容")
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    class Meta:
        permissions = (
            ("scanf_usergitlabconfigcommit", u"查看修改配置记录"),
        )

