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

logging.basicConfig(filename="..//logs//api.log", level=logging.DEBUG)


@frappe.whitelist()
def setEmployeeWXID():
    try:
        inputdata = frappe.local.request.stream.readlines()
        if inputdata:
            message = ""
            currentTime = datetime.datetime.strftime(
                datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            logging.debug(currentTime+"inputdata[0]="+inputdata[0])
            data = json.loads(inputdata[0])
            em_Name = data["em_Name"]
            em_Mobile = data["em_Mobile"]
            em_WXID = data["em_WXID"]
            logging.debug(
                currentTime+"em_Name={0},em_Mobile={1},em_WXID={2}".format(em_Name, em_Mobile, em_WXID))
            if frappe.db.exists("Employee", {"em_Mobile": em_Mobile, "em_Name": em_Name}):
                empDoc = frappe.get_doc(
                    "Employee", {"em_Mobile": em_Mobile, "em_Name": em_Name})
                empDoc.update(data)
                empDoc.save()
                if empDoc["em_Enabled"] == 1:
                    message = "已经审核您为公司销售"
                else:
                    message = "还未审核您为公司销售"
                frappe.local.response.update(
                    {"state": "update", "message": message})
            else:
                data.update({"doctype": "Employee"})
                data["em_Enabled"] = 0
                frappe.get_doc(data).insert()
                message = "请等待公司审核"
                frappe.local.response.update(
                    {"state": "insert", "message": message})
            frappe.db.commit()
    except:
        logging.exception(currentTime)
