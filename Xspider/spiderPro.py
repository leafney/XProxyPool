#coding:utf-8
"""
SpiderPro
Python 使用xlst方式获取动态或静态网页内容并解析

需要安装的依赖库：

$ pip install requests

$ sudo apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev
$ sudo pip install lxml

$ sudo pip install selenium

$ sudo pip install xmltodict

Linux系统下需要安装 phantomjs
Windows系统下请下载 phantomjs.exe

"""

# 静态网页请求
import requests

# 动态网页请求
from selenium import webdriver
# import selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# 网页内容解析
from lxml import etree

# xml转json
import xmltodict

# 日志
import logging

# 工具类
import time
import os
import json
import random
import chardet

# 判断运行平台
import platform

# ****************************
"""
Spider
	getContent(self,url,urlType=1,options=None) 获取网页内容
		* @url 请求网址  
		* @urlType: 1:静态 2：动态
		* @options 自定义请求heanders参数
	getJsonCont(self,url,options=None)  获取api接口json数据
		* @url 请求网址
		* @options 自定义请求heanders参数
	setHtmlStrtoHtmlDom(self,htmlstr)   将html源代码转换成htmlDom
		* @htmlstr html字符串
	saveContent(self,filepath,content,encode=False)   将内容写入文件中
		* @filepath 文件保存路径
		* @content 文件内容
		* @encode 当内容为unicode时对内容进行编码
	xmlToJson(self,xmlStr)  将xml字符串转换为json字符串
		* @xmlSTr  xml字符串

Extractor
	setXsltFromFile(self,xsltFilePath)   从文件读取xslt规则
		* 
	setXsltFromStr(self,xsltStr)   		 从字符串获取xslt规则
		* 
	setXsltFromAPI(self,ApiKey)    		 通过API接口获取xslt规则
		* 
	getXslt(self) 						 返回当前xslt规则
	extractHtmlDomtoXml(self,htmlDom)    提取方法，入参是一个HTML DOM对象，返回是提取结果
		* 

"""
# *****************************


# 设置日志配置项 (保证主名称和主模块中的日志名称相同)
logger=logging.getLogger('spider.spiderpro')
# 常量参数
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36'
# Windows系统下phantomjs.exe所在的路径
PHANTOMJS_BASE_PATH="D:\\YYYY\\333\\jingdong\\phantomjs.exe"


