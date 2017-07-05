# coding : utf-8

from urllib import request, parse, error
import socket
socket.setdefaulttimeout(10)

url = 'http://www.ip181.com/'
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/53.0.2785.143 Safari/537.36"
headers = {
    'User-Agent': user_agent
}

req = request.Request(url=url, headers=headers)
proxy_handler = request.ProxyHandler({'http': '218.247.161.37:80'})
opener = request.build_opener(proxy_handler)
request.install_opener(opener=opener)
try:
    response = request.urlopen(req)
    html = response.read()
    print(html.decode('gb2312'))
except error.HTTPError as e:
    print(e.code)
    print(e.read())
except socket.error as e:
    print('time out')

