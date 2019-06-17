#-*-coding:utf-8 -*-
import requests
import bs4
import csv
import time
import codecs



'''
爬虫提取搜索结果
链接  标题  摘要
author:starDream
'''

# 外部运行
def run(key_word1,filename):
    key_word = key_word1
    page_num = 10
    headers = {'pragma': "no-cache",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "zh-CN,zh;q=0.8",
                    'upgrade-insecure-requests': "1",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
                    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    'cache-control': "no-cache",
                    'connection': "keep-alive"}
    path = filename
    with codecs.open(path, 'w', encoding='utf-8-sig') as f:
        writeContent = csv.writer(f)
        writeContent.writerow(["link", "title", "abstract", "body"])
    type_c = ["ask","know","user_journal","community"]
    for j in range(4):
        with codecs.open(path, 'a+', encoding='utf-8-sig') as f:
            writeContent = csv.writer(f)
            writeContent.writerow(type_c[j])
        globalCount = 0
        for i in range(1,page_num):
            #获得一个页面的标题，摘要和链接
            temp1,num = _get_one_page_result1(type_c[j],i,headers,key_word)
            #将一个页面中的标题，摘要，链接和body中的内容写进csv文件中
            globalCount = _write_to_csv(num,temp1,filename,globalCount)
            if globalCount>=20:
                break
            if num == 0:
                break
            time.sleep(3)

#获取链接内的问答信息
def ask_body(url,headers):
    response = requests.request("GET",url,headers = headers)
    html_content = response.content
    soup = bs4.BeautifulSoup(html_content,'lxml',from_encoding='utf-8-sig')
    left_content = soup.find('div',attrs = {'class':'section-main'})
    problem_content = left_content.find('div',attrs = {'id':'qa-article'})
    title_content = "问题："+problem_content.find('div',attrs = {'class':'qa-title'}).get_text()
    try:
        description_content = "描述： " + problem_content.find('blockquote').get_text()
    except Exception as e:
        description_content = "描述：无 "
    try:
        best_content = "最佳回答：" + left_content.find('div', attrs={'id': 'qa-answer-best'}).get_text()
    except Exception as e:
        best_content = "最佳回答：无 "
    reply_content = title_content + description_content + best_content
    reply_list = left_content.find_all('li',attrs={'class':'answer-item'})
    if len(reply_list) == 0:
        return reply_content
    for i in range(len(reply_list)):
         reply_content = reply_content + str(i+1)+ ". " + reply_list[i].find('div',attrs = {'class':'answer-text'}).get_text()+"\n"
    return reply_content

def know_body(url, headers):
    response = requests.request("GET",url,headers = headers)
    html_content = response.content
    soup = bs4.BeautifulSoup(html_content,'lxml',from_encoding='utf-8-sig')
    main_frame = soup.find('div',attrs = {'id':'DivAll'})
    left_content = main_frame.find('div',attrs={'class':'detail-main wisdom-body-wrapper-ask-single'})
    title = "标题："+ left_content.find('h1').get_text()
    source = "信息："+ left_content.find('h6').get_text()
    content = "正文" + left_content.find('div',attrs = {'class':'article'}).get_text()
    know_body = title + source + content
    return know_body

def journal_body(url,headers):
    response = requests.request("GET", url, headers=headers)
    html_content = response.content
    soup = bs4.BeautifulSoup(html_content, 'lxml', from_encoding='utf-8-sig')
    try:
        main_frame = soup.find('div', attrs={'class': 'mytree-journal-article'})
        head = main_frame.find('div', attrs={'class': 'journal-head'})
        title = "标题：" + head.find('div', attrs={'class': 'journal-title'}).find('h1').get_text()
        source = "时间：" + head.find('span', attrs={'class': 'journal-date'}).get_text()
        content = "正文：" + main_frame.find('div', attrs={'class': 'journal-body'}).get_text()
        journal_body = title + source + content
    except Exception as e:
        return "内容只能在作者小家查看！"
    return journal_body

def community_body(url,headers):
    response = requests.request("GET", url, headers=headers)
    html_content = response.content
    soup = bs4.BeautifulSoup(html_content, 'lxml', from_encoding='utf-8-sig')
    main_frame = soup.find('div', attrs={'class': 'clubTopicList'})
    community_list = main_frame.find_all('div', attrs={'class': 'clubTopicSinglePost'})
    post_content = ""
    for i in range(len(community_list)):
        post_frame = community_list[i].find('div', attrs={'class': 'postBody'}).find('div', attrs={'class': 'postContent'})
        if i==0:
            post_content = "问题："+ post_frame.find('p',attrs={'id': 'topic_content'}).get_text()+"回答："
        else:
            post_content = post_content + str(i) + post_frame.get_text()
    return post_content


# 获取一页的有效链接
def _get_one_page_result1(type_c,page,headers,key_word):
    #负责存放一页中的链接，标题，摘要和body信息
    links_temp = ["None" for x in range(60)]
    url = "http://www.babytree.com/s.php?"
    pn = page
    querystring = {"q": key_word,"c":type_c,"pg": pn}
    #请求宝宝树的网页
    response = requests.request("GET", url, headers=headers, params=querystring)
    #获取到HTML
    html_content = response.content
    #使用bs4进行解析
    soup = bs4.BeautifulSoup(html_content, 'lxml',from_encoding='utf-8-sig')
    #获取页面左边部分
    left_content = soup.find('div', attrs={'class': 'search_item_area'})
    #定义一个全局的网页中每个搜索结果的列表
    try:
        result_url_list = left_content.find_all('div',attrs = {'class':'search_item'})
    except Exception as e:
        print(e)
        print("无搜索结果！")
        return "Empty",0
    for i in range(len(result_url_list)):
            tempUrl = result_url_list[i].find('div',attrs = {'class':'search_item_tit'}).find('a').get('href')
            #寻找到h3标签中存放的文字，一般即为标题
            tempTitle = result_url_list[i].find('div',attrs = {'class':'search_item_tit'}).find('a').get_text()
            #寻找到摘要信息
            tempAbstract = result_url_list[i].find('div',attrs = {'class':'search_item_cont'}).find('p').get_text()
            #爬取链接内的回答信息
            tempReply = ""
            if type_c == "ask":
                tempReply = ask_body(tempUrl,headers)
            elif type_c == "know":
                tempUrl = "http://www.babytree.com"+tempUrl
                tempReply = know_body(tempUrl, headers)
            elif type_c == "user_journal":
                tempReply = journal_body(tempUrl,headers)
            elif type_c == "community":
                tempReply = community_body(tempUrl, headers)
            links_temp[i*4+0] = tempUrl
            links_temp[i*4+1] = tempTitle
            links_temp[i*4+2] = tempAbstract
            links_temp[i*4+3] = tempReply
    return links_temp,len(result_url_list)


#将读取到的页面信息存到csv文件中
def _write_to_csv(num,content,file_name,globalCount):
    #以文件的名字进行命名
    path = file_name
    print('[INFO]:Start to save data...')
    with codecs.open(path,'a+',encoding='utf-8-sig') as f:
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