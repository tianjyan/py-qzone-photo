#!/usr/bin/env python
# coding=utf-8
# pylint: disable=W0703

'''
任务执行重试模块
Licensed to MIT
'''

import time
import traceback
import Queue
import threading
import common


class Worker(threading.Thread):
    """
    任务重试和执行的类。
    """
    def __init__(self, logger, maxretrycount=3, maxdeleytime=1):
        threading.Thread.__init__(self)
        self.max_retry_count = maxretrycount
        self.max_deley_time = maxdeleytime
        self.logger = logger

    def run(self):
        while True:
            if common.get_queue().empty():
                # if common.get_main_thread_pending():
                #     self.logger.info(u'所有任务已经完成，此线程:{0}将结束'.format(self.getName()))
                #     break
                continue
            action, arg = common.get_queue().get(block=True)
            retry_count = 0
            while retry_count <= self.max_retry_count:
                try:
                    action(*arg)
                    self.logger.info(u'下载队列中剩余的任务个数为{0}'.format(common.get_queue().qsize()))
                    break
                except Exception:
                    traceback.print_exc()
                    self.logger.info(u'{0}秒后将重试'.format(self.max_deley_time))
                    retry_count += 1
                    time.sleep(self.max_deley_time)
