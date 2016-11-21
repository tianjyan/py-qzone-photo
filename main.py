#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C1001
# pylint: disable=R0903

import qphoto

qq = 10000
print '正在登陆...'
qz = qphoto.QzonePhoto()
qz.login(12345678, 'password')
print '登录完成!'
while True:
    qz.savePhotos(qq)
    qq += 1
