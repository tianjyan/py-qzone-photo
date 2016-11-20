# -*- coding:utf-8 -*-
__author__ = 'young'

import untils
import Entity
from qqlib import qzone

qq = 12345678
while True:
    qzone = qzone.QZone(Entity.loginQQ, Entity.loginPassword)
    qzone.login()
    cookie = qzone.session.cookies
    cookieStr = 'ptisp={0}; RK={1}; ptcz={2}; pt2gguin={3}; uin={4}; skey={5}'.format(cookie['ptisp'],cookie['RK'],cookie['ptcz'],cookie['pt2gguin'],cookie['uin'],cookie['skey'])
    print cookieStr
    untils.savePhotos(str(qq), cookieStr)
    break
    ##qq += 1



