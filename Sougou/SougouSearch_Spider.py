#-*-coding:utf-8 -*-
import requests
import bs4
import csv
import re

'''
爬虫提取搜狗搜索结果
链接  标题  摘要
author:starDream
'''

# 提取准确的结果
class Get_Precise_Results():
	# 初始化
	def __init__(self, key_word, page_num=10):
		self.key_word = key_word
		self.page_num = page_num
		self.count = 0
		self.globalCount = 0
		self.headers = {'pragma': "no-cache",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.8",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'cache-control': "no-cache",
            'connection': "keep-alive",
            'cookie': "SUV=005B271C1B10D4475B781522D1378441; CXID=458AFFA5417868A0DC18D13411894EF6; SUID=6EA3AE3B3865860A5B7A1A2600012810; wuid=AAERQ9x8IgAAAAqGCmIdCQYAIAY=; IPLOC=CN4201; pgv_pvi=4223668224; usid=8E4A14DE5037990A000000005C121099; SNUID=1E336CA9787DFE8966BD2AF17893EDBE; ad=VK4xxkllll2tLRO9lllllV8H4$9lllllTPSaBkllllwlllll4llll5@@@@@@@@@@; pgv_si=s7030352896; sct=18; ld=Ukllllllll2tESTDlllllV8HEUGlllllTPSaBkllllDlllll4ylll5@@@@@@@@@@"}
	# 外部运行
	def run(self):
		results_dic = {}
		path = self.key_word + ".csv"
		with open(path, 'a+', encoding='utf-8-sig', newline="") as f:
			writeContent = csv.writer(f)
			writeContent.writerow(["link","title","abstract","body"])
		for i in range(self.page_num):
			#获得一个页面的标题，摘要和链接
			temp1,len_result = self._get_one_page_result1(i)
			#获得每一个页面的body中的内容
			temp2 = self._get_the_page_body(temp1,len_result)
			#将一个页面中的标题，摘要，链接和body中的内容写进csv文件中
			tmp= self._write_to_csv(temp2,self.key_word,len_result)
			self.count +=tmp
			if self.count >=20:
				break
		return results_dic

	#将长网址转化为短网址，如果遇到异常，将网址置为None
	def redirect(self, Oriurl):
		try:
			res = requests.get(Oriurl, timeout=30,headers = self.headers)
			url1 = res.url
		except Exception as e:
			print("转换网址:", e)
			return "None"
		return url1

	# 获取一页的有效链接
	def _get_one_page_result1(self, page):
		print('[INFO]:Getting Page %s...' % page)
		#负责存放一页中的链接，标题，摘要和body信息
		links_temp = ["None" for x in range(100)]
		self.url = "https://www.sogou.com/web?"
		pn = page+1
		querystring = {"query": key_word, "page": pn}
		#请求百度网页
		response = requests.request("GET", self.url, headers=self.headers, params=querystring)
		#获取到HTML
		html_content = response.content
		#使用bs4进行解析
		soup = bs4.BeautifulSoup(html_content, 'lxml',from_encoding='utf-8')
		#获取页面左边部分
		left_content = soup.find('div', attrs={'class': 'main'})
		left_content = left_content.find('div',attrs = {'class':'results'})
		# 寻找到去除广告的每个单独的搜索结果
		result_url_list = left_content.find_all('div', attrs={'class': 'vrwrap'})
		lenResult_url = len(result_url_list)
		for i in range(lenResult_url):
			try:
				tempUrl = result_url_list[i].find('h3').find('a').get('href')
				if tempUrl.startswith('http') ==False:
					#寻找到标题下所对应的URL地址
					tempUrl = "https://www.sogou.com"+tempUrl
					tempUrl = self.getUrl(tempUrl)
				#tempUrl = self.redirect(tempUrl)

				#寻找到h3标签中存放的文字，一般即为标题
				tempTitle = result_url_list[i].find('h3').find('a').get_text().strip()
				#寻找到摘要信息
				tempAbstract = result_url_list[i].find('div').get_text().replace(" ","").replace("\n","").replace("\t","").strip()
				links_temp[i*4+0] = tempUrl
				links_temp[i*4+1] = tempTitle
				links_temp[i*4+2] = tempAbstract
			except IndexError:
				print("IndexError")
				links_temp[i * 4 + 0] = "None"
				continue
			except Exception as e:
				print(e)
				#如果遇到问题，则将对应的网址置为None，便于后边解析的时候进行判断，否则会出现问题
				links_temp[i * 4 + 0] = "None"
				continue
		return links_temp,lenResult_url

#获取每个标题下的body信息
	def _get_the_page_body(self,link,len_result):
		for i in range(len_result):
			if link[i*4] !="None":
				try:
					html = requests.get(link[i*4], timeout=30).text
					soup = bs4.BeautifulSoup(html, 'html.parser')
					# title = soup.select('div.mbtitle')
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
	def _write_to_csv(self,content,file_name,len_result):
		#以文件的名字进行命名
		path = file_name+".csv"
		print('[INFO]:Start to save data...')
		temp = 0
		with open(path,'a+',encoding='utf-8-sig',newline = "") as f:
			writeContent = csv.writer(f)
			for i in range(len_result):
				if content[i*4]!="None":
					writeContent.writerow(content[i*4:i*4+4])
					temp +=1
					self.globalCount +=1
				if self.globalCount == 21:
						break
		f.close()
		return temp

	def getUrl(self,url):
		s = requests.session()
		tmpPage = s.get(url)
		detailurl = ""
		try:
			# 得到真实页 真实网站地址
			detailurl = re.search(r'URL=\'(.*?)\'', tmpPage.content.decode('utf-8'), re.S)
			# httpurl = re.match(r"http://.*?/",detailurl.group(1)).group(0)  # 链接主页网址
		except Exception as e:
			print(e)
			return "None"
		return detailurl.group(1)

# 内部调试
if __name__ == '__main__':
	key_word = input('Enter the key word:')
	page_num = 10
	results = Get_Precise_Results(key_word, page_num).run()
	print('All things Done...')
