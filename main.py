#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103

'''
批量下载入口函数
Licensed to MIT
'''

import sys
import time
import Queue
import qphoto
from worker import Worker
import common
from common import logger

reload(sys)
sys.setdefaultencoding('utf-8')
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
# qz.savephotos(qq)
# logger.info(u'主线程已经将所有任务放到队列中')
# common.set_main_thread_pending(True)
while True:
    if common.get_queue().empty():
        time.sleep(1)
        qq = input(u'请输入需要保存相册的QQ号:')
        qz.savephotos(qq)
