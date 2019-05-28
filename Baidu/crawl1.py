#-*-coding:utf-8 -*-
#网页url采集爬虫，给定网址，以及存储文件，将该网页内全部网址采集下，可指定文件存储方式
import requests,time
import responses
from lxml import etree
import os
import sqlite3
import requests
from win32crypt import CryptUnprotectData

def Redirect(url):
    try:
        res = requests.get(url,timeout=10)
        url = res.url
    except Exception as e:
        print("4",e)
        time.sleep(1)
    return url

def baidu_search(wd,pn_max,save_file_name):
    #百度搜索爬虫，给定关键词和页数以及存储到哪个文件中，返回结果去重复后的url集合
    url = "https://www.baidu.com/s"
    return_set = set()
    for page in range(pn_max):
        pn = page*10
        querystring = {"wd":wd,"pn":pn}
        #带上header的原因是
        #模拟浏览器，欺骗服务器，获取和浏览器一致的内容
        headers = {
            'pragma': "no-cache",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.8",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'cache-control': "no-cache",
            'connection': "keep-alive",
            'cookie': "BAIDUID=3C1596F737DB99AD5308E572C26B494E:FG=1; BIDUPSID=3C1596F737DB99AD5308E572C26B494E; PSTM=1530624508; BDUSS=HVRNjBSRm1SVFcwTW9TT0NZQUE2Nkl5MWhOOWozTEJ0Y3JwRWkzVTRPUlNhZUZjRVFBQUFBJCQAAAAAAAAAAAEAAABGh5ASw87RvbfJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFLcuVxS3Llcd; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID=fb-OJeC62wme2979TKySugbP-jUg5v7TH6aok6PAgEX5-VBwdiV_EG0PHf8g0KubFpPcogKKLgOTHULF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tJuOVC8htD-3fP36q45Hh4_Oqxby2C62aJ3BbMJvWJ5TMCoj5Pkh0fR-bb_OKJQMKH4L0lvgtCQGShPC-tPM2l4w5xPLhxDjM6COapb13l02V-jEe-t2ynLVX-cyhtRMW23r0h7mWU5dsxA45J7cM4IseboJLfT-0bc4KKJxthF0hC0lj5KajTOMKUnh-I6yaDJ0WJ5ea-3_KRrN55RxbnLgyxom2xkqQjvybqFXy4TVKt5T-l0VbfPUDMJ9LUvQaTc4BUJ_WxbrMfoj5hjkbfJBQttjQn3hfIkja-5t3fbmVR7TyU42bU47yaji0q4Hb6b9BJcjfU5MSlcNLTjpQT8rDPCEJj-DJR4eoKPQ24-_ePTl-4of5DCShUFsKtDLB2Q-5KL-bb6qhCI6eqOv2qt0bU5Te4TP5bTq_MbdJJjojIQMLtJpW5QD345fKPcpX2TxoUJd5DnJhhvG-xj20-tebPRiWPb9QgbP2pQ7tt5W8ncFbT7l5hKpbt-q0x-jLn7ZVJO-KKCahDKCjMK; delPer=0; H_PS_PSSID=1420_21112_19897_29064_28518_29099_28724_28963_28839_28584_26350; PSINO=2;",

        }
        #使用代理的原因：proxies = proxies
        #proxies = {
	#"http": "http://12.34.56.79:9527",
	#"https": "https://12.34.56.79:9527",
	#}

        #让服务器以为不是同一个客户端在请求
#       #防止我们的真实地址被泄露，防止被追究

        try:
            #post请求比get请求更加安全，且没有文本长度的限制，如果需要登录注册的时候需要发送post请求
            response = requests.request("GET", url, headers=headers, params=querystring)
            print("URL:",response.url)
            #解析html
            selector = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
            print(selector)
        except Exception as e:
            print ("页面加载失败", e)
            continue

        with open(save_file_name,"a", encoding='utf-8') as f:
            for i in range(1,11):
                try:
                    #根据属性href筛选标签
                    context = selector.xpath('//*[@id="'+str(pn+i)+'"]/h3/a[1]/@href')

                    content = selector.xpath('//*[@id="' + str(pn+i) + "\"]/h3/a[1]")
                    print(content)
                    print(content)
                    for contents in content:
                        a=contents.xpath('string(.)')
                    #result = selector.xpath('//*[@id="'+ str(pn+i) +'"]/div[@class="c-abstract"]/text()')
                    #print(result)
                    context = list(set(context))
                    #print(content)
                    #跳转到获取的url，若可跳转则返回url
                    f.write(a)
                    f.write("\n")
                    i=Redirect(context[0])
                    f.write(i)
                    return_set.add(i)
                    f.write("\n")
                except IndexError:
                    pass
                except Exception as e:
                    print(i,return_set)
                    print("3",e)
    return return_set

def getcookiefromchrome(host='.oschina.net'):
    cookiepath=os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
    sql="select host_key,name,encrypted_value from cookies where host_key='%s'" % host
    with sqlite3.connect(cookiepath) as conn:
        cu=conn.cursor()
        cookies={name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
        print(cookies)
        return cookies



if __name__ == '__main__':
    wd = "医生"
    pn = 1
    save_file_name = "save_url.txt"
    return_set = baidu_search(wd,pn,save_file_name)