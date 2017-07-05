# coding:utf-8
from urllib import request, parse


def control_spider(url, data):
    encode_data = parse.urlencode(data)
    req = request.Request(url=url, data=encode_data.encode('utf-8'))
    req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    response = request.urlopen(req)
    print(encode_data)
    print(response.read().decode('utf-8'))

if __name__ == '__main__':
    url = "http://localhost:6800/schedule.json"
    data = {
        'project': 'gaode',
        'spider': 'gaode',
        'province': '湖北省'.encode('unicode-escape'),
        'city_list': ''.encode('unicode-escape'),
        'tags': '061400;061401;060411',
        'table_name': 'web_1',
        'keywords': ""
    }
    control_spider(url, data)