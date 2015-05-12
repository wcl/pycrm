# -*- coding: utf-8 -*-  
import frappe
import json
import logging
import time,datetime
#UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 1: ordinal not in range(128)
import sys
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename="..//logs//api.log",level=logging.DEBUG)

@frappe.whitelist(allow_guest=True)
def query():
    # u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
    # u = frappe.db.exists("customer", "d906c05bf9")
    # print frappe.local.form_dict.keys()
    logging.debug("query-123")
    return 123

@frappe.whitelist()
def newcustomer():
    try:
        inputdata = frappe.local.request.stream.readlines()
        if inputdata:
            currentTime=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            logging.debug(currentTime+"inputdata[0]="+inputdata[0])
            data = json.loads(inputdata[0])
            name = data["name"]
            data['cus_attention'] = 1
            data['cus_code'] = name #
            employeeMark = data["cus_body"].encode('utf-8')  # em_Code,em_Mobile,em_Email
            message=""
            em_WXID="" #employee weixin ID
            emNum=0
            if employeeMark.startswith("last_trade_no"):
                employeeMark=""
            if employeeMark == "":
                data["cus_remark"] = "invlid input "
            else:
                em_Code = frappe.db.get_value("Employee", {"em_Code": employeeMark}, "em_Code")
                if data["isbind"]=="1":
                    if em_Code == None: 
                        em_Code = frappe.db.get_value("Employee", {"em_Mobile": employeeMark}, "em_Code")
                        if em_Code==None:
                            em_Code = frappe.db.get_value("Employee", {"em_Email": employeeMark}, "em_Code")
                            if em_Code==None:
                                logging.debug("employeeMark={0}".format(employeeMark))
                                em_Code = frappe.db.get_value("Employee", {"em_Name": employeeMark}, "em_Code")
                                if em_Code==None:
                                    data["cus_remark"] = "Bind,input not find by Code,Mobile,Email: {0} ".format(employeeMark)
                                    message=u"通过编码，手机号，邮箱,姓名均未找到对应的销售人员，请联系相关销售人员"
                                else:
                                    emNum=frappe.db.count("Employee", {"em_Name": employeeMark})
                                    if emNum==1:
                                        data["cus_salesmanCode"] = em_Code
                                        data["cus_remark"] = "Bind,input  find by Name={0} ".format(employeeMark)
                                    else:
                                        #find muilty employee by Name
                                        message=u"姓名为{0}的销售人员存在{1}个，具体信息如下：\n".format(employeeMark,str(emNum))
                                        multinfos=""
                                        em_Codes=frappe.db.get_values("Employee", {"em_Name": employeeMark}, "em_Code")
                                        for code in em_Codes:
                                            code=code[0]
                                            #logging.debug("em_Codes-code={0}".format(code))
                                            mobile=frappe.db.get_value("Employee", {"em_Code": code}, "em_Mobile")
                                            email=frappe.db.get_value("Employee", {"em_Code": code}, "em_Email")
                                            multinfos=multinfos+u"编码={0},手机号={1},邮箱={2};\n".format(code,mobile,email)
                                            #logging.debug("multinfos={0}".format(multinfos))
                                        multinfos=multinfos+u"请您重新根据编码，手机号或邮箱进行支持,谢谢！"
                                        #logging.debug("multinfos-Last={0}".format(multinfos))
                                        message=message+multinfos
                                        #logging.debug("message-Last={0}".format(message))
                                        
                            else:
                                data["cus_salesmanCode"] = em_Code
                                data["cus_remark"] = "Bind,input  find by Email={0} ".format(employeeMark)
                        else:
                            data["cus_salesmanCode"] = em_Code
                            data["cus_remark"] = "Bind,input  find by Mobile={0} ".format(employeeMark)
                    else:
                        data["cus_salesmanCode"] = em_Code
                        data["cus_remark"] = "Bind,input find by Code={0} ".format(em_Code)
                else:
                    if em_Code == None:
                        data["cus_remark"] = "Scan code,input not find by Code={0} ".format(em_Code)
                    else:
                        data["cus_salesmanCode"] = em_Code
                        data["cus_remark"] = "Scan,input find by Code={0} ".format(em_Code)
                #find Employee Name
                if em_Code != None:
                    if emNum==1:
                        em_Name = frappe.db.get_value("Employee", {"em_Code": em_Code}, "em_Name")
                        em_WXID = frappe.db.get_value("Employee", {"em_Code": em_Code}, "em_WXID")
                        if data["isbind"]=="1":
                            if em_Name != None:
                                logging.debug("em_Code={0},name={1}".format(em_Code,name))
                                numbers=frappe.db.count("Customer", {"cus_salesmanCode": em_Code})+1
                                doctypes = frappe.db.sql_list("select cus_Name from tabCustomer where cus_salesmanCode=='{0}' and name!='{1}'").format(em_Code,name)
                                logging.debug("doctypes={0}".format(str(doctypes)))
                                message=u"谢谢您的参与,销售人员：{0}共有{1}位支持者".format(em_Name,numbers)
                        else:
                            #only display name by saoma
                            if em_Name != None:
                                message=u"{0}".format(em_Name)
                        
        if frappe.db.exists("Customer", name):
            # return "already exists recode with name is " + name
            doc = frappe.get_doc("Customer", name)
            doc.update(data)
            doc.save()
            #return message
            #frappe.local.response.update({"data":doc.save().as_dict(),"status": "update","message":message})
            frappe.local.response.update({"EmployeeWXID": em_WXID,"message":message})
        else:
            data.update({"doctype": "Customer"})
            frappe.get_doc(data).insert()
            #return message
            #frappe.local.response.update({"data": frappe.get_doc(data).insert().as_dict(),"status": "insert","message":message})
            frappe.local.response.update({"EmployeeWXID": em_WXID,"message":message})
        frappe.db.commit()
    except :
        logging.exception(currentTime)

@frappe.whitelist()
def cancelatt():
    print frappe.form_dict
    docname = frappe.form_dict.get('docname')
    frappe.set_value("Customer", docname, 'cus_attention', 0)
    frappe.db.commit()
    return "ok"
@frappe.whitelist()
def uploadfile():
    try:
        if frappe.form_dict.get('from_form'):
            try:
                ret = frappe.utils.file_manager.upload()
            except frappe.DuplicateEntryError:
                # ignore pass
                ret = None
                frappe.db.rollback()
        else:
            if frappe.form_dict.get('method'):
                ret = frappe.get_attr(frappe.form_dict.method)()
    except Exception:
        frappe.errprint(frappe.utils.get_traceback())
        ret = None
    docname = frappe.form_dict.get('docname')
    value = ret['file_url']
    #logger.debug(docname + "," + value)
    frappe.set_value("Customer", docname, "cus_image", value)
    frappe.db.commit()
    # doc = frappe.get_doc(":", frappe.form_dict.get('docname'))
    # frappe.db.set(doc,"cus_image",ret["file_url"])
    return ret
