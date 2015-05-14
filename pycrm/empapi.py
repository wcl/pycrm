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
            code='1'#默认
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
                    message = "您已正式成为鑫玉龙销售团队的一员"
                else:
                    message = "欢迎加入鑫玉龙销售团队，请联系管理员核准启用"
                frappe.local.response.update({"state": "update","code":code,"name":em_Name, "message": message})
            else:
                emMaxCodes=frappe.db.sql_list("select  em_Code from tabEmployee order by (em_Code+0) desc limit 1 ")
                logging.debug("emMaxCodes={0},emMaxCodes[0]={1}".format(str(emMaxCodes),str(emMaxCodes[0])))
                if len(emMaxCodes)>0:
                    nextCode=int(emMaxCodes[0])+1
                    code=str(nextCode)
                    if nextCode>9999:
                        #删除将编码最小的未启用的销售人员替换掉
                        emMinCodes=frappe.db.sql_list("select  em_Code from tabEmployee where em_Enabled=1 order by (em_Code+0) limit 1 ")
                        if len(emMinCodes)>1:
                            code=str(emMinCodes[0])
                            logging.debug("未启用销售中，最小编码={0}".format(code))
                            empDoc = frappe.get_doc("Employee", {"em_Code": code})
                            if empDoc!=None:
                                data["em_Enabled"] = 0
                                data["em_Code"] = code
                                data["em_Address"]=""
                                data["em_Email"]=""
                                data["em_Telephone"]=""
                                empDoc.update(data)
                                empDoc.save()
                            else:
                                logging.debug("通过Code={0}未找到销售人员记录".format(code))
                        else:
                            #已经存在9999已启用的销售
                            message="销售团队已满,感谢您的参与"
                    else:
                        data.update({"doctype": "Employee"})
                        data["em_Enabled"] = 0
                        data["em_Code"] = code
                        frappe.get_doc(data).insert()
                    message = "欢迎加入鑫玉龙销售团队，请联系管理员核准启用"
                    frappe.local.response.update({"state": "insert", "code":code,"name":em_Name,"message": message})
                frappe.db.commit()
                else :
                    #销售表无记录时，即：第一个加入销售团队的人
                    data["em_Enabled"] = 0
                    data["em_Code"] = code #此时code=1
                    data.update({"doctype": "Employee"})
                    frappe.get_doc(data).insert()
                    message = "欢迎加入鑫玉龙销售团队，请联系管理员核准启用"
                    frappe.local.response.update({"state": "insert", "code":code,"name":em_Name,"message": message})
    except:
        logging.exception(currentTime)
