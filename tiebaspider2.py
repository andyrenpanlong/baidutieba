#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import redis
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import urlparse
import config
import json
import multiprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class TieBaClawer(object):

    def __init__(self):
        print "爬虫开始工作..."
        job_redis = redis.Redis(host=config.Redis_ip, port=config.Redis_port, db=config.Redis_db)
        self.job_redis = job_redis
        self.main()

    #将单条数据存入mongo, 主要存储每条贴吧帖子的链接相关信息
    def single_data_save_mysql(self, dataObj):
        # 建立MongoDB数据库连接
        client = MongoClient(config.Mongodb_ip, config.Mongodb_port)
        # 连接所需数据库,admin为数据库名
        db = client.admin
        db.TieBaList2.insert(dataObj)

    # 获取某篇帖子的翻页页码
    def getTieZiPage(self, urlLink):
        r = requests.get(urlLink)
        all_pages = 0
        if r.status_code == 200:
            time.sleep(5)
            bs = BeautifulSoup(r.text, 'html5lib')
            if (bs.select('.l_reply_num')):
                all_pages = bs.select('.l_reply_num')[0].select('.red')[1].text or '1'
        else:
            print "获取页码失败"
        return int(all_pages)

    #获取正文
    def get_content(self):
        print "获取正文开始..."
        url = self.job_redis.spop('urls')
        while url:  # 当数据库还存在网页url，取出一个并爬取
            try:
                endPage = self.getTieZiPage(url)
                print endPage, url
                if (endPage == 0 or endPage == "0"):
                    print "该页面帖子已经被删除"
                    url = self.job_redis.spop('urls')
                    continue
                self.get_all_judgement_info(url, 1, endPage + 1)
            except: # 若出现网页读取错误捕获并输出
                print "获取正文页出错"
                pass
            url = self.job_redis.spop('urls')

    # 获取某个帖子某页之前的所有楼层评论
    def get_all_judgement_info(self, item_link, beginPage, endPage):
        for page in range(beginPage, endPage + 1, 1):
            self.get_single_judgement_info(item_link, page)

    # 获取每一篇帖子的某一页详细信息以及楼层评论
    def get_single_judgement_info(self, item_link, page):
        payload = {'pn': str(page)}
        # r=requests.get(item_link,proxies=proxy,timeout=15,params=payload)
        page_content = []
        r = requests.get(item_link, params=payload, timeout=15)
        time.sleep(1)
        if r.status_code == 200:
            bs = BeautifulSoup(r.text, 'html5lib')
            # 得到回复内容
            contents = bs.select('#j_p_postlist .l_post')
            for i in range(0, len(contents), 1):
                page_content.append(contents[i]['data-field'])
        else:
            print "请求错误，请调试请求！"
            pass
        self.divide_author_content(page_content)

    def divide_author_content(self, msgArr):
        # 建立MongoDB数据库连接
        client = MongoClient(config.Mongodb_ip, config.Mongodb_port)
        # 连接所需数据库,admin为数据库名
        db = client.admin
        for content in msgArr:
            msgData = json.JSONDecoder().decode(content)
            db.Content2.insert(msgData)
            print "抓取的数据为：", msgData


    # 获取某个帖子某页之前的所有楼层评论
    def get_all_judgement_info(self, item_link, beginPage, endPage):
        for page in range(beginPage, endPage + 1, 1):
            self.get_single_judgement_info(item_link, page)

    def main(self):
        self.get_content()

if __name__ == '__main__':
    TieBaClawer()
