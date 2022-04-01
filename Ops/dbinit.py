
from django.contrib.auth.models import User, Group, Permission, ContentType
from django.http import HttpResponse, HttpResponseRedirect
from release.models import AnsibleExceMode, BaseConfiguration
from  asset.models import RegionName



class Setup(object):
    def __init__(self):
        self.admin_user = "admin"
    def _create_admin(self):
        if not Permission.objects.filter(codename = "scanf_user"):
            Permission.objects.create(name = u"查看用户", codename="scanf_user", \
                       content_type = ContentType.objects.get_for_model(User))
        if not  Permission.objects.filter(codename = "scanf_group"):
            Permission.objects.create(name = u"查看用户组", codename="scanf_group", \
                       content_type=ContentType.objects.get_for_model(Group))
        if User.objects.filter(username=self.admin_user):
            return HttpResponse("已经初始化admin,请勿重复初始化！")
        User.objects.create_user(username=self.admin_user, password="1234qwer", \
             email="hengjun.wei@xxxxxxxxx.com", is_active=True)
#        prvi_list = Permission.objects.values("id")
 #       for i in prvi_list:
  #          ids = i["id"]
   #         print("-------i-------=", i)
    #        print("-------ids-------=", ids)

     #       User.objects.get(username="admin").user_permissions.add(ids)
      #  return HttpResponse("初始化完成，初始化后用户名为'admin',密码为'1234qwer',请及时修改密码！")
    def _create_ansiblemodle(self):
        origin_dict = [{"name":"cat", "code":" ansible %s -m raw -a  \"cat %s\""}, \
                    {"name":"sh", "code":" ansible %s -m raw -a \"sh %s %s\""}]
        baseconfig_dict = [{"name":"reg.xxxxxx.net", "code":"syck", "remark":u"私有仓库"},
                         {"name": "service-create.sh", "code": "cjrq", "remark": u"创建容器"},
                         {"name": "service-update.sh", "code": "sjrq", "remark": u"升级容器"}]
        AnsibleExceMode.objects.all().delete()
        BaseConfiguration.objects.all().delete()
        for org in origin_dict:
            AnsibleExceMode.objects.create(**org)
        for base in baseconfig_dict:
            BaseConfiguration.objects.create(**base)
    def _create_regionname(self):
        org_dict = [{"name":u"新加坡", "code":"ap-southeast-1"},
                    {"name": u"俄勒冈", "code": "us-west-2"},
                    {"name": u"爱尔兰", "code": "eu-west-1"},
                    {"name": u"首尔", "code": "ap-northeast-2"},
                    {"name": u"俄亥俄州", "code": "us-east-2"},
      #              {"name": u"加利福尼亚北部", "code": "us-west-1"},
      #              {"name": u"弗吉尼亚北部", "code": "us-east-1"},
       #             {"name": u"加拿大 (中部)", "code": "ca-central-1"},
       #             {"name": u"欧洲（法兰克福）", "code": "eu-central-1"},
       #             {"name": u"欧洲 (伦敦)", "code": "eu-west-2"},
        #            {"name": u"欧洲 (巴黎)", "code": "eu-west-3"},
        #            {"name": u"亚太区域（东京）", "code": "ap-northeast-1"},
     #               {"name": u"亚太区域 (大阪当地)", "code": "ap-northeast-3"},
        #            {"name": u"亚太区域（悉尼）", "code": "ap-southeast-2"},
     #               {"name": u"亚太地区（孟买）", "code": "ap-south-1"},
    #                {"name": u"南美洲（圣保罗）", "code": "sa-east-1"},
                    ]
        RegionName.objects.all().delete()
        for org in org_dict:
            RegionName.objects.create(**org)
        print(RegionName.objects.all().values("name"))
    def _set_admin_premission(self):
        prvi_list = Permission.objects.values("id")
        User.objects.get(username="admin").user_permissions.clear()
        for i in prvi_list:
            ids = i["id"]
            print("-------i-------=", i)
            print("-------ids-------=", ids)
            User.objects.get(username="admin").user_permissions.add(ids)
        return HttpResponse("初始化完成，初始化后用户名为'admin',密码为'1234qwer',请及时修改密码！")


def tt(request):
    t = Setup()
    t._create_admin()
    t._set_admin_premission()
    t._create_regionname()
    t._create_ansiblemodle()
    print("----------end------tt------")
    return HttpResponseRedirect("/login/")
