#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import urlparse

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


print search_all_page_url("智能家具吧")