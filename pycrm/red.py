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
logging.basicConfig(filename="..//logs//api.log", level=logging.DEBUG)


def to_tag(k, v):
    return '<{key}>{value}</{key}>'.format(key=k, value=get_content(k, v))


def get_content(k, v):
    if isinstance(v, basestring):
        # it's a string, so just return the value
        return str(v)
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
num=0
@frappe.whitelist(allow_guest=True)
def sendred():
    try:
        inputdata = frappe.local.request.stream.readlines()
        currentTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        if inputdata:
            logging.debug(currentTime + "inputdata[0]=" + inputdata[0])
            data = json.loads(inputdata[0])
            global num
            snum=str(num+1)
            billno = data["mch_id"] + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d') + (10-len(snum))*'0'+snum
            data["mch_billno"]=billno
            logging.debug(currentTime + "billno=" + billno)
            data["nonce_str"] = "d2asf1323242sdf1a"
            logging.debug(currentTime + "data=" + str(data))
            query_str = urllib.urlencode(
                sorted(data.items())) + "&key=" + data["key"]
            sign = hashlib.md5(query_str).hexdigest().upper()
            data["sign"] = sign
            body = to_tag("xml", data)
            logging.debug(currentTime + "body=" + str(body))
            req = urllib2.Request("https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack",
                                  data=body, headers={'Content-Type': 'application/xml'})
            u = urllib2.urlopen(req)
            response = u.read()
            return response
    except:
        logging.exception(currentTime)

