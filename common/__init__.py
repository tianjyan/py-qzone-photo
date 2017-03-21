#!/usr/bin/env python
# coding=utf-8
# pylint: disable=W0601

'''
全局变量类
Licensed to MIT
'''


def set_queue(value):
    """
    设置工作队列。
    """
    global WORKQUEUE
    WORKQUEUE = value


def get_queue():
    """
    获取工作队列。
    """
    return WORKQUEUE
