# -*- coding: utf-8 -*-
import frappe
import json
import logging
import time
import datetime
# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 1:
# ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename="..//logs//syncOrder.log", level=logging.DEBUG)


@frappe.whitelist()
def getEmployeeReport():
    try:
        inputdata = frappe.local.request.stream.readlines()
        if inputdata:
            message = "123"
            currentTime = datetime.datetime.strftime(
                datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            logging.debug(currentTime+"inputdata[0]="+inputdata[0])
            data = json.loads(inputdata[0])
            em_WXID = data["em_WXID"] #销售的微信ID
            logging.debug(currentTime+"em_WXID={0}".format(em_WXID))
            statisticalDate=time.strftime('%Y%m%d',time.localtime(time.time()))#当前日期，如20150522
            key="{0}{1}".format(em_WXID,statisticalDate)
            salesName=""
            emName=frappe.db.get_value("Employee", {"em_WXID": em_WXID}, "em_Name")
            if emName!=None:
                salesName=emName
            #计算当前销售总订单量，订单总金额，订单总退款金额
            orderNumber=0.00
            orderTotalPrice=0.00
            refundTotalPrice=0.00
            sqlStr="""
                   select salesWXID,sum(orderNumber) as orderNumber,
                   sum(orderTotalPrice) as orderTotalPrice,sum(refundTotalPrice) as refundTotalPrice
                   from tabSalesReport where salesWXID='{0}' group by salesWXID
                   """.format(em_WXID)
            logging.debug("sqlStr={0}".format(sqlStr))
            reportList=frappe.db.sql(sqlStr, as_dict=True)
            for reportData in reportList:
                logging.debug("reportData={0}".format(str(reportData)))
                orderNumber=reportData["orderNumber"]
                orderTotalPrice=reportData["orderTotalPrice"]
                refundTotalPrice=reportData["refundTotalPrice"]
                
            #计算昨天的销售业绩
            if frappe.db.exists("SalesReport", key):
                message="销售业绩"
                logging.debug(message)
                doc = frappe.get_doc("SalesReport", key)
                orderNumberCurrent=doc.orderNumber
                orderTotalPriceCurrent=doc.orderTotalPrice
                refundNumberCurrent=doc.refundNumber
                refundTotalPriceCurrent=doc.refundTotalPrice
                frappe.local.response.update({"salesName":salesName,"orderNumber":orderNumber,"orderTotalPrice":orderTotalPrice,"refundTotalPrice":refundTotalPrice
                                              ,"orderNumberCurrent": orderNumberCurrent,"orderTotalPriceCurrent":orderTotalPriceCurrent,"refundNumberCurrent":refundNumberCurrent
                                              ,"refundTotalPriceCurrent":refundTotalPriceCurrent,"message":message})
            else:
                message="暂无销售业绩"
                logging.debug(message)
                frappe.local.response.update({"salesName":salesName,"orderNumber":orderNumber,"orderTotalPrice":orderTotalPrice,"refundTotalPrice":refundTotalPrice
                                              ,"orderNumberCurrent": 0,"orderTotalPriceCurrent":0.00,"refundNumberCurrent":0,"refundTotalPriceCurrent":0.00
                                              ,"message":message})
    except:
        logging.exception(currentTime)
