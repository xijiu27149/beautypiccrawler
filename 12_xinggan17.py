import sys
from threading import Thread
from urllib import request
from lxml import etree
import os
import time
from requests_html import HTMLSession
import ssl
import requests

urltemplate = "https://www.xinggan17.com/forum.php?gid=169"
#urltemplate="https://xchina.co/photos/kind-2/{}.html" 171页
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
ssl._create_default_https_context = ssl._create_unverified_context
httpproxy_handler = request.ProxyHandler(
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
)
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

pdictemplate = "H:\\folder\\xinggan17\\{}\\{}\\"
ppfolder ="H:\\folder\\xinggan17\\{}\\"
#pdictemplate="/Users/dujingwei/Movies/folder/xchina/{}/"
#pdictemplate="/Volumes/ExtremePro/folder/xchina/{}/"
openner = request.build_opener(httpproxy_handler)

RETRYTIME = 0


def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res0 = requests.get(furl, headers=headers)

        furl1 = furl.replace("thumb", "images")
        res1=requests.get(furl1,headers=headers)
        if(int(res0.headers['content-length']) > int(res1.headers['content-length'])):
            res=res0
        else:
            res=res1
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except:
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
        return furl+"下载失败"

def checkfolderexist(classname,title):
    checkfolder=ppfolder.format(classname)
    if(not os.path.exists(checkfolder)):
        os.makedirs(checkfolder)
        return title

    dirs = os.listdir(checkfolder)
    for dir in dirs:
        temp = dir.split('[')
        temp = dir.replace("[{}".format(temp[len(temp)-1]), "")
        if(temp == title):
            return dir
    return title

def getpagehtml(pageurl):
    global RETRYTIME
    try:
        resp=requests.get(pageurl,headers=headers)
        return resp.text
        #req = request.Request(pageurl, headers=headers)
        #resp = openner.open(req)
        #return resp.read()
    except:
        if(RETRYTIME == 3):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        print("{}请求超时，20秒后重试第{}次".format(pageurl, RETRYTIME))
        time.sleep(20)
        getpagehtml(pageurl)

def docrawler(cur_classindex,cur_pageindex,items):
    if(cur_classindex == currentclassindex and cur_pageindex < currentsubclasspage ):
       return 
    for item in items:        
        itemurl = "https://www.xinggan17.com/"+item.xpath('a/@href')[0]
        itemtitle = item.xpath(
            'a/text()')[0].replace("[", "【").replace("]", "】").replace("/", " ").replace("?", "").strip()
        itemtitle = checkfolderexist(classname, itemtitle)
        imgfolder = pdictemplate.format(classname, itemtitle)
        if(not os.path.exists(imgfolder)):
            os.makedirs(imgfolder)
        imgpagehtmltext = getpagehtml(itemurl)
        imgpagehtml = etree.HTML(imgpagehtmltext)
        imgs = imgpagehtml.xpath('//div[@class="my-gallery"]/figure/a/img')
        imgindex = 1
        filenamelength=3
        if(len(imgs)>999):
            filenamelength=4
        for img in imgs:
            imgurl = img.xpath('@src')[0]
            imgname = os.path.basename(imgurl)
            imgname = "{}{}".format(imgfolder, "{}{}".format(
                str(imgindex).rjust(filenamelength, '0'), os.path.splitext(imgurl)[-1]))
            if(not os.path.exists(imgname)):
                downloadpic(imgname, imgurl)
            print("class:【{}/{}】{},page:【{}/{}】，总【{}/{}】-{}下载完毕".format(classitemindex, len(classitems), classname, cur_pageindex, totalpage,
                                                                                          imgindex, len(imgs), imgname))
            imgindex += 1
        if(not os.path.dirname(imgfolder)[-2:] == "P]"):
            newpicfolder = "{}[{}P]".format(
                os.path.dirname(imgfolder), imgindex-1)
            os.rename(imgfolder, newpicfolder)
        print("class:【{}/{}】{},page:【{}/{}】{}下载完毕".format(classitemindex,
              len(classitems), classname, cur_pageindex, totalpage, itemtitle))

currentclassindex=30
currentsubclasspage=2
currentitemindex=16
GroupNum=2

classpagetext=getpagehtml(urltemplate)
if(classpagetext == "failed"):
    print("请求超时")
    sys.exit()
classpagehtml=etree.HTML(classpagetext)
classitems = classpagehtml.xpath('//table[@class="fl_tb"]/tr/a')
classitemindex=1
for classitem in classitems:
    if(classitemindex<currentclassindex):
        classitemindex+=1
        continue
    if(classitemindex==31):
        classitemindex+=1
        continue
    if(classitemindex==33):
        break
    classname = classitem.xpath(
        'div/div[2]/a/text()')[0] + classitem.xpath('div/div[2]/a/em/text()')[0]
    classurl = "https://www.xinggan17.com/"+classitem.xpath('@href')[0]
    classsubpagehtmltext=getpagehtml(classurl)
    if(classpagetext == "failed"):
        print("请求超时")
        sys.exit()
    classsubpagehtml=etree.HTML(classsubpagehtmltext)
    totalpage = classsubpagehtml.xpath(
        '//div[@class="pg"]/label/span/text()')
    if(len(totalpage)==0):
        totalpage=1
    else:
        totalpage=totalpage[0].replace("页","").replace("/","").strip()
    for i in range(1,int(totalpage)+1):
        if(classitemindex == currentclassindex and i < currentsubclasspage):
            continue
        subclasspageurl = classurl.replace(
            classurl.split("/")[-1], "{}.html".format(i))
        subclasspagehtmltext=getpagehtml(subclasspageurl)
        subclasspagehtml=etree.HTML(subclasspagehtmltext)
        items = subclasspagehtml.xpath('//h3[@class="xw0"]')
        #创建多线程
        t_list = []
        for t in range(0, len(items), GroupNum):
            th = Thread(target=docrawler, args=(classitemindex,
            i, items[t:t+GroupNum]))
            t_list.append(th)
            th.start()
        for t in t_list:
            t.join()
            
    classitemindex+=1
print("Done")
