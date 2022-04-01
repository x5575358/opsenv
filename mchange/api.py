# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/7/3 16:48
# File  : api.py
# Software PyCharm

from release.release_api import async_list_bash, bash, DockerRemoteApi
from  .models import HostsInfo, ServerMirror

def get_server_mirror(ip_list):
    docker_hander = DockerRemoteApi()
    print("----ip_list-----", ip_list)
    hostname_ip_list = []
    ServerMirror.objects.all().delete()
    for mid_ip in ip_list:
        print("----mid_ip--111111111111122222222---", mid_ip)
        mid_list = docker_hander.sealing_version_get_container(mid_ip)
        hostsinfo = HostsInfo.objects.get(ip=mid_ip)
     #   hostname_ip_list = hostname_ip_list + list(HostsInfo.objects.filter(ip=mid_ip).values("ip", "name"))
        for mid_dict in mid_list:
            data = {}
            data.update(dict({"repository":mid_dict["warehouse"], "tag":mid_dict["tag"], \
                 "image_id":mid_dict["id"], "hostsinfo":hostsinfo}))
            print(data)
            ServerMirror.objects.create(**data)
    return hostname_ip_list
            
