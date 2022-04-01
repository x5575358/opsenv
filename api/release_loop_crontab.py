# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/20 16:36
# File  : loop_crontab.py
# Software PyCharm

from api.open_api import DbOperator,read_file,bash
#from Ops.settings import DB_HOST,DB_DATABASE,DB_PORT,DB_USER,DB_PASSWORD

DB_HOST="xxxxxxx"
DB_PORT=8500
DB_USER="devuser"
DB_PASSWORD="Dev123456!"
DB_DATABASE="ops"


# DB_HOST="localhost"
# DB_PORT=8500
# DB_USER="root"
# DB_PASSWORD="mysql"
# DB_DATABASE="ops"

db=DbOperator(DB_HOST,DB_DATABASE,DB_PORT,DB_USER,DB_PASSWORD)

def update_async(status, param):
    asy_update = "UPDATE release_asyncrecord set release_status=%s WHERE file_path=\"%s\";" %(str(status),str(param))
    db.update_or_delete_param(asy_update)


def update_affirm(status, param):
    affirm_update = "UPDATE release_affirminfo set release_status=%s WHERE id=\"%s\";" %(str(status),str(param))
    db.update_or_delete_param(affirm_update)


def update_task(status, param):
    task_update = "UPDATE release_taskinfo set release_status=%s WHERE id=\"%s\";"%(str(status),str(param))
    db.update_or_delete_param(task_update)


sql="select asy.file_path,asy.affirm_id_id, a.ftaskinfo_id,\
    a.ip,TIMESTAMPDIFF(SECOND,asy.creation_time,asy.update_time),\
    TIMESTAMPDIFF(SECOND,asy.update_time,NOW()),t.warehouse_tags from release_asyncrecord \
    asy LEFT JOIN release_affirminfo  a ON a.id = asy.affirm_id_id \
    LEFT JOIN release_taskinfo t ON a.ftaskinfo_id=t.id \
    where asy.release_status >= 2;"

double_list_ret=db.query_result(sql)
for o  in double_list_ret:
    file_path = o[0]
    affirm_id = o[1]
    task_id=o[2]
    distance_now_time=o[5]
    if distance_now_time > 7200:
        update_async(4, file_path)
        update_affirm(3, affirm_id)
        update_task(5,task_id)
        continue
    #end_word="connection to %s closed."%o[3]
    end_word="to %s closed."%o[3]
    f_content=read_file(file_path)
    if end_word in f_content and "SUCCESS" in f_content:
        #print("执行成功")
#        warehouse_tags = o[6].replace("[","").replace("]","").split(";")
#        for tags in warehouse_tags:
#            str_result = str(tags)
#            check_order=" docker ps|grep %s |wc -l"%str_result
#            ret_code=bash(check_order)
#            if "1" == ret_code:
#                update_async(0, file_path)
#                update_affirm(0, affirm_id)
#                update_task(0, task_id)
#            else:
#                update_async(1, file_path)
#                update_affirm(1, affirm_id)
#                update_task(4, task_id)
         update_async(0, file_path)
         update_affirm(0, affirm_id)
         update_task(0, task_id)
    elif end_word in f_content and "FAILED" in f_content:
       # print("执行失败")
       # print(f_content)
       # print("-------->>>>执行失败<<<<--------")
        update_async(1, file_path)
        update_affirm(1, affirm_id)
        update_task(4, task_id)
    elif end_word not in f_content or "FAILED" in f_content:
    #    print("1执行失败")
     #   print(f_content)
      #  print("-111------->>>>执行失败<<<<--------")
        update_async(1, file_path)
        update_affirm(1, affirm_id)
        update_task(4, task_id)

db.close_db()
