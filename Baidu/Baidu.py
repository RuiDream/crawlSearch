#-*-coding:utf-8 -*-
import requests
import bs4
import csv
import time
import codecs



'''
爬虫提取百度搜索结果
链接  标题  摘要
author:starDream
'''

# 外部运行
def run(key_word1,filename):
    key_word = key_word1
    page_num = 10
    global globalCount
    globalCount = 0
    headers = {'pragma': "no-cache",
                    'accept-encoding': "gzip, deflate, br",
                    'accept-language': "zh-CN,zh;q=0.8",
                    'upgrade-insecure-requests': "1",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
                    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    'cache-control': "no-cache",
                    'connection': "keep-alive",
                    'cookie':"BAIDUID=3C1596F737DB99AD5308E572C26B494E:FG=1; BIDUPSID=3C1596F737DB99AD5308E572C26B494E; PSTM=1530624508; BD_UPN=12314753; BDUSS=HVRNjBSRm1SVFcwTW9TT0NZQUE2Nkl5MWhOOWozTEJ0Y3JwRWkzVTRPUlNhZUZjRVFBQUFBJCQAAAAAAAAAAAEAAABGh5ASw87RvbfJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFLcuVxS3Llcd; ispeed_lsm=0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=1420_21112_29238_28518_29099_29368_28839_29221_26350; delPer=0; BD_CK_SAM=1; BD_HOME=1; pgv_pvi=9848146944; pgv_si=s9376059392; shifen[89313084785_23522]=1560560490; BCLID=8069099223813726195; BDSFRCVID=0r-OJeC62wRQn5ow3-69ugbP-HEGKp5TH6aIaCsiSLVmu2Vszz1sEG0Pjf8g0KAbtohNogKKLgOTHULF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tJ4f_D0XJIP3qR5gMJ5q-n3HKUrL5t_XbI6y3JjOHJOoDDvH0j3cy4LdjG5fQqoXJCOfo56y-45JHxtzyMonynO03-Aq5xcK0570bhRCa4KKS4Ou26Q5QfbQ0M6hqP-jW26aLn7SBJ7JOpvsbUnxyhLTQRPH-Rv92DQMVU52QqcqEIQHQT3mDUThDG0ftj-8Jn-sQJ5e24oqHP-kKPrV-4oH5MQy5toyHD7yWCvd3bvcOR5Jj65b0l_HjfnfJKuq5jTM3ftEWp5nOPtG3MA--fF_Lpb0QM7pa6IH-tOLMDj5sq0x0-6te-bQyPQa-PR3BDOMahv15h7xOM5sQlPK5JkgMx6MqpQJQeQ-5KQN3KJmhpFuD60bj6b-jaAsbtQb26r-3--8-bTVHRDk5-Qo-4_eqxby26PLam79aJ5nJDobVxjkjtnbDIrBBpoM5q8LWgTxa-taQpP-HqTpLnbE0UAZhq_HLJJEMJ6eKl0MLnctbb0xyUQD5-4JXxnMBMnr52OnaU513fAKftnOM46JehL3346-35543bRTohFLtDtbMC0wj5A3K4LOMq5-5b0X-K5L3JD8bnjoHRjvq4bohjnQKmc9BtQmJJrfbfj8JR7bhTCCeJoJ-lODy-oxBb8tQg-q3lTq0-OEVpRKhJ_K3Rth2GQe0x-jLIQhVn0MWhjDfb7dX4nJyUPTbPnnBpQr3H8HL4nv2JcJbM5m3x6qLTKkQN3TJMIEK5r2SCDKtCQP; COOKIE_SESSION=14_7_9_8_4_11_0_1_7_4_0_0_27930_0_69_0_1560588271_1560560545_1560588202%7C9%23199_42_1560560464%7C7; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=1; H_PS_645EC=e677Pr1BBrM3QgnBOD%2BgYMI0puGDe3KKDz22rle6UpRv%2Fnc%2BKXNxOBph12gfqxG8dXUQ"
               }
    results_dic = {}
    path = filename
    with codecs.open(path, 'w', encoding='utf-8-sig') as f:
        writeContent = csv.writer(f)
        writeContent.writerow(["link", "title", "abstract", "body"])
    for i in range(page_num):
        #获得一个页面的标题，摘要和链接
        temp1,num = _get_one_page_result1(i,headers,key_word)
        #获得每一个页面的body中的内容
        temp2 = _get_the_page_body(temp1,num,headers)
        #将一个页面中的标题，摘要，链接和body中的内容写进csv文件中
        globalCount = _write_to_csv(temp2,filename,globalCount)
        print("GlobalCount:",globalCount)
        if globalCount>=20:
            break
        if num ==0:
            break
        time.sleep(3)
    return results_dic

