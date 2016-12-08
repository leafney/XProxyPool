# coding:utf-8
"""
sqliteHelper

"""

import sqlite3
import time
import logging

logger=logging.getLogger('spider.sqliteHelper')

class SqliteHelper(object):
	"""docstring for SqliteHelper"""
	def __init__(self):
		'''
		数据库连接
		'''
		self.database=sqlite3.connect('proxy.db')
		self.cursor=self.database.cursor()

	def db_compress(self):
		'''
		数据库压缩
		'''
		self.database.execute('VACUUM')

	def commit(self):
		'''
		提交
		'''
		self.database.commit()

	def db_createTable(self):
		'''
		初始化数据库
		'''
		sql_init='''
		DROP TABLE IF EXISTS "main"."proxyip";
		'''
		sql_create='''
		CREATE TABLE "proxyip" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
"xip"  TEXT(32),
"xport"  TEXT(8),
"xaddr"  TEXT(64),
"xlevel"  TEXT(32),
"xprotocal"  TEXT(8),
"xstatus"  INTEGER NOT NULL DEFAULT 0,
"xtime"  TEXT
);
		'''
		self.cursor.executescript(sql_init)
		self.cursor.executescript(sql_create)
		self.database.commit()

	def db_delete(self):
		'''
		删除
		'''
		sql_delete='''

		'''
		self.cursor.execure()
		self.commit()

	def db_update_for_status(self,pid,pstatus):
		'''
		更新状态
		'''
		sql_update='''
		UPDATE proxyip SET xstatus=? WHERE id=?
		'''
		self.cursor.execute(sql_update,(pstatus,pid))
		self.commit()

	def db_insert_for_proxyip(self,entrylist):
		'''
		插入数据集合
		'''
		sql_exist='''
		SELECT id FROM proxyip WHERE xip=?
		'''
		sql_insert='''
		INSERT INTO proxyip (xip,xport,xaddr,xlevel,xprotocal,xstatus,xtime) VALUES (?,?,?,?,?,0,?)
		'''
		count=0
		for entry in entrylist:
			self.cursor.execute(sql_exist,(entry['xip'],))
			res=self.cursor.fetchone()
			if res:
				print('this ip is haved : %s' %(entry['xip']))
			else:
				gettime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
				self.cursor.execute(sql_insert,(entry['xip'],entry['xport'],entry['xaddr'],entry['xlevel'],entry['xprotocal'],gettime))
				count+=1

		self.commit()
		return count

	def db_select_all_for_verify(self):
		'''
		查询数据库中所有数据用于验证代理ip是否可用
		'''
		sql_verify='''
		SELECT id,xip,xport,xprotocal FROM proxyip WHERE xstatus=0
		'''
		self.cursor.execute(sql_verify)
		res=self.cursor.fetchall()
		return res

	def db_select_proxy_ip_count(self):
		'''
		获取数据库中代理ip的总数
		'''
		sql_count='''
		SELECT count(1) FROM proxyip WHERE xstatus=0
		'''
		self.cursor.execute(sql_count)
		count=self.cursor.fetchone()
		return count

	def close(self):
		self.cursor.close()
		self.database.close()

	def db_delete_proxy_ip_for_useless(self,pstatus):
		"""
		删除数据库中指定状态的数据，并压缩sqlite文件大小
		"""

		sql_delete='''
		DELETE FROM proxyip	WHERE xstatus=?
		'''
		self.cursor.execute(sql_delete,(pstatus,))
		self.db_compress() # 压缩数据库大小
		self.commit() # 提交修改
		logging.info('删除数据库中指定状态的数据，并压缩sqlite文件大小')
		


