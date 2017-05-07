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

def set_main_thread_pending(value):
    """
    设置主线程是否已经处于等待状态
    """
    global ISPENDING
    ISPENDING = value

def get_main_thread_pending():
    """
    获取主线程是否已经处于等待状态
    """
    return ISPENDING
