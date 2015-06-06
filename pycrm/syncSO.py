# -*- coding: utf-8 -*-
import urllib2
import urllib
import hashlib
import collections
import ssl
import httplib
import json
import logging
import time
import datetime
import binascii
import os
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(filename="..//..//..//logs//syncOrder.log",
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
def to_tag(k, v):
    return '<{key}>{value}</{key}>'.format(key=k, value=get_content(k, v))
def get_content(k, v):
    if isinstance(v, basestring):
        # it's a string, so just return the value
        return unicode(v).encode('utf-8')
    elif isinstance(v, dict):
        # it's a dict, so create a new tag for each element
        # and join them with newlines
        return '\n%s\n' % '\n'.join(to_tag(*e) for e in v.items())
    elif isinstance(v, list):
        # it's a list, so create a new key for each element
        # by using the enumerate method and create new tags
        return '\n%s\n' % '\n'.join(to_tag('{key}-{value}'.format(key=k, value=i + 1), e) for i, e in enumerate(v))
CERT_FILE = 'apiclient_cert.pem'  # Renamed from PEM_FILE to avoid confusion
KEY_FILE = 'apiclient_key.pem'  # This is your client cert!

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)
    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
cert_handler = HTTPSClientAuthHandler(KEY_FILE, CERT_FILE)
opener = urllib2.build_opener(cert_handler)
urllib2.install_opener(opener)

def syncSO():
    #前提：.csv为一天内的数据
    currentTime=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    path="CsvData//{0}.csv".format(time.strftime('%Y%m%d',time.localtime(time.time())))
    logging.debug(path)
    isSuccess=True
    #获取错误时的行号
    errorLineNum=1 #默认错误行号，即从1开始
    fileName="errorLineNumFile.txt" 
    if os.path.exists(fileName):
        errorLineNumFile = open (fileName,'r')
        errorLineNumStr=errorLineNumFile.read()
        isInt=unicode(str(errorLineNumStr)).isdecimal()
        if isInt:
            errorLineNum=int(errorLineNumStr) 
        errorLineNumFile.close()
    #准备进行数据同步（从错误行号开始,默认从头开始，错误号为1）
    if os.path.exists(path):
        with open(path) as cf:
            reader = csv.reader(cf)
            try:
                for row in reader:
                    tmpErrorLineNum=reader.line_num
                    #忽略第一行标题
                    if reader.line_num <= errorLineNum:
                        continue
                    data=row
                    list1=['tradeTime','wxOrderNo','userWXID','tradeType','tradeStatus','bank','currencyType','totalPrice','redPrice'
                           ,'productName','refundOrderNo','refundTotalPrice','refundredPrice','refundType','refundStatus']
                    tradeTime=data[0].replace('`','') #交易时间
                    wxOrderNo=data[5].replace('`','') #微信订单号
                    userWXID=data[7].replace('`','') #客户微信ID
                    tradeType=data[8].replace('`','') #交易类型
                    tradeStatus=data[9].replace('`','') #交易状态
                    bank=data[10].replace('`','') #付款银行
                    currencyType=data[11].replace('`','')#货币种类
                    totalPrice=data[12].replace('`','') #总金额
                    redPrice=data[13].replace('`','') #企业红包金额
                    productName=data[20].replace('`','').decode("gb2312")#商品名称
                    logging.debug("productName={0}".format(productName))
                    refundOrderNo=data[14].replace('`','') #微信退款单号
                    refundTotalPrice=data[16].replace('`','')#退款额度
                    refundredPrice=data[17].replace('`','')#企业红包退款金额
                    refundType=data[18].replace('`','')#退款类型
                    refundStatus=data[19].replace('`','')#退款状态
                    list2=[tradeTime,wxOrderNo,userWXID,tradeType,tradeStatus,bank,currencyType,totalPrice,redPrice
                           ,productName,refundOrderNo,refundTotalPrice,refundredPrice,refundType,refundStatus]
                    sorderData=dict(zip(list1,list2))
                    logging.debug(sorderData)
                    crmSOrder_Insert(sorderData)
            except:
                isSuccess=False
                errorLineNum=tmpErrorLineNum-1
		logging.exception("errorLineNum={0}".format(str(errorLineNum)))
                logging.exception(currentTime)
            #失败则记录下此时的错误行号
            if isSuccess==False:
                if os.path.exists(fileName):
                    errorLineNumFile = open (fileName,'w') 
                    errorLineNumFile.write(str(errorLineNum))
                    errorLineNumFile.close()
            logging.debug("isSuccess={0}".format(str(isSuccess)))
            #对本次同步到销售订单表的数据进行销售统计
            if isSuccess==True:
                syncSalesReport()
                
    else:
        logging.debug("file: {0} not find ".format(path))

#调用本地API创建销售订单及字表
def crmSOrder_Insert(sorderData):
    url="http://127.0.0.1"
    #url="http://192.168.1.109:8000"
    logging.debug("order={0}".format(str(sorderData)))
    data=str(sorderData).replace("u'","\"").replace("'","\"")
    logging.debug("data={0}".format(data))
    req = urllib2.Request("{0}/api/method/pycrm.neworderapi.newOrder".format(url),data=data,headers={'Content-Type': 'application/json','skip':'doraemon'})
    u = urllib2.urlopen(req)
    resp = u.read()
    return resp



#销售业绩统计
def syncSalesReport():
    url="http://127.0.0.1"
    #url="http://192.168.1.109:8000"
    req = urllib2.Request("{0}/api/method/pycrm.neworderapi.newSalesReportData".format(url),headers={'Content-Type': 'application/json','skip':'doraemon'})
    u = urllib2.urlopen(req)
    resp = u.read()
    return resp
syncSO()




