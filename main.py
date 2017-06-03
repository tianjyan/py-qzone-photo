#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103

'''
批量下载入口函数
Licensed to MIT
'''

import os
import json
import Queue
import qphoto
from worker import Worker
import common
from common import logger

logger = logger.Logger()
logger.info(u'Logger初始化完成')
logger.info(u'读取配置文件')
confileFileName = os.environ.get('env')
if confileFileName is None:
    confileFileName = 'config.json'
configFile = file(confileFileName)
config = json.load(configFile)
configFile.close()
logger.info(u'读取配置文件完成')
qz = qphoto.QzonePhoto(logger)
logger.info(u'登陆QQ:{}'.format(config['account']))
qz.login(config['account'], config['password'])
logger.info(u'登陆完成')
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
qz.savephotos(config['target_qq'])
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
