# -*- encoding:UTF-8 -*-
import requests

print '\xbe\xdc\xbe\xf8\xb7\xc3\xce\xca\xa1\xa3'.decode("gbk")
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


urls = [
    "https://imtt.dd.qq.com/16891/80B6C15AD0AC33A4F3E2C8E2445CA703.apk?fsname=com.taobao.taobao_8.3.10_223.apk",
    "https://imtt.dd.qq.com/16891/371C7C353C7B87011FB3DE8B12BCBCA5.apk?fsname=com.tencent.mm_7.0.0_1380.apk",
    "https://imtt.dd.qq.com/16891/FEA3304FC9D84ADBF9F44BD542A9FD3E.apk?fsname=com.baidu.searchbox_11.2.0.10_46662912.apk",
    "https://imtt.dd.qq.com/16891/B82FD7E2F759060B05E2D486364BE1D0.apk?fsname=com.tencent.mobileqq_7.9.5_980.apk",
]
# for x in range(1000):
#     for url in urls:
#         resp = GET(url=url)
#         with open("a.apk", "wb") as application:
#             application.write(resp.content)
#         print x

resp = GET(url=urls[2])
print resp.headers
print resp.is_redirect
# print [resp.content]
