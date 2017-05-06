#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103

'''
批量下载入口函数
Licensed to MIT
'''

import Queue
import qphoto
from worker import Worker
import common

qq = 10000
print '正在登陆...'
qz = qphoto.QzonePhoto()
qz.login(10000, 'Password')
print '登录完成!'
common.set_queue(Queue.Queue())
worker_count = 2
while worker_count > 0:
    worker = Worker()
    worker.setDaemon(False)
    worker.start()
    worker_count -= 1
qz.savephotos(qq)
while True:
    pass
