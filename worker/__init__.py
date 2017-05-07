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
    def __init__(self, logger):
        threading.Thread.__init__(self)
        self.max_retry_count = 3
        self.max_deley_time = 1
        self.logger = logger

    def run(self):
        while True:
            if common.get_queue().empty():
                if common.get_main_thread_pending():
                    self.logger.info(u'所有任务已经完成，此线程将结束')
                    break
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
                    print u'%s秒后将重试' % self.max_deley_time
                    retry_count += 1
                    time.sleep(self.max_deley_time)
