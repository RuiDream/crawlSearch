#-*-coding:utf-8 -*-
#网页url采集爬虫，给定网址，以及存储文件，将该网页内全部网址采集下，可指定文件存储方式
import requests,time
import responses
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

    #百度搜索爬虫，给定关键词和页数以及存储到哪个文件中，返回结果去重复后的url集合
    url = "https://www.baidu.com/s"
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
            'cookie': "BAIDUID=2F09104D730320690B2C1A2CCD3CA766:FG=1;BDORZ=B490B5EBF6F3CD402E515D22BCDA1598;BDSVRTM=0;BDUSS=WY1QkVPZDZjRUNkaTRwYlZ6ZjNhRHNRWGV5eFgxMFNvd1kzcm1ZVUx4Q0pibDVjQVFBQUFBJCQAAAAAAAAAAAEAAAAIkQiGvPLM~W0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAInhNlyJ4TZcc;BD_CK_SAM=1;BD_UPN=12314353;BIDUPSID=2F09104D730320690B2C1A2CCD3CA766;H_PS_645EC=c8beTqRWdqge4LlwsQlK4cwTkjZmvvdEXTMhBKNNonodKSCNCjhHuG9PU2o;H_PS_PSSID=1433_21083_20697_28329_28132_26350_28266_27244;PSINO=3;PSTM=1543374859;delPer=0;sugstore=1;",

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
                    context = selector.xpath('//*[@id="'+str(pn+i)+'"]/h3/a[1]/@href')

                    content = selector.xpath('//*[@id="' + str(pn+i) + "\"]/h3/a[1]")
                    for contents in content:
                        a=contents.xpath('string(.)')
                    #result = selector.xpath('//*[@id="'+ str(pn+i) +'"]/div[@class="c-abstract"]/text()')
                    #print(result)
                    context = list(set(context))
                    print(len(context),context[0])
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

if __name__ == '__main__':

    wd = "天气 武汉"
    pn = 1
    save_file_name = "save_url.txt"
    return_set = baidu_search(wd,pn,save_file_name)