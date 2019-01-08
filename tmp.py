# -*- encoding:UTF-8 -*-
import requests

headers = {'Accept': '*/*',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'Cache-Control': 'max-age=0',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
           'Connection': 'keep-alive',
           'Referer': 'http://www.baidu.com/'
           }


def POST(url, data):
    session = requests.Session()
    session.headers = headers
    resp = session.post(url=url, data=data)
    return resp


def GET(url):
    session = requests.Session()
    session.headers = headers
    resp = session.get(url=url)
    return resp


import urllib
import sys


def report(count, blockSize, totalSize):
    if totalSize < 4000:
        return False
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write("\r%d%%" % percent + ' complete')
    sys.stdout.flush()


urls = [
    "https://imtt.dd.qq.com/16891/8AC244815C2FA8D472AC19EFF184F17A.apk?fsname=com.gui.gui.chen.flash.light.one_2.3.4_234.apk",
    "https://dc2d8d5b0b9641aa7fb44379ca67b370.dd.cdntips.com/imtt.dd.qq.com/16891/8AC244815C2FA8D472AC19EFF184F17A.apk?mkey=5c342f5ede468b66&f=0ce9&fsname=com.gui.gui.chen.flash.light.one_2.3.4_234.apk&cip=222.70.173.147&proto=https"
]
resp = GET(url=urls[1])
print resp.headers
print resp.cookies



# for x in range(1000):
#     for url in urls:
#         resp = GET(url=url)
#         with open("a.apk", "wb") as application:
#             application.write(resp.content)
#          print x
for x in range(10000):
    print x
    print '\n'
    urllib.urlretrieve(urls[1], 'a,apk', report)

# # print [resp.content]
