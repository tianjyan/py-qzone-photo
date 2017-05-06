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
import random
from qqlib import qzone
import qqlib
from qphoto.model import Album, Photo
import common


class QzonePhoto(object):
    """
    查询QQ空间相册并下载的类。
    """

    # 地址更新来源：https://github.com/fooofei/py_qzone_photo
    albumbase = ('https://h5.qzone.qq.com/proxy/domain/tjalist.photo.qzone.qq.com/fcgi-bin/'
                 'fcg_list_album_v3?g_tk={gtk}&t={t}&hostUin={dest_user}&uin={user}&appid=4'
                 '&inCharset=gbk&outCharset=gbk&source=qzone&plat=qzone&format=jsonp&callbackFun=')
    photobase = ('https://h5.qzone.qq.com/proxy/domain/tjplist.photo.qzone.qq.com/fcgi-bin/'
                 'cgi_list_photo?g_tk={gtk}&t={t}&mode=0&idcNum=5&hostUin={dest_user}'
                 '&topicId={album_id}&noTopic=0&uin={user}&pageStart=0&pageNum=9000&inCharset=gbk'
                 '&outCharset=gbk&source=qzone&plat=qzone&outstyle=json&format=jsonp&json_esc=1')

    def __init__(self):
        self.cookie = None
        self.qzone_g_tk = None
        self.number = None
        self.session = None

    def login(self, number, password):
        """
        登录QQ。
        如果需要验证码，会保存验证码到本地，需要手动识别输入
        """
        request = qzone.QZone(number, password)
        try:
            request.login()
        except qqlib.NeedVerifyCode as exc:
            if exc.message:
                print('Error:', exc.message)
            verifier = exc.verifier
            open('verify.jpg', 'wb').write(verifier.fetch_image())
            print u'验证码已保存到verify.jpg'
            vcode = input('请输入验证码(带单引号)：')
            request.verifier.verify(vcode)
            request.login()
        self.session = request.session
        self.number = number
        self.qzone_g_tk = request.g_tk()

    def getablums(self, number):
        """
        获取相册集。
        可能会遇到未登录的错误，或者解码失败的错误。
        查询失败会返回一个空的集合。
        """
        ablums = list()
        requesturl = self.albumbase.format(
            gtk=self.qzone_g_tk, t=random.Random().random(), dest_user=number, user=self.number)
        content = None
        response = None
        try:
            response = self.session.get(requesturl, timeout=8)
            content = response.text
        except Exception:
            print u'获取{0}的相册集失败。'.format(number)
            traceback.print_exc()
            return ablums
        finally:
            if response:
                response.close()
        try:
            if content:
                content = content.replace('_Callback(', '')
                content = content.replace(');', '')
                content = json.loads(content)
                if 'data' in content and 'albumListModeClass' in content['data']:
                    for item in content['data']['albumListModeClass']:
                        for album in item['albumList']:
                            ablums.append(Album._make([album['id'], album['name'], album['total']]))
        except Exception:
            print u'转换{0}的相册集Json失败'.format(number)
            print content
            traceback.print_exc()
        return ablums

    def getphotosbyalbum(self, album, number):
        """
        获取相册。
        可能会遇到未登录的错误，或者解码失败的错误。
        """
        photos = list()
        requesturl = self.photobase.format(
            gtk=self.qzone_g_tk, t=random.Random().random(),
            dest_user=number, user=self.number, album_id=album.uid)
        content = None
        response = None
        try:
            response = self.session.get(requesturl, timeout=8)
            content = response.text
        except Exception:
            print u'获取{0}的相册失败。'.format(number)
            traceback.print_exc()
            return photos
        finally:
            if response:
                response.close()
        content = content.replace('_Callback(', '')
        content = content.replace(');', '')
        try:
            if content:
                content = content.replace('_Callback(', '')
                content = content.replace(');', '')
                content = json.loads(content)
                if 'data' in content and 'photoList' in content['data']:
                    for item in content['data']['photoList']:
                        url = ('origin_url' in item and item['origin_url'] or item['url'])
                        photos.append(Photo._make([url, item['name'], album]))
        except Exception:
            print u'转换{0}的相册集Json失败'.format(number)
            print content
            traceback.print_exc()
        return photos

    @classmethod
    def savephoto(cls, args):
        """
        保存图片
        """
        session, photo, number, index, count = args
        url = photo.url.replace('\\', '')
        print u'下载{0}第{1}个相册的第{2}张照片'.format(number, index, count)
        response = session.get(url, timeout=8)
        content = response.content
        folder = cls.getsavepath(number, index, photo.album.name)
        path = os.path.join(folder, u'{0}_{1}.jpeg'.format(count, photo.name))
        if not cls.ispathvalid(path):
            path = os.path.join(folder, u'{0}.jpeg'.format(count))
        with open(path, "wb") as stream:
            stream.write(content)
            stream.close()
        response.close()


    @classmethod
    def getsavepath(cls, number, index, albumname):
        """
        创建并返回保存图片的路径
        """
        base = os.path.join(os.getcwd(), u'qzonephoto')
        if not os.path.exists(base):
            os.mkdir(base)
        qqpath = os.path.join(base, u'{0}'.format(number))
        if not os.path.exists(qqpath):
            os.mkdir(qqpath)
        albumpath = os.path.join(qqpath, u'{0}_{1}'.format(index, albumname))
        if not cls.ispathvalid(albumpath):
            albumpath = os.path.join(qqpath, u'{0}'.format(index))
        if not os.path.exists(albumpath):
            os.mkdir(albumpath)
        return albumpath

    @classmethod
    def ispathvalid(cls, pathname):
        """
        路径是否有效
        http://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
        :param pathname:
        :return: bool
        """
        import errno
        import sys
        try:
            _, pathname = os.path.splitdrive(pathname)
            root = os.environ.get('HOMEDRIVE', 'C:') if sys.platform == 'win32' else os.path.sep
            root = root.rstrip(os.path.sep) + os.path.sep

            for pathname_part in pathname.split(os.path.sep):
                try:
                    os.lstat(root + pathname_part)
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == 123:
                            return False
                    elif exc.errno in [errno.ENAMETOOLONG, errno.ERANGE]:
                        return False
        except TypeError:
            return False
        else:
            return True

    def savephotos(self, number):
        """保存相册。
        查询相册并保存图片
        """
        print u'获取：{0}的相册信息'.format(number)
        ablums = self.getablums(number)
        if len(ablums) > 0:
            for index, ablum in enumerate(ablums):
                if ablum.count > 0:
                    photos = self.getphotosbyalbum(ablum, number)
                    for count, photo in enumerate(photos):
                        common.get_queue().put((self.savephoto,
                                                [(self.session,
                                                  photo,
                                                  number,
                                                  index + 1,
                                                  count + 1)]),
                                               block=True)
        else:
            print u'读取到得相册个数为0'
