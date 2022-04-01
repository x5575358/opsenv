# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/26 16:53
# File  : celery.py
# Software PyCharm

from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery_proj' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ops.settings')
app = Celery('release')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
