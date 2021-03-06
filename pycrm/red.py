# -*- coding: utf-8 -*-
import urllib2
import urllib
import hashlib
import collections
import ssl
import httplib
import frappe
import json
import logging
import time
import datetime
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


def getbody(data):
    data["nonce_str"] = "d2asf1323242sdf1a"
    myKey = data["key"]
    del data["key"]
    logging.debug("data=" + str(data))

    newdata = dict(
        [k.encode('utf-8'), unicode(v).encode('utf-8')] for k, v in data.items())

    querydata = sorted(newdata.items())

    query_str = ""
    for key, value in querydata:
        query_str += key + "=" + value + "&"

    logging.debug("query_str:" + query_str)
    # query_str = urllib.urlencode(sorteddata) + "&key=" + myKey
    query_str += unicode("key=" + myKey).encode('utf-8')

    sign = hashlib.md5(query_str).hexdigest().upper()
    data["sign"] = sign
    body = to_tag("xml", data)
    logging.debug("body=" + str(body))
    return body


@frappe.whitelist(allow_guest=True)
def sendred():
    try:
        inputdata = frappe.local.request.stream.readlines()

        if inputdata:
            logging.debug("inputdata[0]=" + inputdata[0])
            data = json.loads(inputdata[0])
            #global num
            # snum=str(num+1)
            #billno = data["mch_id"] + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d') + str(time.time())[0:10]
            #data["mch_billno"] = billno
            #logging.debug("billno=" + billno)

            req = urllib2.Request("https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack",
                                  data=getbody(data), headers={'Content-Type': 'application/xml'})
            u = urllib2.urlopen(req)
            response = u.read()
            logging.debug(response)
            return response
    except:
        logging.exception()


@frappe.whitelist(allow_guest=True)
def sendcoupon():
    try:
        inputdata = frappe.local.request.stream.readlines()

        if inputdata:
            logging.debug("inputdata[0]=" + inputdata[0])
            data = json.loads(inputdata[0])
            #global num
            # snum=str(num+1)

            req = urllib2.Request("https://api.mch.weixin.qq.com/mmpaymkttransfers/send_coupon",
                                  data=getbody(data), headers={'Content-Type': 'application/xml'})
            u = urllib2.urlopen(req)
            response = u.read()
            logging.debug(response)
            return response
    except:
        logging.exception()
