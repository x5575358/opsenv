Ops 版本0.0.1

软件版本：

    boto3==1.7.47
    celery==3.1.25
    celery-with-redis==3.0
    configparser==3.5.0
    Django==1.11.4
    django-celery==3.1.17
    PyMySQL==0.8.1
    redis==2.10.6
    pymongo==3.7.1
    uWSGI==2.0.17.1
    docker==3.5.0
    docker-pycreds==0.3.0

    
Ops结构：

    Ops平台结构
    |
    |____首页(v0.0.2)
    |   |
    |   |_____堆叠图
    |   |       |_____资源信息统计图
    |   |_____柱形图
    |   |       |_____资源统计Ec2实例规格top10
    |   |       |____集群、仓库、容器、标签
    |   |_____折线图
    |   |       |____一周访问排名图
    |   |_____圆饼图
    |           |____Ec2资源环境分布
    |
    |____用户管理(v0.0.2)
    |   |_____用户管理
    |   |       |_____权限分配
    |   |       |_____权限列表
    |   |_____用户组
    |           |_____权限分配
    |           |_____权限列表
    |
    |____资源信息(v0.0.3)
    |   |_____Ec2
    |   |_____Alb
    |   |_____Rds
    |
    |____持续集成
    |   |_____GitLab  
    |   |   |_____代码提交
    |   |   |_____配置修改
    |   |_____Jenkins
    |   |   |_____代码构建
    |   |_____Harbor
    |   |   |_____项目：项目列表、项目半自动同步(v0.0.1)
    |   |   |_____镜像仓库：仓库列表、仓库半自动同步(v0.0.1)
    |   |   |_____镜像标签：标签列表、标签半自动同步(v0.0.1)
    |   |_____Report
    |   |   |_____Ec2资源消耗
    |
    |____容器管理
    |   |_____容器分布(v0.0.1)
    |   |_____环境(v0.0.3)
    |   |_____环境组(v0.0.3)
    |
    |____发布管理
    |   |_____对比容器：容器对比结果列表、差异容器直接发布升级(v0.0.1)
    |   |_____hosts列表：ansible hosts主机信息列表(v0.0.1)
    |   |_____发布任务：新增升级任务(v0.0.1)
    |   |_____历史发布(v0.0.1)
    |
    |____变更管理
    |   |_____封版、发布
    |   |_____变更申请
    |
    |____工具管理(v0.0.3)
    |   |_____工具列表(v0.0.3)
    |   |_____脚本上传(v0.0.3)
    |   |_____脚本封装(v0.0.3)
    |
    |____审计(v0.0.2)
    |   |_____登陆日志(v0.0.2)
    |   |_____操作日志(v0.0.2)
    |   |_____异步日志(v0.0.2)
    |   |_____重启日志(v0.0.3)
    |   |_____脚本日志(v0.0.3)

编码风格(PEP8)

编码规范：

    类名:以名词命名，首写字母大写。
    变量名：以小写字母，单词之间用下划线分割。
    常量：大写。
    Imports 导入
    导入应该按照以下顺序分组：
        标准库导入
        相关第三方库导入
        本地 应用/库特定导入
        你应该在每一组导入之间加入空行。
        
