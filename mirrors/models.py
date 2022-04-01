from django.db import models



class ProjectInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    repo_count = models.IntegerField()
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    metadata = models.CharField(max_length=20)
    class Meta:
        permissions = (
            ("scanf_projectinfo", u"查看项目"),
        )

class MirrorWarehouse(models.Model):
    name = models.CharField(max_length=40)
    tags_count = models.IntegerField()
    creation_time = models.DateTimeField(auto_now=True,help_text="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,help_text="修改时间")
    projecter = models.ForeignKey(ProjectInfo)
    class Meta:
        permissions = (
            ("scanf_warehouse", u"查看镜像仓库"),
        )

class MirrorTags(models.Model):
    digest = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    size = models.IntegerField()
    os = models.CharField(max_length=20)
    docker_version = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now=True,help_text="创建时间")
    warehouser = models.ForeignKey(MirrorWarehouse)
    class Meta:
        permissions = (
            ("scanf_mirrotag", u"查看镜像标签"),
        )

