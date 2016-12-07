# coding:utf-8

import requests
import time
import json
import re
import os

# 爬虫抓取操作类
from Xspider.spiderPro import Spider
from Xspider.spiderPro import Extractor
# 帮助类
import Xspider.spiderHelper as Shelper
# 数据库操作类
from db.SQLiteHelper import SqliteHelper


proxyman=Shelper.setLog('spider')



class ProxySpider(object):
	"""docstring for ProxySpider"""
	def __init__(self):
		pass
	
	# 获取代理ip for mimiip
	def get_proxy_ip_mimiip(self,urlFormat,tmpName,maxPageNo=1,urlType=1):
		"""[获取代理ip for mimiip]
		
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
				proxyman.info(aa_show)

				p_ip={"{0}".format(pro['xprotocal']):"http://{0}:{1}".format(pro['xip'],pro['xport'])}
				res=self.check_proxy_ip(p_ip)
				if res:
					proxy_list_ok.append(pro)

			# 将筛选处理后的代理IP添加到数据库中
			count = p.db_insert_for_proxyip(proxy_list_ok)
			print('insert %d ips success' %(count))

			# 获取完一页数据后，休息一下
			Shelper.makeSleep(5)




	# 验证代理ip是否可用
	def check_proxy_ip(self,proxyip):
		'''
		验证代理ip是否可用
		proxyip 格式 {"http":"http://120.52.73.97:8081"}
		'''
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
				proxyman.error('Result Content is Not Ip')
				return False

			mask_ip=pattern_res.group(0)

			# 直接访问
			OrigionalIP = requests.get("http://icanhazip.com", timeout=30).content.strip()
		
			ip_show='origional_ip is [{0}] -- mask_ip is [{1}]'.format(OrigionalIP,mask_ip)
			print(ip_show)
			# proxyman.info('the mask_ip:[{0}] is '.format(mask_ip))

			if OrigionalIP != mask_ip:
				print('Proxy IP ok')
				proxyman.info('the mask ip【{0}】and return ip【{1}】is {2}'.format(the_checked_ip,mask_ip,'【OK】'))
				return True
			else:
				print('Not Anonymous')
				proxyman.info('the mask ip【{0}】and return ip【{1}】is {2}'.format(the_checked_ip,mask_ip,'Not Anonymous'))
				return False
		except requests.exceptions.Timeout:
			print('the request timeout')
			proxyman.error('Timeout')
			return False
		except Exception as e:
			print('the request error')
			proxyman.error('Error')
			return False

	# 判断代理ip是否过期
	def verify_proxy_ip(self):
		'''
		验证数据库中的【全部的】代理ip是否过期，如果过期，更新status=1，标记为待删除状态
		'''
		p=SqliteHelper()
		result=p.db_select_all_for_verify()
		if result:
			for pro in result:
				pid=pro[0]
				aa_show='verify {0}-{1}:{2}'.format(pro[3],pro[1],pro[2])
				print(aa_show)
				proxyman.info(aa_show)

				p_ip={"{0}".format(pro[3]):"http://{0}:{1}".format(pro[1],pro[2])}
				res=self.check_proxy_ip(p_ip)
				if not res:
					# 该代理ip不可用了
					sign_show='proxy ip【{0}】can not used ,signed for delete it'.format(pro[1])
					print(sign_show)
					proxyman.info(sign_show)
					# 标记为待删除状态
					p.db_update_for_status(pid,1)

				Shelper.makeSleep(3,False)

		else:
			res_show='未从数据库中获取到待检测的代理ip'
			print(res_show)
			proxyman.info(res_show)






if __name__ == '__main__':
	
	# 初始化数据库
	# p=SqliteHelper()
	# p.db_createTable()


	# 获取代理--mimiip  maxPage=
	# url='http://www.mimiip.com/gngao/{0}'
	# tmpName=Shelper.getFilePath('template','tmp_mimiip_min_static.xslt')
	# ps=ProxySpider()
	# ps.get_proxy_ip_mimiip(url,tmpName,1)


	# 检测数据库中代理可用性
	# ps=ProxySpider()
	# ps.verify_proxy_ip()




	print('ok')