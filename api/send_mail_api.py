# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/8/23 18:43
# File  : send_mail_api.py
# Software PyCharm


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from Ops.settings import SEND_ACCOUNT, ACCOUNT_PASSWD
#send_info="xxxxxxxOps平台欢迎xxx的加入.       \n\
#          平台访问地址:xxxx          \n\
#          您的账号：xxxxx           \n\
#          您的密码：xxxxx            \n"




def send_mail_message(rec, subject, send_msg):
    try:
        msg = MIMEText(send_msg, 'plain' , 'utf-8')
        msg['From'] = formataddr(["管理员<%s>"%SEND_ACCOUNT, SEND_ACCOUNT])
        msg['To'] = formataddr(["<%s>"%rec, rec])
        msg['Subject'] = subject

        server=smtplib.SMTP("smtphm.qiye.163.com", 25)
        rets=server.login(SEND_ACCOUNT, ACCOUNT_PASSWD)
        server.sendmail(SEND_ACCOUNT, [rec, ], msg.as_string())
        server.quit()
        print("邮件发送成功----^v^")
    except Exception as e:
        print("邮件发送失败----*v*")
        print(e)
#sender_account = "pay-opadmin@xxxxxxxxx.com"
#recevier_account = "hengjun.wei@xxxxxxxxx.com"
#send_mail_message(sender_account,recevier_account,send_info)

