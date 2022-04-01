#!/bin/bash
#author: dennis
#date:	2018-10-2


redis_config_id=`docker ps|grep "config-server\|redis"|awk -F " " '{print $1}'`
for id in $redis_config_id
do
    docker restart $id && sleep 20
done

container_id=`docker ps|awk -F " " '{print $1}'|grep  -v "CONTAINER\|config-server\|redis"`
for id in $container_id
do
    docker restart $id && sleep 20
done
