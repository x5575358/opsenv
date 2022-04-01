#!/bin/bash

container_id=`docker ps -q`
dest_v_select_str=`echo $container_id|sed 's/ /\\\|/g'`
sudo rm -f $(ls /data/applogs/*|grep -v $(echo $dest_v_select_str))
