#!/usr/bin/env python
# coding=utf-8
# pylint: disable=W0703
# pylint: disable=W1401
# pylint: disable=E1101

'''
QQ空间相册查询下载模块
Licensed to MIT
'''

import json
import traceback
import urllib2
import os
import random
import re
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

    def __init__(self, logger):
        self.logger = logger
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
            vcode = input('验证码已保存到verify.jpg，请输入验证码(带单引号)：')
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
            self.logger.error(u'获取{0}的相册集失败。地址: {1}'.format(number, requesturl))
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
                if 'data' in content and 'mode' in content['data']:
                    mode = content['data']['mode']
                    if mode == 2:
                        ablums = self.getablumssortbylist(number, content)
                    elif mode == 3:
                        ablums = self.getablumssortbyclass(number, content)
                    else:
                        self.logger.error(u'无法识别{0}的排序模式: {1}'.format(number, content))
                else:
                    self.logger.error(u'无法识别{0}的Json格式: {1}'.format(number, content))
        except Exception:
            self.logger.error(u'转换{0}的相册集Json失败。Json内容: {1}'.format(number, content))
            traceback.print_exc()
        return ablums

    def getablumssortbylist(self, number, content):
        """
        解析普通视图分类
        """
        self.logger.debug(u'以普通视图分类方式获取{0}的相册。{1}'.format(number, content))
        ablums = list()
        if 'albumListModeSort' in content['data']:
            for item in content['data']['albumListModeSort']:
                ablums.append(Album._make([item['id'], item['name'], item['total']]))
        return ablums

    def getablumssortbyclass(self, number, content):
        """
        解析分组视图分类
        """
        self.logger.debug(u'以分类视图分类方式获取{0}的相册。{1}'.format(number, content))
        ablums = list()
        if 'albumListModeClass' in content['data']:
            for item in content['data']['albumListModeClass']:
                if 'albumList' in item and item['albumList']:
                    for album in item['albumList']:
                        ablums.append(Album._make([album['id'], album['name'], album['total']]))
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
            self.logger.error('获取{0}的相册失败。地址：{1}'.format(number, requesturl))
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
            self.logger.error('转换{0}的相册集Json失败。Json内容：{1}'.format(number, content))
            traceback.print_exc()
        return photos

    @classmethod
    def savephoto(cls, args):
        """
        保存图片
        """
        logger, session, photo, number, index, count = args
        url = photo.url.replace('\\', '')
        folder = cls.getsavepath(number, index, photo.album.name)
        fixname = re.sub('[\\\/:*?"<>|]', '-', photo.name)
        path = os.path.join(folder, u'{0}_{1}.jpeg'.format(count, fixname))
        if os.path.exists(path):
            logger.info(u'{0}第{1}个相册的第{2}张照片已经存在。相册名：{3}，照片名：{4}'.format(
                number, index, count, photo.album.name, photo.name))
            return
        logger.info(u'下载{0}第{1}个相册的第{2}张照片。相册名：{3}，照片名：{4}'.format(
            number, index, count, photo.album.name, photo.name))
        response = session.get(url, timeout=8)
        content = response.content
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
        fixname = re.sub('[\\\/:*?"<>|]', '-', albumname)
        albumpath = os.path.join(qqpath, u'{0}_{1}'.format(index, fixname))
        if not os.path.exists(albumpath):
            os.mkdir(albumpath)
        return albumpath

    def savephotos(self, number, maxphotocount=0):
        """保存相册。
        查询相册并保存图片
        """
        photocount = 0
        self.logger.info(u'获取：{0}的相册信息。'.format(number))
        ablums = self.getablums(number)
        if len(ablums) > 0:
            for index, ablum in enumerate(ablums):
                if ablum.count > 0:
                    photos = self.getphotosbyalbum(ablum, number)
                    for count, photo in enumerate(photos):
                        if maxphotocount is not 0 and photocount >= maxphotocount:
                            self.logger.info(u'已经达到指定的最大下载个数:{0}'.format(photocount))
                            return
                        if common.get_queue().qsize() >= 1000:
                            self.logger.info(u'队列任务书已经达到1000，等待执行完后再继续')
                            while True:
                                if common.get_queue().qsize() <= 500:
                                    break
                        common.get_queue().put((self.savephoto,
                                                [(self.logger,
                                                  self.session,
                                                  photo,
                                                  number,
                                                  index + 1,
                                                  count + 1)]),
                                               block=True)
                        photocount += 1
            self.logger.info(u'已经将{0}的照片放到下载队列中。'.format(number))
        else:
            self.logger.info(u'获取：{0}的相册信息的个数为0。'.format(number))
