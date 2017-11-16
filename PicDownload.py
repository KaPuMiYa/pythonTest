# 简易爬虫抓取图片
import re
from urllib import request


def getHtml(url):
    page = request.urlopen(url)
    html = page.read()
    return html


def getImage(html):
    # 正则判断图片img的URL地址
    reg = r'src="(.+?\.jpg)" pic_ext'
    imagePattern = re.compile(reg)
    html = html.decode('utf-8')
    imgList = re.findall(imagePattern, html)
    index = 0
    for imgUrl in imgList:
        # 直接将远程数据下载到本地
        request.urlretrieve(imgUrl, 'D://Java//pythonSpace//PythonTest1//img//%s.jpg' % index)
        index += 1
        print(index)


html = getHtml("https://tieba.baidu.com/p/2460150866")
print(getImage(html))
