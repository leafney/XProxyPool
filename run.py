# coding:utf-8
"""Python Ip Proxy Pool

用Python搭建高匿代理池
"""

import requests
import time
import json
import re

# 爬虫抓取操作类
from Xspider.spiderPro import Spider
from Xspider.spiderPro import Extractor
# 帮助类
import Xspider.spiderHelper as shelper
# 数据库操作类
from db.SQLiteHelper import SqliteHelper

# *********************************

# proxyman=Shelper.setLog('spider')



class ProxySpider(object):
	"""docstring for ProxySpider"""
	def __init__(self):
		self.SQLdb=SqliteHelper()
		self.proxyman=shelper.setLog('spider')

	# 获取代理ip for mimiip
	def get_proxy_ip_mimiip(self,urlFormat,tmpName,maxPageNo=1,urlType=1):
		"""[获取代理ip for mimiip]
		
		[注意：该方法为示例方法，用于演示抓取站点代理IP列表及验证到保存入库的完整过程]

		Arguments:
			urlFormat {[type]} -- [链接]
			tmpName {[type]} -- [模板目录]
		
		Keyword Arguments:
			maxPageNo {number} -- [最大页码] (default: {1})
			urlType {number} -- [1:静态页  2:动态页] (default: {1})
		"""
		
		extra=Extractor()
		extra.setXsltFromFile(tmpName)
		doSpider=Spider()
		p=SqliteHelper()

		if maxPageNo <= 1:
			maxPageNo=1
		maxPageNo+=1

		for page in range(1,maxPageNo):
			url=urlFormat.format(page)
			# url='http://www.mimiip.com/gngao/{0}'.format(page)

			html_dom=doSpider.getContent(url,urlType)
			op_xml=extra.extractHtmlDomtoXml(html_dom)
			op_json=doSpider.xmlToJson(op_xml)

			# proxyman.info(op_json)
			# print(op_json)
			# return False
			# break

			# 解析转换后的json
			obj=json.loads(op_json)
			proxy_list=[]
			if obj['proxyshow']:
				for ps in obj['proxyshow']['item']:
					proxy_dict={}

					proxy_dict['xip']=ps['xip']
					proxy_dict['xport']=ps['xport']
					proxy_dict['xaddr']=ps['xaddr'].replace('\n','')
					proxy_dict['xlevel']=ps['xlevel']
					proxy_dict['xprotocal']=ps['xprotocal'].lower()
					proxy_list.append(proxy_dict)

			proxy_list_ok=[]
			# 遍历，验证代理ip是否可用
			for pro in proxy_list:
				aa_show='the {0}-{1}:{2} for {3}'.format(pro['xprotocal'],pro['xip'],pro['xport'],pro['xaddr'].encode('utf-8'))
				print(aa_show)
				self.proxyman.info(aa_show)

				p_ip={"{0}".format(pro['xprotocal']):"http://{0}:{1}".format(pro['xip'],pro['xport'])}
				res=self.check_proxy_ip(p_ip)
				if res:
					proxy_list_ok.append(pro)

			# 将筛选处理后的代理IP添加到数据库中
			count = p.db_insert_for_proxyip(proxy_list_ok)
			print('insert %d ips success' %(count))

			# 获取完一页数据后，休息一下
			shelper.makeSleep(5)


	# 获取代理ip
	def get_proxy_ip(self,funcSite,urlFormat,tmpName,maxPageNo=1,urlType=1):
		"""[获取某站点下的代理ip]
		
		[通过指定抓取站点链接，指定xslt模板文件的方式来抓取指定代理站点下的可用的高匿代理IP]
		
		Arguments:
			funcSite {[type]} -- [针对于指定站点解析json数据的方法]
			urlFormat {[type]} -- [指定站点url,页码部分为“{0}”]
			tmpName {[type]} -- [指定站点的xslt模板]
		
		Keyword Arguments:
			maxPageNo {number} -- [最大页码] (default: {1})
			urlType {number} -- [站点html类型 1静态  2动态] (default: {1})
		"""
		extra=Extractor()
		extra.setXsltFromFile(tmpName)
		doSpider=Spider()

		if maxPageNo <= 1:
			maxPageNo=1
		maxPageNo+=1
		try:
			for page in range(1,maxPageNo):
				url=urlFormat.format(page)
				# 获取某页面html内容
				page_html_dom=doSpider.getContent(url,urlType)
				page_xml=extra.extractHtmlDomtoXml(page_html_dom)
				page_json_data=doSpider.xmlToJson(page_xml)

				# **************************************
				# Debug html
				# page_htmlStr=doSpider.htmlStr
				# self.proxyman.info(page_htmlStr)

				# Debug jsondata
				self.proxyman.info(page_json_data)
				# print(page_json_data)
				# **************************************

				# 针对于抓取的站点，对得到的内容进行解析处理后得到抓取的代理IP集合
				page_proxy_list=funcSite(page_json_data)

				# 对代理IP进行可用性验证筛选
				page_proxy_list_ok=self.availabile_proxy_ip(page_proxy_list)

				# 将验证通过的代理IP添加到数据库中
				self.save_proxy_ip(page_proxy_list_ok)

				# 获取完一页数据后，休息一下
				shelper.makeSleep(5)
		except Exception as e:
			err_show='[get_proxy_ip]--error-{0}'.format(str(e))
			print(err_show)
			self.proxyman.error(err_show)
		finally:
			fina_show='[get_proxy_ip]--The work is Done'
			print(fina_show)
			self.proxyman.error(fina_show)


	# 代理Ip可用性验证
	def availabile_proxy_ip(self,proxyList):
		"""[可用性验证]
		
		[遍历，验证代理ip是否可用]
		
		Arguments:
			proxyList {[list]} -- [待验证的代理ip集合]
		
		Returns:
			[list] -- [验证通过的代理ip集合]
		"""
		
		proxy_list_ok=[]
		try:
			for pro in proxyList:
				aa_show='the {0}-{1}:{2} for {3}'.format(pro['xprotocal'],pro['xip'],pro['xport'],pro['xaddr'].encode('utf-8'))
				print(aa_show)
				self.proxyman.info(aa_show)

				# {"http":"http://102.168.5.103:8080"}
				p_ip={"{0}".format(pro['xprotocal']):"http://{0}:{1}".format(pro['xip'],pro['xport'])}
				# 通过比对正常请求和通过代理请求的结果判断该代理ip是否可用
				res=self.check_proxy_ip(p_ip)
				if res:
					proxy_list_ok.append(pro)
		except Exception as e:
			err_show='[availabile_proxy_ip]--error-{0}'.format(str(e))
			print(err_show)
			self.proxyman.error(err_show)
		finally:
			return proxy_list_ok


	# 将验证后的代理ip添加到数据库中
	def save_proxy_ip(self,proxyList):
		"""[添加到数据库中]
		
		[将验证后的代理ip添加到数据库中]
		
		Arguments:
			proxyList {[list]} -- [验证后的代理Ip集合]
		"""
		count = self.SQLdb.db_insert_for_proxyip(proxyList)
		print('insert %d ips success' %(count))
		self.proxyman.info('insert %d ips success' %(count))


	# 验证指定代理ip是否可用
	def check_proxy_ip(self,proxyip):
		"""[验证代理ip是否可用]
		
		[proxyip 格式 {"http":"http://120.52.73.97:8081"}]
		
		Arguments:
			proxyip {[dict]} -- [待验证的代理ip字典]
		
		Returns:
			bool -- [是否通过]
		"""

		s = requests.Session()
		a = requests.adapters.HTTPAdapter(max_retries=3)
		b = requests.adapters.HTTPAdapter(max_retries=3)
		s.mount('http://', a)
		s.mount('https://', b)

		the_checked_ip=proxyip.values()[0]

		try:
			MaskedIP = s.get("http://icanhazip.com", timeout=10, proxies=proxyip).content.strip()

			# 用正则判断请求返回的内容是否是ip
			pattern=r"^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$"
			pattern_res=re.match(pattern,MaskedIP)
			if not pattern_res:
				res_show='return result is not ip'
				print(res_show)
				self.proxyman.error('Result Content is Not Ip')
				return False

			mask_ip=pattern_res.group(0)

			# 直接访问
			OrigionalIP = requests.get("http://icanhazip.com", timeout=30).content.strip()
		
			ip_show='origional_ip is [{0}] -- mask_ip is [{1}]'.format(OrigionalIP,mask_ip)
			print(ip_show)

			if OrigionalIP != mask_ip:
				print('Proxy IP ok')
				self.proxyman.info('the mask ip【{0}】and return ip【{1}】is {2}'.format(the_checked_ip,mask_ip,'【OK】'))
				return True
			else:
				print('Not Anonymous')
				self.proxyman.info('the mask ip【{0}】and return ip【{1}】is {2}'.format(the_checked_ip,mask_ip,'Not Anonymous'))
				return False
		except requests.exceptions.Timeout:
			print('the request timeout')
			self.proxyman.error('Timeout')
			return False
		except Exception as e:
			print('the request error')
			self.proxyman.error('Error')
			return False

	# 判断数据库中代理ip是否可用并进行标记处理
	def verify_proxy_ip(self):
		"""[判断代理ip是否过期]
		
		[验证数据库中的【全部的】代理ip是否过期，如果过期，更新status=1，标记为待删除状态]
		"""
		# 从数据库中获取全部代理IP列表
		result=self.SQLdb.db_select_all_for_verify()
		if result:
			for pro in result:
				pid=pro[0]
				aa_show='verify {0}-{1}:{2}'.format(pro[3],pro[1],pro[2])
				print(aa_show)
				self.proxyman.info(aa_show)

				p_ip={"{0}".format(pro[3]):"http://{0}:{1}".format(pro[1],pro[2])}
				res=self.check_proxy_ip(p_ip)
				if not res:
					# 该代理ip不可用了
					sign_show='proxy ip【{0}】can not used ,signed for delete it'.format(pro[1])
					print(sign_show)
					self.proxyman.info(sign_show)
					# 在数据库中标记为待删除状态
					self.SQLdb.db_update_for_status(pid,1)

				shelper.makeSleep(3,False)

		else:
			res_show='未从数据库中获取到待检测的代理ip'
			print(res_show)
			self.proxyman.info(res_show)


