#-*-coding:utf-8 -*-
#网页url采集爬虫，给定网址，以及存储文件，将该网页内全部网址采集下，可指定文件存储方式
import urllib
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests,time
from lxml import etree

def Redirect(url):
    try:
        res = requests.get(url,timeout=10)
        url = res.url
    except Exception as e:
        print("4",e)
        time.sleep(1)
    return url

def baidu_search(wd,pn_max,save_file_name):
    wd = urllib.parse.quote(wd)
    #百度搜索爬虫，给定关键词和页数以及存储到哪个文件中，返回结果去重复后的url集合
    url = "https://www.baidu.com/sf/vsearch?pd=video&tn=vsearch&ie=utf-8&rsv_spt=7&rsv_bp=1&f=8&wd="+wd
    return_set = set()
    for page in range(pn_max):
        pn = page*10
        querystring = {"wd":wd,"pn":pn}
        headers = {
            'pragma': "no-cache",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.8",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'cache-control': "no-cache",
            'connection': "keep-alive",
            }
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            print("!!!!!!!!!!!!",response.url)
            #解析html
            selector = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
        except Exception as e:
            print ("页面加载失败", e)
            continue

        with open(save_file_name,"a", encoding='utf-8') as f:
            for i in range(1,11):
                try:
                    #根据属性href筛选标签
                    context = selector.xpath('//div[@class="video_small_intro"]/a/@href')
                    #context = list(set(context))
                    #for each in context:
                    print(len(context),context[i-1])

                    content = selector.xpath('//div[@class="video_small_intro"]/a//text()')
                    #content = list(set(content))
                    #contents=content[i-1]
                    # for contents in content[i-1]:
                    #a = content.xpath('string(.)')
                    print(content[i-1])
                   # for contents in content:
                     #   a = contents.xpath('string(.)')
                    #f.write(a)
                    #f.write("\n")
                    f.write(content[i-1])
                    f.write("\n")
                    i = Redirect(context[i-1])
                    f.write(i)
                    return_set.add(i)
                    f.write("\n")
                    f.write("\n")
                    #跳转到获取的url，若可跳转则返回url
                except IndexError:
                    pass
                except Exception as e:
                    print(i,return_set)
                    print("3",e)
    return return_set

if __name__ == '__main__':

    wd = "小猪佩奇"
    pn = 1
    save_file_name = "save_url1.txt"
    return_set = baidu_search(wd,pn,save_file_name)