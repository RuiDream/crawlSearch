#-*-coding:utf-8 -*-
import requests
import bs4
import csv
import time
import codecs
import random



'''
爬虫提取搜索结果
链接  标题  摘要
author:starDream
'''

# 外部运行
def run(key_word1,filename):
    key_word = key_word1
    page_num = 10
    globalCount = 0
    headers = {
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
                   }
    path = filename
    with codecs.open(path, 'w', encoding='utf-8-sig') as f:
        writeContent = csv.writer(f)
        writeContent.writerow(["link", "title", "abstract", "body"])
    for i in range(1,page_num):
        #获得一个页面的标题，摘要和链接
        temp1,num = _get_one_page_result1(i,headers,key_word)
        #将一个页面中的标题，摘要，链接和body中的内容写进csv文件中
        globalCount = _write_to_csv(num,temp1,filename,globalCount)
        print("GlobalCount:",globalCount)
        if globalCount >=20:
            break
        if num == 0:
            break
        visitTime = random.randint(15,20)
        time.sleep(visitTime)
    return ""

def commentBody(url,headers):
    visitTime = random.randint(3, 8)
    time.sleep(visitTime)
    response = requests.request("GET", url, headers=headers)
    html_content = response.content
    soup = bs4.BeautifulSoup(html_content, 'lxml', from_encoding='utf-8-sig')
    left_content = soup.find('div', attrs={'class': 'contL'})
    problem = "问题:"+left_content.find('div', attrs={'class': 'articleCont'}).find('h1').get_text()
    description = "描述"+left_content.find('div', attrs={'class': 'cont mt10'}).get_text()
    try:
        commentResult = left_content.find('div', attrs={'class': 'list mt10'})
        commentList = commentResult.find_all('li')
    except Exception:
        comment = "无回复"
        reply_content = problem + description + comment
        return reply_content
    comment = "回复："
    for i in range(len(commentList)):
        comment = comment + str(i+1)+". " + commentList[i].find('div', attrs={'class': 'text'}).get_text()
    reply_content = problem+description+comment
    return reply_content

# 获取一页的有效链接
def _get_one_page_result1(page,headers,key_word):
    print('[INFO]:Getting Page %s...' % page)
    #负责存放一页中的链接，标题，摘要和body信息
    links_temp = ["None" for x in range(60)]
    url = "http://www.lamabang.com/search/type-2-k-"+key_word+".html?"
    pn = page
    querystring = { "page": pn}
    #请求网页
    response = requests.request("GET", url, headers=headers, params=querystring)
    #获取到HTML
    html_content = response.content
    #使用bs4进行解析
    soup = bs4.BeautifulSoup(html_content, 'lxml',from_encoding='utf-8-sig')
    #获取页面左边部分
    left_content = soup.find('div', attrs={'class': 'searchResults'})
    #定义一个全局的网页中每个搜索结果的列表、
    try:
        result_url_list = left_content.find('div', attrs={'class': 'topicList'}).find_all('dl')
    except Exception as e:
        print(e)
        print("无搜索结果！")
        return "Empty",0

    for i in range(len(result_url_list)):
            tempArticle = result_url_list[i].find('div',attrs={'class':'article'})
            tempUrl = tempArticle.find('div',attrs={'class':'title'}).find('a').get('href')
            tempTitle = tempArticle.find('div',attrs={'class':'title'}).get_text()
            tempAbstract =tempArticle.find('div',attrs={'class':'content'}).get_text()
            tempBody = commentBody(tempUrl,headers)
            links_temp[i * 4 + 0] = tempUrl
            links_temp[i * 4 + 1] = tempTitle
            links_temp[i * 4 + 2] = tempAbstract
            links_temp[i * 4 + 3] = tempBody

    return links_temp,len(result_url_list)

#将读取到的页面信息存到csv文件中
def _write_to_csv(num,content,file_name,globalCount):
    #以文件的名字进行命名
    path = file_name
    print('[INFO]:Start to save data...')
    with codecs.open(path,'a',encoding='utf-8-sig') as f:
        writeContent = csv.writer(f)
        for i in range(num):
            if content[i * 4] != "None":
                writeContent.writerow(content[i*4:i*4+4])
                globalCount +=1
            if globalCount >= 20:
                break
    f.close()
    return globalCount

# 内部调试
if __name__ == '__main__':
    key_word = input('Enter the key word:')
    filename = key_word+'.csv'
    results = run(key_word,filename)
    print('All things Done...')
