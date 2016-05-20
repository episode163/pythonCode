#使用beautifulSoup4解析页面内容
#页面部分内容  如下：
#2/2 LOW (0% - 20%)
#1	SH_ENB_I8	TDDST_IOT_LTE_SH	0%	0.00%	0.00%	*	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	*
#2	SH_CKY_ENB_I5	TDDST_IOT_LTE_SH	8.33%	25.00%	0.00%	*	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	0.00%	100.00%	0.00%	100.00%	0.00%	0.00%
from __future__ import division
from datetime import date,timedelta, datetime, tzinfo
import re
import urllib2
from base64 import encodestring
from bs4 import BeautifulSoup
import smtplib
import email

class createReport(object):
	def __init__(self, reportDate, username, password):
		self.username = username
		self.password = password
		self.usageResult = []
		lastdate = reportDate - timedelta(days = 1)
		self.date = reportDate 
		self.startTime = datetime.strftime(self.date.replace(second = 0).replace(minute = 0).replace(hour = 0).replace(month = lastdate.month).replace(day = lastdate.day),"%Y-%m-%d%%20%H:%M:%S")
		self.endTime = datetime.strftime(self.date.replace(second = 59).replace(minute = 59).replace(hour = 23).replace(month = lastdate.month).replace(day = lastdate.day),"%Y-%m-%d%%20%H:%M:%S")
		self.reportDate = datetime.strftime(lastdate,"%Y-%m-%d")
		self.temp = list()
		self.result = list()


	def createNameTag(self, domain):
		if domain == '':
			return 'ST_LOAD_LTE_TDD_SH_JX'
		else:
			return 'TDDST_%s_LTE_SH' % (domain)

	def createURL(self, nameTag, level):
		return "http://135.251.227.32/merlin/php/enb_all_time_usage.php?start_d=%s&end_d=%s&stgroup=%s&stat=&sttype=all&omc=all&ustype=all&lab=&level=%s&work_h=1&report_type=daily&sttype=ENB&ustype=all&weekend=1&wnwSort=all_asc&Selection=3&DisableRedirections=False" % (self.startTime, self.endTime, nameTag, level)
	  

	def addAuthHeader(self, url):
		req = urllib2.Request(url)
		b64str = encodestring('%s:%s' % (self.username, self.password))[:-1]
		req.add_header("Authorization", "Basic %s" % b64str)
		return req

	def judgeNotAttr(tag):
		return not tag.has_attr('colspan')

	def analyzeUsagePage(self, URL):
		print URL
		#解析URL,获取内容
		pageTree = BeautifulSoup(BeautifulSoup(urllib2.urlopen(self.addAuthHeader(URL)).read()).prettify())
		contentInBold = pageTree.html.body.table.tbody.find_all('b')
		contentTagTr = pageTree.html.body.table.tbody.find_all('tr')
		subcontent = BeautifulSoup(str(contentTagTr))

		for text in subcontent:
			if BeautifulSoup(str(text)).tr != None: #判断,去掉没有tr的行
				if not BeautifulSoup(str(text)).tr.td.has_attr('colspan'):#判断,去掉没'colspan'属性的td
					info = BeautifulSoup(str(text)).get_text()#获取文本的内容
					self.temp.append(str(info).replace('\n',''))#对换行符进行处理
		for element in self.temp:
			data = element.replace(' '*11,',').replace(' '*6,'').split(',')#对空格进行处理
			del data[0],data[30]#删除第一个和最后一个
			self.result.append(data)		
		return  self.result		
		

	def start(self, groups):
		nameTag = 'all'
		url = self.createURL(nameTag,'all')
		return self.analyzeUsagePage(url)
		

		
def initPrograme(date, groups, username, password):
	instance = createReport(date, username, password)
	result = instance.start(groups)
	return result

if __name__ == '__main__' :
	groups = ["IOT", "LOAD", "KPIQOS", "NLV", "FI-APP", "FI-DIG", "FI-DIG-CAPA", "FI-OAM"]
	date = datetime.today()
	username = 'host'
	password = '123456'
	allPltf = initPrograme(date, groups, username, password)
	# print allPltf
	inputPltfName = raw_input("please input:")
	print 'input : %s' % inputPltfName #输入一个平台的名字，如果在list中有，就输出所有的信息
	for pltf in allPltf:
		if inputPltfName == pltf[0]:
			print pltf
			break 
