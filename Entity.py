# -*- coding:utf-8 -*-
__author__ = 'young'

album1 = "http://alist.photo.qq.com/"
album2 = "http://xalist.photo.qq.com/"

albumbase1 = "http://alist.photo.qq.com/fcgi-bin/fcg_list_album?uin="#如果没有设置密保的相册是通过这个地址访问的
albumbase2 = "http://xalist.photo.qq.com/fcgi-bin/fcg_list_album?uin="#//设置密保的相册是通过这个地址访问的

photo1 = "http://plist.photo.qq.com/"
photo2 = "http://xaplist.photo.qq.com/"
photobase1 = "http://plist.photo.qq.com/fcgi-bin/fcg_list_photo?uin="
photobase2 = "http://xaplist.photo.qq.com/fcgi-bin/fcg_list_photo?uin="

#savepath = "/Users/young/downloads/qqPhoto" #图片保存位置的父目录
savepath = 'C:\Users\young\Desktop'

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


