import feedparser
from urllib import request
from bs4 import BeautifulSoup
from tomd import Tomd
import os

# 写文件
def writedoc(text, dirname,filename):

    with open(dirname + "/" + filename + ".md", 'w', encoding='utf-8') as f:
        #写文件
        f.write(text)
    print(filename + ".md 写入完成" + "\n")

# 创建目录
def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 / 符号
    path = path.rstrip("//")
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
     # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False

# 获得含有对应标题内容的（string = 'snapshot'）最新链接地址
def get_url(string):
    url = "https://minecraft.net/en-us/feeds/community-content/rss"
    # data = feedparser.parse(url)
    data = feedparser.parse(url)

    link_list = []
    for i in range(len(data.entries)):
        if string in data.entries[i]['title']:
            link_list.append(data.entries[i]['link'])
    return link_list[0]
        
# 获得目标地址的html文件,并利用Beautifulsoup解析       
def get_soup(url):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

    req = request.Request(url, headers=headers)

    with request.urlopen(req) as response:
        # 读取response里的内容，并转码
        html_doc = response.read().decode('utf-8') # 默认即为 utf-8
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup

# 寻找解析的html内与快照相关的内容，并将格式转换为markdown
def soup_snapshot_2md(soup):
    # 待写入字符串
    text = str()

    # 查找所有有关的节点
    tags = soup.find_all(class_="page-section page-section--first article-body")[0]
    body_tag = soup.find_all("div", class_="end-with-block")[0]
    author_tag =soup.find_all("div", class_="attribution pb-3")[0]

    # 快照图片
    img_tag = soup.find_all(class_="article-head__image-container")[0]
    img_url = f"![]({'https://www.minecraft.net'}{img_tag.img['src']})"
    text = img_url + "\n"

    # 标题、副标题
    # head = 'Minecraft Snapshot 20w21a'
    head = tags.h1.get_text(strip=True)
    lead = tags.p.get_text(strip=True)
    text += "# " + head + "\n"
    text += "## " + lead + "\n"

    # 获得快照版本
    if "snapshot" in head.lower():
        head_name = head[head.rfind(" ") + 1:]
        dirname = "./snapshots/" + head_name
        filename = head_name
        print(dirname)
    elif "pre-release" in head.lower():
        head_name = head[head.find(" ") + 1:]
        dirname = "./pre_release/" + head_name
        filename = head_name
        print(dirname)

    # 文章主体转换为markdown
    body_html = str()
    output = str()
    for child in body_tag.children:
        body_html += str(child)
    output = Tomd(body_html).markdown
    output = output.replace("<br/>","")
    output = output.replace("&lt;","<")
    output = output.replace("&gt;",">")
    output = output.replace("<li>","- ")
    output = output.replace("</li>\n","")
    text += output

    # 文章作者
    author = author_tag.dl.get_text()
    author_img_url = f"![]({'https://www.minecraft.net'}{author_tag.img['src']})"
    pubdate = author_tag.find(class_="pubDate").attrs['data-value'][:10]
    text += (author.rstrip("\n") + "\n" + pubdate + "\n" + author_img_url + "\n")
    text = text.replace("Written By", "**Written By**")
    text = text.replace("Published", "**Published**")

    # 创建目录
    mkdir(dirname)

    # 写入文件
    writedoc(text, dirname, filename)

soup_snapshot_2md(get_soup(get_url('snapshot')))
soup_snapshot_2md(get_soup(get_url('pre-release')))
