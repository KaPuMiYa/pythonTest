# 1.对百度贴吧的任意帖子进行抓取
# 2.指定是否只抓取楼主发帖内容  http://tieba.baidu.com/p/3138733512?see_lz=1&pn=1
# 3.将抓取到的内容分析并保存到文件
import re
from urllib import request
from urllib.error import URLError


# 处理页面标签类


class Tool:
    # 去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    # 删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    # 把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格制表<td>替换为\t
    replaceTD = re.compile('<td>')
    # 把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    # 将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签剔除
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n  ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)

        return x.strip()


class BDTB:
    # 初始化，传入URL，以及
    def __init__(self, baseUrl, SeeLZ, floorTag):
        # base链接地址
        self.baseUrl = baseUrl
        # 是否只看楼主
        self.SeeLZ = '?see_lz=' + str(SeeLZ)
        # HTML标签剔除工具类对象
        self.tool = Tool()
        # 全局file变量，文件写入操作对象
        self.file = None
        # 楼层标号，初始为1
        self.floor = 1
        # 默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = u"百度贴吧"
        # 是否写入楼分隔符的标记
        self.floorTag = floorTag

    # 传入页码，获取该页帖子的代码
    def getPage(self, pageNum):
        try:
            url = self.baseUrl + self.SeeLZ + '&pn=' + str(pageNum)
            req = request.Request(url)
            response = request.urlopen(req)
            return response.read().decode('utf-8')
        except URLError as e:
            if hasattr(e, "reason"):
                print(u"连接百度贴吧失败，原因：", e.reason)
                return None

    # 获取帖子标题
    def getTitle(self, page):
        # 得到标题的正则表达式
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
        result = re.search(pattern, page)
        if result:
            # print(result.group(1))  # 测试输出
            return result.group(1).strip()
        else:
            return None

    # 提取帖子一共有多少页
    def getPageNum(self, page):
        # 获取帖子页数的正则表达式
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            # print(result.group(1))  # 测试输出
            return result.group(1).strip()
        else:
            return None

    # 获取每一层楼的内容
    def getContent(self, page):
        # 匹配所有楼层的内容
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            content = "\n" + self.tool.replace(item) + "\n"
            contents.append(content.encode('utf-8'))
        return contents

    def setFileTitle(self, title):
        # 如果标题不是为None，即成功获取到标题
        if title is not None:
            self.file = open(title + ".txt", "w+")
        else:
            self.file = open(self.defaultTitle + ".txt", "w+")

    def writeData(self, contents):
        for item in contents:
            if self.floorTag == "1":
                # 楼之间的分隔符
                floorLine = "\n【" + str(
                    self.floor) + u"】楼------------------------------------------------------------------------------------\n"
                self.file.write(floorLine)
                # 用python3 读取 默认返回的是bytes 而不是 str,需要解码为str
            self.file.write(item.decode('utf-8'))
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum == None:
            print("URL已失效，请重试")
            return

        try:
            print("该帖子共有 " + str(pageNum) + " 页")
            for i in range(1, int(pageNum) + 1):
                print("正在写入第 " + str(i) + " 页数据")
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        except IOError as e:
            print("写入异常，原因", e)
        finally:
            print("写入任务完成")


print(u"请输入帖子代号")
baseUrl = 'http://tieba.baidu.com/p/' + str(input(u'http://tieba.baidu.com/p/'))
seeLZ = input("是否只获取楼主发言，是输入1，否输入0\n")
floorTag = input("是否写入楼层信息，是输入1，否输入0\n")
bdtb = BDTB(baseUrl, seeLZ, floorTag)
bdtb.start()