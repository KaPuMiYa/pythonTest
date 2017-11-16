# 抓取糗事百科页面内容
import re
from urllib import request
from urllib.error import URLError


class BaiKe:
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-agent': self.user_agent}
        self.storiesList = []
        self.enable = False

    # 获取页面HTML内容
    def getPageHtml(self, pageIndex):
        try:
            url = 'http://www.qiushibaike.com/8hr/page/' + str(pageIndex)
            req = request.Request(url, headers=self.headers)
            response = request.urlopen(req)
            pageCode = response.read().decode('utf-8')
            return pageCode
        except URLError as e:
            if hasattr(e, "reason"):
                print("连接失败原因：", e.reason)
                return None

    # 获取页面中每一项具体的内容
    def getItems(self, pageIndex):
        pageCode = self.getPageHtml(pageIndex)
        if not pageCode:
            print("页面加载失败。。。")
            return None

        # 正则表达式匹配
        # .*? 是一个固定的搭配，.和*代表可以匹配任意无限多个字符，加上？表示使用非贪婪模式进行匹配
        # (.*?)代表一个分组,item[0]就代表第一个(.*?)所指代的内容,re.S 标志代表在匹配时为点任意匹配模式，
        # 发布人,段子内容，,是否图片，以及点赞的个数
        pattern = re.compile(
            '<div.*?author clearfix">.*?<a .*?<h2.*?>(.*?)</h2>.*?<div.*?content">.*?<span.*?>(.*?)</span>(.*?)' +
            '<div class="stats.*?class="number">(.*?)</i>', re.S)
        items = re.findall(pattern, pageCode)
        pageStories = []
        # 是否含有图片item[2]
        for item in items:
            haveImg = re.search("img", item[2])
            if not haveImg:
                #  去除字符br
                replaceBR = re.compile('<br/>')
                text = re.sub(replaceBR, "\n", item[1])
                # 删除字符串中开头、结尾处的空白符
                pageStories.append([item[0].strip(), text.strip(), item[2].strip(), item[3].strip()])

        return pageStories

    # 判断页数，从第一页开始
    def loadPage(self):
        if self.enable == True:
            if len(self.storiesList) < 2:
                pageStories = self.getItems(self.pageIndex)
                if pageStories:
                    self.storiesList.append(pageStories)
                    self.pageIndex += 1

    # 每次输出一个内容
    def getOneStory(self, pageStories, page):
        for story in pageStories:
            i = input()
            self.loadPage()
            if i == 'Q':
                self.enable = False
                return
            print(u"第%d页\n发布人:%s\n赞:%s\n%s" % (page, story[0], story[3], story[1]))

    def start(self):
        print(u"正在读取糗事百科，按回车键查看新段子，Q退出")
        self.enable = True
        self.loadPage()
        nowPage = 0
        while self.enable:
            if len(self.storiesList) > 0:
                pageStories = self.storiesList[0]
                nowPage += 1
                del self.storiesList[0]
                self.getOneStory(pageStories, nowPage)


if __name__ == "__main__":
    spider = BaiKe()
    spider.start()
