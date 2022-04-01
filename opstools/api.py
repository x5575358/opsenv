from release.release_api import DockerRemoteApi
from .models import RunContainer, AsyncFileInfo 
from mirrors.mirror_api import GetDayTime
from celery import task
import docker
import time

@task
def async_docker_restart(data_dict):
    '''
    async to restart container by gived the info
    :param data_dict: 
    :return: 
    '''
    for key, value in data_dict.items():
        try:
            url = "tcp://%s:2375"%key
            print("--async_docker_restart----url-------", url)
            client = docker.DockerClient(base_url=url)
            tags_list = RunContainer.objects.filter(hosts_ip=key, excute_status=3).values("create_tags").distinct()
            print("------sttttt--tags_list--------",tags_list)
            st_time = time.time()
            tags = tags_list[0]["create_tags"]
            for short_id in value:
                print("----start--get--containers--")
                mid_handle = client.containers.get(container_id=short_id)
                print("----start--end--containers--")
                print("------restart start----")
                ret = mid_handle.restart()
                print("------restart over----")
                RunContainer.objects.filter(hosts_ip=key, container_id=short_id, excute_status=3).update(excute_status=1)
            print("--------tags_list--------", tags_list)
            ed_time = time.time()
            print("------------time------------------",ed_time-st_time)
            GT = GetDayTime()
            NOW_DAY = GT.get_now_time("%Y-%m-%d %H:%M:%S")
            AsyncFileInfo.objects.filter(create_tags=tags).update(excute_status=1, update_time=NOW_DAY)
        except ZeroDivisionError as e:
           print("-----error----", e)

