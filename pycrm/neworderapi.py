# -*- coding: utf-8 -*-
import frappe
import json
import logging
import time
import datetime
import time
from datetime import timedelta, date

# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 1:
# ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(filename="..//logs//syncOrder.log", level=logging.DEBUG)


@frappe.whitelist(allow_guest=True)
def newOrder():
    try:
	inputdata = frappe.local.request.stream.readlines()
        if inputdata:
            message = ""
            currentTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            keydate = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')
            logging.debug(currentTime+"inputdata[0]="+inputdata[0])
            data = json.loads(inputdata[0])
            data["productName"]=data["productName"].encode('utf-8')
            data["salesWXID"]=getSalesidBycusID(data["userWXID"])
            orderNo=data["wxOrderNo"]
            refundOrderNo=data["refundOrderNo"]
            #key=refundOrderNo+keydate
	    logging.debug(orderNo)
            if frappe.db.exists("SOrder", orderNo):
                #如果是退货单，则必定之前有对应的销售订单
                order = frappe.get_doc("SOrder", orderNo)
                if data["refundType"]!="":
		    logging.debug(refundOrderNo)
                    data.update({"doctype": "SOrderLine"})
                    #data["key"]=key
                    data["parent"]=orderNo
                    data["parentfield"]="SOrderLine"
		    data["parenttype"]="SOrder"
		    frappe.get_doc(data).insert()
		    #update SOrder
		    frappe.set_value("SOrder", orderNo, 'refundNumber', order.refundNumber+1)
		    #退款-退红包或优惠劵
		    refundTotalPrice=order.refundTotalPrice+float(data["refundTotalPrice"])
                    frappe.set_value("SOrder", orderNo, 'refundTotalPrice',refundTotalPrice )
                    
                    refundredPrice=order.refundredPrice+float(data["refundredPrice"])
		    frappe.set_value("SOrder", orderNo, 'refundredPrice',refundredPrice )
            else:
                #销售订单头,注意是退款单
                if data["refundType"]=="":
                    data.update({"doctype": "SOrder"})
                    frappe.get_doc(data).insert()
                else:
                    #不应该存在无订单就有退货单的可能
                    pass
            frappe.db.commit()
    except:
        logging.exception(currentTime)

#时间戳转时间
def convertTime(sjc):
    x = time.localtime(sjc)
    t=time.strftime('%Y-%m-%d %H:%M:%S',x)
    return t

#获取销售人员微信ID
def getSalesidBycusID(userWXID):
    saleswxid="o6j3_spyEyqcSTWzASEBvehkQm-A" #TO:殷雄微信ID,后期应该清空
    if frappe.db.exists("Customer", userWXID):
        doc = frappe.get_doc("Customer", userWXID)
        if doc.cus_salesmanCode!=None:
	    em_wxid=frappe.db.get_value("Employee", {"em_Code": doc.cus_salesmanCode,"em_Enabled":"1"}, "em_wxid")
	    if em_wxid!=None:
	        saleswxid=em_wxid
    return saleswxid

@frappe.whitelist(allow_guest=True)
def newSalesReportData():
    currentTime=datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')
    statisticalDate=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    #对SOrder中的当天的数据进行汇总统计
    sqlStr="""
           select salesWXID,sum(totalprice-redPrice) as orderTotalPrice,count(1) as orderNumber,
                     sum(refundNumber) as refundNumber,sum(refundTotalPrice-refundredPrice) as refundTotalPrice,
                     date_format(tradeTime,'%Y%m%d') as tradeDate
           from tabSOrder group by saleswxid,date_format(tradeTime,'%Y%m%d')
           """
    logging.debug("sqlStr={0}".format(sqlStr))
    try:
        reportList=frappe.db.sql(sqlStr, as_dict=True)
        for reportData in reportList:
            logging.debug("reportData={0}".format(str(reportData)))
            key=reportData["salesWXID"]+reportData["tradeDate"]
	    reportData["key"]=key
            reportData["StatisticalDate"]=statisticalDate
            crmSalesReport_Insert(reportData)
            
    except:
        logging.exception(currentTime)

def crmSalesReport_Insert(data):
    try:
        message = "123"
        currentTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        key=data["key"]
	logging.debug(key)
        if frappe.db.exists("SalesReport", key):
            pass
        else:
            #销售报表数据
            data.update({"doctype": "SalesReport"})
            frappe.get_doc(data).insert()
        frappe.db.commit()
    except:
        logging.exception(currentTime)
