#!/usr/bin/env python
# coding=utf-8

'''
实体类
Licensed to MIT
'''


class Album(object):
    """
    相册类
    """
    def __init__(self, uid, name, count):
        self.uid = uid
        self.name = name
        self.count = count


class Photo(object):
    """
    照片类
    """
    def __init__(self, url, name, album):
        self.url = url
        self.name = name
        self.album = album
