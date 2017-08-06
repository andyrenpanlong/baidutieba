#coding=utf-8

import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import urlparse
import json
import redis
import config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

job_redis = redis.Redis(host=config.Redis_ip, port=config.Redis_port, db=config.Redis_db)

def search_all_page_url(tieba_name):
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
        print "页面信息获取失败"
    return all_pages

# 获取某条贴吧信息的所有帖子链接
def get_which_all_linkUrl(all_pages, tieba_name):
    start_url = 'http://tieba.baidu.com/f'
    host_url = 'http://tieba.baidu.com'
    for page in range(0, all_pages, 50):
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
                print "adawda:", msgData
                # 将另外一份数据保存在mongo中
                single_data_save_mysql(msgData)
                # 一份保存在redis中，供爬虫调用
                job_redis.sadd('urls', msgData['tie_href'])
        else:
            print "请求出错"


def single_data_save_mysql(dataObj):
    #建立MongoDB数据库连接
    client = MongoClient('127.0.0.1', 27017)
    #连接所需数据库,test为数据库名
    db = client.admin
    db.TieBaList2.insert(dataObj)

def mainSpider(tieba_name):
    all_pages = search_all_page_url(tieba_name)
    get_which_all_linkUrl(all_pages, tieba_name)

#先启动这个，优先获取列表
# mainSpider("智能家居吧")
mainSpider("人工智能吧")