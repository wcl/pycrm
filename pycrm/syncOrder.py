# -*- coding: utf-8 -*-
import urllib2
import urllib
import hashlib
import collections
import ssl
import httplib
#import frappe
import json
import logging
import time
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename="..//logs//api.log",
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

def syncOrder():
    currentTime=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    try:
        access_token=""
        try:
            logging.debug("get access_token from php server")
            phpInfo=urllib2.urlopen("http://xylapp.sinaapp.com/token.php")
            access_token=phpInfo.read()
            logging.debug("php server-->access_token={0}".format(access_token))
        except:
            logging.exception(currentTime)
            access_token=createAccessTocken()
        if access_token!="":
            #微信小店，订单列表查询
            req = urllib2.Request("https://api.weixin.qq.com/merchant/order/getbyfilter?access_token="+access_token,data='{"status":2}', headers={'Content-Type': 'application/xml'})
            u = urllib2.urlopen(req)
            resp = u.read()
            data=json.loads(resp)
            if data["errcode"]==0:
                orderList = json.loads(resp)["order_list"]
                for order in orderList:
                    crmOrder_Create(order)
            else:
                logging.error("调用订单接口出错，errcode={0},errinfo={1}".format(data["errcode"],data["errmsg"]))
            
            #扫码购买商品,对账单接口
            pass
            
        else:
            logging.debug("access_token为空，无法调用微信接口")
    except:
        logging.exception("error")

#自己创建access_token
def createAccessTocken():
    currentTime=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    access_token=""
    try:
        logging.debug("self create access_token")
        appid="wx36177abf9259c7ff"
        secret="1998afc9601e372c09b6cc665fdb3c1f"
        info=urllib2.urlopen("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(appid,secret))
        access_token=json.load(info)["access_token"]
        logging.debug("self create-->access_token={0}".format(access_token))
    except:
        logging.exception(currentTime)
    return access_token

#微信小店订单集合
def crmOrder_Create(order):
    logging.debug("order={0}".format(str(order)))
    data=str(order).replace("u'","\"").replace("'","\"")
    logging.debug("data={0}".format(data))
    req = urllib2.Request("http://192.168.21.93:8000/api/method/pycrm.neworderapi.newOrder",data=data,headers={'Content-Type': 'application/json','skip':'doraemon'})
    u = urllib2.urlopen(req)
    resp = u.read()
    return resp

#通过客户微信ID查找对应的销售人员微信ID
"""
def (cus_wxid):
    saleswxid=""
    if frappe.db.exists("Customer", cus_wxid):
        doc = frappe.get_doc("Customer", cus_wxid)
        if doc["cus_salesmanCode"]!=None:
            saleswxid=doc["cus_salesmanCode"]
    return saleswxid
"""

syncOrder()
"""
token="5YF3YVeDSz1nM-qacqR6BIk_v18fALG1bun52Mh6gJCWv2pnyOYO34F1YSR9YNwDbVJN4B1X4r9aJSOqfWbGwaUIdLJ1VveBW0bMsSiIF-g"
req = urllib2.Request("https://api.weixin.qq.com/merchant/order/getbyfilter?access_token="+token,data='{"status":2}', headers={'Content-Type': 'application/xml'})
print req
u = urllib2.urlopen(req)
resp = u.read()
res = json.loads(resp)["order_list"]
print res
print type(res)
"""



