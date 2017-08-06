#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2
import time
import redis
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import urlparse
import json
import config
import multiprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/49.0.2623.108 Chrome/49.0.2623.108 Safari/537.36'}

class TieBaClawer(object):

    def __init__(self):
        print "爬虫开始工作..."
        job_redis = redis.Redis(host=config.Redis_ip, port=config.Redis_port, db=config.Redis_db)
        self.job_redis = job_redis
        self.main()

    #获取全部帖子的总页面
    def search_all_page_url(self, tieba_name):
        start_url = 'http://tieba.baidu.com/f'
        payload = {'ie': 'utf-8', 'kw': str(tieba_name)}
        r = requests.get(start_url, params=payload)
        all_pages = ''
        if r.status_code == 200:
            time.sleep(2)
            bs = BeautifulSoup(r.text, 'html5lib')
            get_all_pages = bs.select('.pagination-default .last')[0].get('href')
            result = urlparse.urlparse(get_all_pages)
            parmas = urlparse.parse_qs(result.query, True)
            all_pages = int(parmas["pn"][0])
            print "共计页数为：", all_pages
        else:
            print "获取帖子列表失败"
            pass
        return all_pages

    # 获取某条贴吧信息的所有帖子链接
    def get_which_all_linkUrl(self, all_pages, tieba_name):
        start_url = 'http://tieba.baidu.com/f'
        host_url = 'http://tieba.baidu.com'
        for page in range(0, all_pages, 50):
            print page
            payload = {'ie': 'utf-8', 'kw': str(tieba_name), 'pn': page}
            res = requests.get(start_url, params=payload, timeout=20)
            print "当前页码为：", page, payload
            if res.status_code == 200:
                bs = BeautifulSoup(res.text, 'html5lib')
                get_which_all_links = bs.select("#thread_list .j_thread_list")
                for i in range(0, len(get_which_all_links), 1):
                    dataSet = get_which_all_links[i]['data-field']
                    tie_href = get_which_all_links[i].select('.threadlist_title .j_th_tit')[0]['href']
                    title = get_which_all_links[i].select('.threadlist_title .j_th_tit')[0].get('title')
                    msgData = json.JSONDecoder().decode(dataSet)
                    msgData['tie_href'] = host_url + tie_href
                    msgData['title'] = str(title)
                    # 将另外一份数据保存在mongo中
                    self.single_data_save_mysql(msgData)
                    # 一份保存在redis中，供爬虫调用
                    self.job_redis.sadd('urls', msgData['tie_href'])
            else:
                print "获取贴吧链接信息出错"
                pass

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

    # 获取某个帖子某页之前的所有楼层评论
    def get_all_judgement_info(self, item_link, beginPage, endPage):
        for page in range(beginPage, endPage + 1, 1):
            self.get_single_judgement_info(item_link, page)

    #获取要抓取的全部链接
    def get_tieba_list(self, tieba_name):
        #获取页码
        all_pages = self.search_all_page_url(tieba_name)
        self.get_which_all_linkUrl(all_pages, tieba_name)

    def main(self):
        tieba_name = "智能家具吧"

        #只有主进程执行获取列表操作，并将数据雪茹数据库和redis
        if config.identity == "master":
            # 主进程
            print "守护进程启动。。。"
            p1 = multiprocessing.Process(target=self.get_tieba_list(tieba_name))
            p1.daemon = False
            p1.start()

        print "10min后开始爬取帖子相信内容。。。"
        time.sleep(10)
        p2 = multiprocessing.Process(target=self.get_content())
        p2.daemon = True
        p2.start()

if __name__ == '__main__':
    TieBaClawer()
