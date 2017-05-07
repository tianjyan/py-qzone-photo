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
from common import logger

qq = 10000
print '正在登陆...'
logger = logger.Logger()
qz = qphoto.QzonePhoto(logger)
qz.login(10000, 'Password')
print '登录完成!'
common.set_queue(Queue.Queue())
common.set_main_thread_pending(False)
worker_count = 2
worker_list = []
while worker_count > 0:
    worker = Worker(logger)
    worker.setDaemon(False)
    worker.start()
    worker_count -= 1
    worker_list.append(worker)
qz.savephotos(qq)
logger.info(u'主线程已经将所有任务放到队列中')
common.set_main_thread_pending(True)
while True:
    done = True
    for worker in worker_list:
        if worker.isAlive():
            done = False
            break
    if done:
        logger.info(u'所有进程已经结束。')
        break

