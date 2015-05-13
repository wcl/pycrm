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
            code='1'
            currentTime = datetime.datetime.strftime(
                datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            logging.debug(currentTime+"inputdata[0]="+inputdata[0])
            data = json.loads(inputdata[0])
            em_Name = data["em_Name"].encode('utf-8') #
            em_Mobile = data["em_Mobile"]
            em_WXID = data["em_WXID"]
            logging.debug(currentTime+"em_Name={0},em_Mobile={1},em_WXID={2}".format(em_Name, em_Mobile, em_WXID))
            emCode=frappe.db.get_value("Employee", {"em_Mobile": em_Mobile, "em_Name": em_Name}, "em_Code")
            if emCode != None:
                empDoc = frappe.get_doc("Employee", {"em_Mobile": em_Mobile, "em_Name": em_Name})
                empDoc.update(data)
                empDoc.save()
                code=emCode
                if empDoc.as_dict()["em_Enabled"] == 1:
                    message = "注册成功"
                else:
                    message = "注册成功，请联系管理员核查"
                frappe.local.response.update({"state": "update","code":code, "message": message})
            else:
                emMaxCodes=frappe.db.sql_list("select  em_Code from tabEmployee order by (em_Code+0) desc limit 1 ")
                logging.debug("emMaxCodes={0},emMaxCodes[0]={1}".format(str(emMaxCodes),str(emMaxCodes[0])))
                code=str(int(emMaxCodes[0])+1)
                data.update({"doctype": "Employee"})
                data["em_Enabled"] = 0
                data["em_Code"] = code
                frappe.get_doc(data).insert()
                message = "您是新注册，请联系管理员核查"
                frappe.local.response.update({"state": "insert", "code":code,"message": message})
            frappe.db.commit()
    except:
        logging.exception(currentTime)
