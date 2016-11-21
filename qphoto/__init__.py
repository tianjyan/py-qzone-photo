#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C1001
# pylint: disable=R0903
'''
Qzone Photo Download module
'''

import json
import urllib2
import os
from qqlib import qzone
import qqlib

class QzonePhoto:

    albumbase1 = "http://alist.photo.qq.com/fcgi-bin/fcg_list_album?uin="#如果没有设置密保的相册是通过这个地址访问的
    albumbase2 = "http://xalist.photo.qq.com/fcgi-bin/fcg_list_album?uin="#//设置密保的相册是通过这个地址访问的
    photobase1 = "http://plist.photo.qq.com/fcgi-bin/fcg_list_photo?uin="
    photobase2 = "http://xaplist.photo.qq.com/fcgi-bin/fcg_list_photo?uin="

    def __init__(self):
        self.cookie = None

    def login(self, qqNumber, password):
        qq = qzone.QQ(qqNumber, password)
        try:
            qq.login()
        except qqlib.NeedVerifyCode as e:
            # 需要验证码
            verifier = e.verifier
            open('verify.jpg', 'wb').write(verifier.image)
            print '验证码已保存到verify.jpg'
            vcode = input('请输入验证码：')
            try:
                verifier.verify(vcode)
            except qqlib.VerifyCodeError as e:
                print '验证码错误！'
                raise e
            else:
                qq.login()
        cookie = qq.session.cookies
        cookieStr = 'ptisp={0}; RK={1}; ptcz={2};\
                    pt2gguin={3}; uin={4}; skey={5}'.\
                    format(cookie['ptisp'], cookie['RK'], cookie['ptcz'],\
                    cookie['pt2gguin'], cookie['uin'], cookie['skey'])
        self.cookie = cookieStr

    def getAblums(self, qqNumber):
        ablums = list()
        requestUrl = self.albumbase1 + str(qqNumber) + "&outstyle=2"
        print requestUrl
        request = urllib2.Request(requestUrl)
        response = urllib2.urlopen(request, timeout=10)
        content = response.read().decode('gbk')
        response.close()
        content = content.replace('_Callback(', '')
        content = content.replace(');', '')
        if 'album' in json.loads(content):
            for i in json.loads(content)['album']:
                ablums.append(Album(i['id'], i['name'], i['total']))
        return ablums

    def getPhotosByAlum(self, album, qqNumber):
        photos = list()
        requestUrl = self.photobase1 + str(qqNumber) + "&albumid=" + album.ID + "&outstyle=json"
        print requestUrl
        request = urllib2.Request(requestUrl)
        request.add_header('Cookie', self.cookie)
        response = urllib2.urlopen(request, timeout=10)
        content = response.read().decode('gbk')
        response.close()
        content = content.replace('_Callback(', '')
        content = content.replace(');', '')
        if 'pic' in json.loads(content):
            for i in json.loads(content)['pic']:
                photos.append(Photo(i['url'], i['name'], album))
        return photos

    def saveImage(self, photo, qqNumber, index):
        print index, photo.URL
        url = photo.URL.replace('\\', '')
        response = urllib2.urlopen(url, timeout=10)
        data = response.read()
        response.close()
        downloadFolder = os.getcwd()+os.path.sep+'qzonephoto'
        if not os.path.exists(downloadFolder):
            os.mkdir(downloadFolder)
        targetFolder = downloadFolder+os.path.sep+str(qqNumber)
        if not os.path.exists(targetFolder):
            os.mkdir(targetFolder)
        with open(targetFolder + os.path.sep + index + '.jpeg', "wb") as code:
            code.write(data)
            code.close()

    def savePhotos(self, qqNumber):
        print u'获取：'+str(qqNumber)+u'的相册信息'
        ablums = self.getAblums(qqNumber)
        if len(ablums) > 0:
            for i, a in enumerate(ablums):
                if a.Count > 0:
                    print u'开始下载第'+str(i+1)+u'个相册'
                    photos = self.getPhotosByAlum(a, qqNumber)
                    for index, p in enumerate(photos):
                        self.saveImage(p, qqNumber, str(i)+'_'+str(index))
                    print u'第'+str(i+1)+u'个相册下载完成'
        else:
            print u'读取到得相册个数为0'

class Album:
    def __init__(self, uid, name, count):
        self.ID = uid
        self.Name = name
        self.Count = count


class Photo:
    def __init__(self, url, name, album):
        self.URL = url
        self.Name = name
        self.Album = album