class Spider:
	"""docstring for Spider"""
	def __init__(self):
		self.htmlStr=""
		self.jsonStr=""

	# 获取网页内容
	# @url 请求网址
	# @urlType: 1:静态 2：动态
	# @options 自定义请求heanders参数
	def getContent(self,url,urlType=1,options=None):
		if urlType==1:
			try:
				logger.info('start:-{getContent}-{static webpage}')

				headers={"User-Agent":USER_AGENT}
				# 添加用户自定义headers
				if options:
					headers.update(options)

				r=requests.get(url,headers=headers,timeout=3000)
				# 获取网页内容编码用来转换成unicode类型
				r.encoding =chardet.detect(r.content)['encoding']
				html = r.text
				# print(html)
				self.htmlStr=html
				output=etree.HTML(html)
				return output
			except Exception,e:
				logger.error('{getContent}-获取网页内容失败-%s' %str(e))
				return None
			finally:
				logger.info('end:-{getContent}')
		else:
			try:
				logger.info('start:-{getContent}-{dynamic webpage}')
				# 设置webbrowser请求参数
				dcap = dict(DesiredCapabilities.PHANTOMJS)
				dcap["phantomjs.page.settings.userAgent"] = (USER_AGENT)

				browser=None
				if platform.system()=="Windows":
					# Windows 系统下 (需指定phantomjs.exe的路径)
					browser = webdriver.PhantomJS(desired_capabilities=dcap,service_log_path=os.path.devnull,executable_path=PHANTOMJS_BASE_PATH)
				else:
					# Linux 系统下
					browser = webdriver.PhantomJS(desired_capabilities=dcap,service_log_path=os.path.devnull)
				browser.set_page_load_timeout(300)
				browser.get(url)
				time.sleep(3)
				# 执行js得到整个dom
				html = browser.execute_script("return document.documentElement.outerHTML")
				self.htmlStr=html
				output = etree.HTML(html)
				return output
			except Exception,e:
				logger.error('{getContent}-获取网页内容失败-%s' %str(e))
				return None
			finally:
				browser.quit() # 退出，防止占用大量内存
				logger.info('end:-{getContent}')

	# 获取api接口json数据
	# @url 请求网址
	# @options 自定义请求heanders参数
	def getJsonCont(self,url,options=None):
			try:
				logger.info('start:-{getJsonCont}-{json data}')

				headers={"User-Agent":USER_AGENT}
				# 添加用户自定义headers
				if options:
					headers.update(options)

				r=requests.get(url,headers=headers,timeout=3000)
				# 请求头信息
				req_header=r.request.headers
				print(req_header)
				html = r.text
				# print(html)
				self.jsonStr=html
				return html
			except Exception,e:
				logger.error('{getJsonCont}-获取json内容失败-%s' %str(e))
				return None
			finally:
				logger.info('end:-{getJsonCont}')

	# 将html源代码转换成htmlDom
	# @htmlstr html字符串
	def setHtmlStrtoHtmlDom(self,htmlstr):
			try:
				logger.info('start:-{setHtmlStrtoHtmlDom}')
				self.htmlStr=htmlstr
				output = etree.HTML(htmlstr)
				return output
			except Exception,e:
				logger.error('{setHtmlStrtoHtmlDom}-将html字符串转换成HtmlDom时出错-%s' %str(e))
				return None
			finally:
				logger.info('end:-{setHtmlStrtoHtmlDom}')

	# 


	# 将内容写入文件中
	# @filepath 文件保存路径
	# @content 文件内容
	# @encode 当内容为unicode时对内容进行编码
	def saveContent(self,filepath,content,encode=False):
		f=open(filepath,'w')
		if encode:
			content=content.encode('utf-8')
		f.write(content)
		f.close()

	# 将xml字符串转换为json字符串
	# @xmlSTr  xml字符串
	def xmlToJson(self,xmlStr):
		logger.info('start:-{xmlToJson}')
		try:
			convertedDict=xmltodict.parse(xmlStr)
			jsonStr=json.dumps(convertedDict)
			return jsonStr
		except Exception,e:
			logger.error('{xmlToJson}-xml转换失败-%s' %str(e))
			return None
		finally:
			logger.info('end:-{xmlToJson}')


# 说明: html内容提取器
# 功能: 使用xslt作为模板，快速提取HTML DOM中的内容。
class Extractor(object):
	"""docstring for GsExtractor"""
	def _init_(self):
		self.xslt=""

	# 从文件读取xslt规则
	def setXsltFromFile(self,xsltFilePath):
		f=open(xsltFilePath,'r')
		try:
			self.xslt=f.read()
		finally:
			f.close()

	# 从字符串获取xslt规则
	def setXsltFromStr(self,xsltStr):
		self.xslt=xsltStr

	# 通过API接口获取xslt规则 todo
	def setXsltFromAPI(self,ApiKey):
		apiurl = ""
		apireq=requests.get(apiurl)
		self.xslt=apireq.text

	# 返回当前xslt规则
	def getXslt(self):
		return self.xslt

	# 提取方法，入参是一个HTML DOM对象，返回是提取结果
	def extractHtmlDomtoXml(self,htmlDom):
		logger.info('start:-{extractHtmlDomtoXml}')
		xslt_root = etree.XML(self.xslt)
		transform = etree.XSLT(xslt_root)
		try:
			result_xml=transform(htmlDom)
			# 得到的xml类型是 lxml.etree._XSLTResultTree 使用时需要转换为str
			# print(result_xml)
			return str(result_xml)
		except Exception,e:
			logger.error('{extractHtmlDomtoXml}-通过XSLT获取xml元数据失败-%s' %str(e))
			# print(e)
			return None
		finally:
			logger.info('end:-{extractHtmlDomtoXml}')



if __name__ == '__main__':
	pass
	# # 指定模板文件和网页类型
	# tmp='tmp_meinvcont.xslt'
	# urlType=1

	# # 初始化
	# extra=Extractor()
	# extra.setXsltFromFile(tmp)
	# doSpider=Spider()

	# # 抓取
	# # 根据文章网址获取内容中的图片
	# cont=doSpider.getContent(meinv_link,urlType)
	# op_xml=extra.extractHtmlDomtoXml(cont)
	# op_json = doSpider.xmlToJson(op_xml)