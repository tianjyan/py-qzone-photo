#!/usr/bin/env python
# coding=utf-8

'''
实体类
Licensed to MIT
'''
from collections import namedtuple

Album = namedtuple('Album', ['uid', 'name', 'count'])
Photo = namedtuple('Photo', ['url', 'name', 'album'])
