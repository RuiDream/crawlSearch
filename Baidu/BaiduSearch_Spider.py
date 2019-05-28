#-*-coding:utf-8 -*-
import requests
import bs4
import csv

'''
爬虫提取百度搜索结果
链接  标题  摘要
author:starDream
'''

# 提取准确的结果
class Get_Precise_Results():
	# 初始化
	def __init__(self, key_word, page_num=10):
		self.key_word = key_word
		self.page_num = page_num
		self.headers = {
			'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
			}
	# 外部运行
	def run(self):
		results_dic = {}
		for i in range(self.page_num):
			#获得一个页面的标题，摘要和链接
			temp1 = self._get_one_page_result1(i)
			#获得每一个页面的body中的内容
			temp2 = self._get_the_page_body(temp1)
			#将一个页面中的标题，摘要，链接和body中的内容写进csv文件中
			self._write_to_csv(temp2,self.key_word)

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
		links_temp = ["None" for x in range(40)]
		self.url = "https://www.baidu.com/s"
		pn = page *10
		querystring = {"wd": key_word, "pn": pn}
		#请求百度网页
		response = requests.request("GET", self.url, headers=self.headers, params=querystring)
		#获取到HTML
		html_content = response.content
		#使用bs4进行解析
		soup = bs4.BeautifulSoup(html_content, 'lxml',from_encoding='utf-8')
		#获取页面左边部分
		left_content = soup.find('div', attrs={'id': 'content_left'})
		#定义一个全局的网页中每个搜索结果的列表
		global result_url_list
		for i in range(1,11):
			try:
				#寻找到去除广告的每个单独的搜索结果
				result_url_list = left_content.find('div',id = str(pn+i))
				#寻找到标题下所对应的URL地址
				tempUrl = self.redirect(result_url_list.find('h3').find('a').get('href'))
				#寻找到h3标签中存放的文字，一般即为标题
				tempTitle = result_url_list.find('h3').find('a').get_text()
				#寻找到摘要信息
				tempAbstract = result_url_list.find('div').get_text().replace(" ","").replace("\n","").replace("\t","").strip()
				links_temp[(i-1)*4+0] = tempUrl
				links_temp[(i-1)*4+1] = tempTitle
				links_temp[(i-1)*4+2] = tempAbstract
			except IndexError:
				pass
			except Exception as e:
				print(e)
				#如果遇到问题，则将对应的网址置为None，便于后边解析的时候进行判断，否则会出现问题
				links_temp[(i - 1) * 4 + 0] = "None"
				continue
		return links_temp


#获取每个标题下的body信息
	def _get_the_page_body(self,link):
		for i in range(10):
			self.url2 = link[i*4]
			if self.url2 != "None":
				#同上
				response = requests.request("GET", self.url2, headers=self.headers)
				html_content = response.content
				soup = bs4.BeautifulSoup(html_content, 'lxml', from_encoding='utf-8')
				# 获取页面body部分
				body_content = soup.find('body').get_text().replace(" ","").replace("\n","").replace("\t","").strip()
				link[i*4+3] = body_content
			else:
				link[i * 4 + 3] = self.url2
		return link
#将读取到的页面信息存到csv文件中
	def _write_to_csv(self,content,file_name):
		#以文件的名字进行命名
		path = file_name+".csv"
		print('[INFO]:Start to save data...')
		with open(path,'a+',encoding='utf-8',newline = "") as f:
			writeContent = csv.writer(f)
			for i in range(10):
				writeContent.writerow(content[i*4:i*4+3])
		f.close()

# 内部调试
if __name__ == '__main__':
	key_word = input('Enter the key word:')
	page_num = 2
	results = Get_Precise_Results(key_word, page_num).run()
	print('All things Done...')