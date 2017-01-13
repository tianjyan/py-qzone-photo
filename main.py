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
worker = Worker()
worker.setDaemon(True)
worker.start()
while True:
    qz.savephotos(qq)
    qq += 1
