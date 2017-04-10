#!/usr/bin/env python
# coding=utf-8
# pylint: disable=W0703

'''
QQ空间相册查询下载模块
Licensed to MIT
'''

import json
import traceback
import urllib2
import os
from qqlib import qzone
import qqlib
from qphoto.model import Album, Photo
import common


class QzonePhoto(object):
    """
    查询QQ空间相册并下载的类。
    """

    albumbase1 = "http://photo.qq.com/fcgi-bin/fcg_list_album?uin="  # 如果没有设置密保的相册是通过这个地址访问的
    albumbase2 = "http://xalist.photo.qq.com/fcgi-bin/fcg_list_album?uin="  # 设置密保的相册是通过这个地址访问的
    photobase1 = "http://photo.qq.com/fcgi-bin/fcg_list_photo?uin="
    photobase2 = "http://xaplist.photo.qq.com/fcgi-bin/fcg_list_photo?uin="

    def __init__(self):
        self.cookie = None

    def login(self, number, password):
        """登录QQ。
        如果需要验证码，会保存验证码到本地，需要手动识别输入
        """
        request = qzone.QQ(number, password)
        try:
            request.login()
        except qqlib.NeedVerifyCode as exc:
            if exc.message:
                print('Error:', exc.message)
            verifier = exc.verifier
            open('verify.jpg', 'wb').write(verifier.fetch_image())
            print u'验证码已保存到verify.jpg'
            # 输入验证码
            vcode = input(u'请输入验证码：')
            verifier.verify(vcode)
            request.login()
        cookie = request.session.cookies
        cookies = 'ptisp={0}; RK={1}; ptcz={2};pt2gguin={3}; uin={4}; skey={5}'.format(
            cookie['ptisp'], cookie['RK'], cookie['ptcz'], cookie['pt2gguin'], cookie['uin'], cookie['skey'])
        self.cookie = cookies

    def getablums(self, number):
        """获取相册集。
        可能会遇到未登录的错误，或者解码失败的错误。
        查询失败会返回一个空的集合。
        """
        ablums = list()
        requesturl = self.albumbase1 + str(number) + "&outstyle=2"
        # print u'相册集地址:' + requesturl
        request = urllib2.Request(requesturl)
        request.add_header('Cookie', self.cookie)
        content = None
        response = None
        try:
            response = urllib2.urlopen(request, timeout=10)
            content = response.read().decode('gbk')
        except Exception:
            print u'获取相册集失败:qq-%s' % number
            traceback.print_exc()
            return ablums
        finally:
            if response is not None:
                response.close()
        content = content.replace('_Callback(', '')
        content = content.replace(');', '')
        try:
            if 'album' in json.loads(content):
                for i in json.loads(content)['album']:
                    ablums.append(Album(i['id'], i['name'], i['total']))
        except Exception:
            print u'转换相册集Json失败:qq-%s' % number
            print content
            traceback.print_exc()
        return ablums

    def getphotosbyalbum(self, album, number):
        """获取相册。
        可能会遇到未登录的错误，或者解码失败的错误。
        """
        photos = list()
        requesturl = self.photobase1 + str(number) + "&albumid=" + album.uid + "&outstyle=json"
        # print u'相册地址:' +  requesturl
        request = urllib2.Request(requesturl)
        request.add_header('Cookie', self.cookie)
        content = None
        response = None
        try:
            response = urllib2.urlopen(request, timeout=10)
            content = response.read().decode('gbk')
        except Exception:
            print u'获取相册失败:qq-%s' % number
            traceback.print_exc()
            return photos
        finally:
            if response is not None:
                response.close()
        content = content.replace('_Callback(', '')
        content = content.replace(');', '')
        try:
            if 'pic' in json.loads(content):
                for i in json.loads(content)['pic']:
                    photos.append(Photo(i['url'], i['name'], album))
        except Exception:
            print u'转换相册Json失败:qq-%s' % number
            print content
            traceback.print_exc()
        return photos

    @classmethod
    def savephoto(cls, args):
        """保存图片。
        保存到工作目录下的qzonephoto文件夹下。
        格式：QQ号_相册编号_图片编号.jpeg
        """
        photo, index = args
        print u'下载文件:' + index
        # print u'文件地址:' + photo.url
        url = photo.url.replace('\\', '')
        response = urllib2.urlopen(url, timeout=10)
        data = response.read()
        response.close()
        downloadfolder = os.path.join('qzonephoto', photo.album.name)
        if not os.path.exists(downloadfolder):
            os.mkdir(downloadfolder)
        with open(os.path.join(downloadfolder , photo.name + '.jpeg'), "wb") as code:
            code.write(data)
            code.close()

    def savephotos(self, number):
        """保存相册。
        查询相册并保存图片
        """
        print u'获取：' + str(number) + u'的相册信息'
        ablums = self.getablums(number)
        if len(ablums) > 0:
            for i, ablum in enumerate(ablums):
                if ablum.count > 0:
                    photos = self.getphotosbyalbum(ablum, number)
                    for index, photo in enumerate(photos):
                        common.get_queue().put(
                            (self.savephoto, [(photo, str(index))]), block=True)
        else:
            print u'读取到得相册个数为0'
