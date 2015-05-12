# -*- coding: utf-8 -*-  
import frappe
import json
import logging
import time,datetime
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
            employeeMark = data["cus_body"]  # em_Code,em_Mobile,em_Email
            message=""
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
                                    message=u"通过编码，手机号，邮箱,姓名均未找到对应的销售人员"
                                else:
                                    emNum=frappe.db.count("Employee", {"em_Name": employeeMark})
                                    if emNum==1:
                                        data["cus_salesmanCode"] = em_Code
                                        data["cus_remark"] = "Bind,input  find by Name={0} ".format(employeeMark)
                                    else:
                                        #find muilty employee by Name
                                        message=u"姓名为{0}的销售人员存在多个，信息如下：\n".format(employeeMark)
                                        multinfos="";
                                        em_Codes=frappe.db.get_values("Employee", {"em_Name": employeeMark}, "em_Code")
                                        for code in em_Codes:
                                            mobile=frappe.db.get_value("Employee", {"em_Code": code}, "em_Mobile")
                                            email=frappe.db.get_value("Employee", {"em_Code": code}, "em_Email")
                                            multinfos=multinfos+u"Code={0},Mobile={1},Email={2};\n".format(code,mobile,email)
                                        message=message+multinfos
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
                    em_Name = frappe.db.get_value("Employee", {"em_Code": em_Code}, "em_Name")
                    if data["isbind"]=="1":
                        if em_Name != None:
                            numbers=frappe.db.count("Customer", {"cus_salesmanCode": em_Code})+1
                            message=u"您是销售人员：{0}的第{1}位支持者".format(em_Name,numbers)
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
            frappe.local.response.update({"EmployeeCusID": "123","message":message})
        else:
            data.update({"doctype": "Customer"})
            frappe.get_doc(data).insert()
            #return message
            #frappe.local.response.update({"data": frappe.get_doc(data).insert().as_dict(),"status": "insert","message":message})
            frappe.local.response.update({"EmployeeCusID": "456","message":message})
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