# ***********************

def proxy_mimiip(jsonStr):
	"""MimiIp -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr'].replace('\n','')
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=ps['xprotocal'].lower()
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_mimiip]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list


def proxy_kuaidaili(jsonStr):
	"""快代理 -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr'].replace(' ','')
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=(ps['xprotocal'].split(',')[0]).lower()  # HTTP, HTTPS 多种时只取第一种
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_kuaidaili]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list


def proxy_ip84(jsonStr):
	"""Ip84 -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr'].replace('\n','')
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=ps['xprotocal'].lower()
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_ip84]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list


def proxy_xicidaili(jsonStr):
	"""XiciDaili -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr'].replace('\n','')
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=ps['xprotocal'].lower()
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_mimiip]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list

	# kx代理
def proxy_kxdaili(jsonStr):
	"""kxDaili -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr']
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=(ps['xprotocal'].split(',')[0]).lower()  # HTTP, HTTPS 多种时只取第一种
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_kxdaili]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list


	# 小舒代理
def proxy_xsdaili(jsonStr):
	"""xsDaili -- 解析转换后的json
	
	Arguments:
		jsonStr {[type]} -- [description]
	
	Returns:
		[type] -- [description]
	"""
	obj=json.loads(jsonStr)
	proxy_list=[]
	try:
		if obj['proxyshow']:
			for ps in obj['proxyshow']['item']:
				proxy_dict={}

				proxy_dict['xip']=ps['xip']
				proxy_dict['xport']=ps['xport']
				proxy_dict['xaddr']=ps['xaddr'].replace('\t','').replace('\n','').replace(' ','') # 替换制表符、回车和空格
				proxy_dict['xlevel']=ps['xlevel']
				proxy_dict['xprotocal']=ps['xprotocal'].lower()
				proxy_list.append(proxy_dict)
	except Exception as e:
		err_show='[proxy_kxdaili]--error-{0}'.format(str(e))
		print(err_show)
	finally:
		return proxy_list


# ***********************

if __name__ == '__main__':
	
	"""
	数据库相关
	"""

	# 初始化数据库
	# p=SqliteHelper()
	# p.db_createTable()


	# 检测数据库中代理可用性
	# ps=ProxySpider()
	# ps.verify_proxy_ip()


	# *****************

	"""
	第一种方式
	"""

	# 获取代理--mimiip  maxPage=
	# url='http://www.mimiip.com/gngao/{0}'
	# tmpName=shelper.getFilePath('template','tmp_mimiip_min_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip_mimiip(url,tmpName,1)


	# *****************

	"""
	采用第二种方式
	"""

	# mimiip
	# url='http://www.mimiip.com/gngao/{0}'
	# tmpName=shelper.getFilePath('template','tmp_mimiip_min_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip(proxy_mimiip,url,tmpName,1)



	# 快代理--kuaidaili  maxPage=10
	# url='http://www.kuaidaili.com/proxylist/{0}/'
	# tmpName=shelper.getFilePath('template','tmp_kuaidaili_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip(proxy_kuaidaili,url,tmpName,1)


	# IP巴士  http://ip84.com
	# url='http://ip84.com/dlgn/{0}'
	# tmpName=shelper.getFilePath('template','tmp_ip84_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip(proxy_ip84,url,tmpName,1)


	# XiciDaili 国内高匿免费HTTP代理IP http://www.xicidaili.com/nn/2
	# url='http://www.xicidaili.com/nn/{0}'
	# tmpName=shelper.getFilePath('template','tmp_xicidaili_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip(proxy_xicidaili,url,tmpName,1)


	# kxDaili 开心代理 http://www.kxdaili.com/dailiip/1/10.html#ip
	# url='http://www.kxdaili.com/dailiip/1/{0}.html#ip'
	# tmpName=shelper.getFilePath('template','tmp_kxdaili_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip(proxy_kxdaili,url,tmpName,1)


	# xsDaili 小舒代理 http://www.xsdaili.com/index.php?s=/index/mfdl/p/2.html
	url='http://www.xsdaili.com/index.php?s=/index/mfdl/p/{0}.html'
	tmpName=shelper.getFilePath('template','tmp_xsdaili_static.xslt')
	ps=ProxySpider()
	ps.get_proxy_ip(proxy_xsdaili,url,tmpName,1)



	print('ok')