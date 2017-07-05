# coding:utf-8
from urllib import request
from bs4 import BeautifulSoup


url = "http://music.baidu.com/top/dayhot?qq-pf-to=pcqq.group"

req = request.Request(url)
response = request.urlopen(req)
soup = BeautifulSoup(response.read(), 'lxml', from_encoding='utf-8')
for i in soup.select('a'):
    print(i.get_text())