#将长网址转化为短网址，如果遇到异常，将网址置为None
def redirect(Oriurl,headers):
    try:
        res = requests.get(Oriurl, timeout=30,headers = headers)
        url1 = res.url
    except Exception as e:
        print("转换网址:", e)
        return "None"
    return url1

# 获取一页的有效链接
def _get_one_page_result1(page,headers,key_word):
    print('[INFO]:Getting Page %s...' % page)
    #负责存放一页中的链接，标题，摘要和body信息
    links_temp = ["None" for x in range(40)]
    url = "https://www.baidu.com/s"
    pn = page *10
    querystring = {"wd": key_word, "pn": pn}
    #请求百度网页
    response = requests.request("GET", url, headers=headers, params=querystring)
    #获取到HTML
    html_content = response.content
    #使用bs4进行解析
    soup = bs4.BeautifulSoup(html_content, 'lxml',from_encoding='utf-8-sig')
    #获取页面左边部分
    left_content = soup.find('div', attrs={'id': 'content_left'})
    num =0
    #定义一个全局的网页中每个搜索结果的列表
    for i in range(1,11):
        try:
            #寻找到去除广告的每个单独的搜索结果
            result_url_list = left_content.find('div',id = str(pn+i))
            #寻找到标题下所对应的URL地址
            tempUrl = redirect(result_url_list.find('h3').find('a').get('href'),headers)
            #寻找到h3标签中存放的文字，一般即为标题
            tempTitle = result_url_list.find('h3').find('a').get_text()
            #寻找到摘要信息
            tempAbstract = result_url_list.find('div').get_text().replace(" ","").replace("\n","").replace("\t","").strip()
            links_temp[(i-1)*4+0] = tempUrl
            links_temp[(i-1)*4+1] = tempTitle
            links_temp[(i-1)*4+2] = tempAbstract
            num = num + 1
        except IndexError:
            pass
        except Exception as e:
            print(e)
            #如果遇到问题，则将对应的网址置为None，便于后边解析的时候进行判断，否则会出现问题
            links_temp[(i - 1) * 4 + 0] = "None"
    return links_temp,num

#获取每个标题下的body信息
def _get_the_page_body(link,len_result,headers):
    for i in range(len_result):
        if link[i*4] !="None":
            try:
                html = requests.get(link[i*4], timeout=30,headers = headers).content
                soup = bs4.BeautifulSoup(html, 'lxml')
                paras_tmp = soup.select('p')
                paras = paras_tmp[3:]
                text = ""
                for t in paras:
                    if len(t) > 0:
                        text += t.get_text() + "\n\n"
                link[i * 4 + 3] = text
            except Exception as e:
                print(e)
                link[i * 4 + 3] = "None"
                continue
        else:
            link[i * 4 + 3] = "None"
        #print(link[i*4:i*4+4])
    return link
#将读取到的页面信息存到csv文件中
def _write_to_csv(content,file_name,globalCount):
    #以文件的名字进行命名
    path = file_name
    print('[INFO]:Start to save data...')
    with codecs.open(path,'a',encoding='utf-8-sig') as f:
        writeContent = csv.writer(f)
        for i in range(10):
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
    filename = key_word +'.csv'
    results = run(key_word,filename)
    print('All things Done...')
