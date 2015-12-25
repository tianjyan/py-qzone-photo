# -*- coding:utf-8 -*-
__author__ = 'young'

import json
import urllib2
import os

import Entity


def getAblums(qq, url):
    ablums = list()
    print url + qq + "&outstyle=2"
    request = urllib2.Request(url + qq + "&outstyle=2")
    f = urllib2.urlopen(request, timeout=10)
    response = f.read().decode('gbk')
    f.close()
    response = response.replace('_Callback(', '')
    response = response.replace(');', '')
    #print response
    if 'album' in json.loads(response):
        for i in json.loads(response)['album']:
            ablums.append(Entity.Album(i['id'], i['name'], i['total']))
    return ablums


def getPhotosByAlum(album, qq, url):
    photos = list()
    print url + qq + "&albumid=" + album.ID + "&outstyle=json"
    request = urllib2.Request(url + qq + "&albumid=" + album.ID + "&outstyle=json")
    f = urllib2.urlopen(request, timeout=10)
    response = f.read().decode('gbk')
    f.close()
    response = response.replace('_Callback(', '')
    response = response.replace(');', '')
    #print response
    if 'pic' in json.loads(response):
        for i in json.loads(response)['pic']:
            photos.append(Entity.Photo(i['url'], i['name'], album))
    return photos


def saveImage(path, photo, qq, index):
    print index, photo.URL
    url = photo.URL.replace('\\', '')
    f = urllib2.urlopen(url, timeout=10)
    data = f.read()
    f.close()
    if not os.path.exists(path+os.path.sep+qq):
        os.mkdir(path+os.path.sep+qq)
    with open(path+os.path.sep+qq+os.path.sep + index + '.jpeg', "wb") as code:
        code.write(data)
        code.close()


def savePhotos(qq, path=Entity.savepath):
    print u'获取：'+qq+u'的相册信息'
    ablums = getAblums(qq, Entity.albumbase2)
    if len(ablums) > 0:
        for i, a in enumerate(ablums):
            if a.Count > 0:
                print u'开始下载第'+str(i+1)+u'个相册'
                photos = getPhotosByAlum(a, qq, Entity.photobase2)
                for index, p in enumerate(photos):
                    saveImage(path, p, qq, str(i)+'_'+str(index))
                print u'第'+str(i+1)+u'个相册下载完成'
    else:
        print u'读取到得相册个数为0'