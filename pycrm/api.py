# -*- coding: cp936 -*-
import frappe
import json


logger = frappe.get_logger()


@frappe.whitelist(allow_guest=True)
def query():
    # u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
    # u = frappe.db.exists("customer", "d906c05bf9")
    # print frappe.local.form_dict.keys()
    return 123


@frappe.whitelist()
def newcustomer():
    inputdata = frappe.local.request.stream.readlines()
    if inputdata:
        data = json.loads(inputdata[0])
        name = data["name"]
        data['cus_attention'] = 1
        employeeCode = data["cus_body"]  # get employee code
        if employeeCode == "":
            data["cus_remark"] = "invlid input "
        elif frappe.db.exists("Employee", {"em_Code": employeeCode}):
            headInfo = frappe.get_doc("Employee", employeeCode)
            data["cus_salesmanName"] = headInfo["em_Name"]
            data["cus_salesmanCode"] = employeeCode
        else:
            data["cus_remark"] = "input not find code={0} ".format(
                employeeCode)
    if frappe.db.exists("customer", name):
        # return "already exists recode with name is " + name
        doc = frappe.get_doc("customer", name)
        doc.update(data)
        frappe.local.response.update({
            "data": doc.save().as_dict(),
            "status": "update"
        })
    else:
        data.update({"doctype": "customer"})
        frappe.local.response.update({
            "data": frappe.get_doc(data).insert().as_dict(),
            "status": "insert"
        })

    frappe.db.commit()


@frappe.whitelist()
def cancelatt():
    print frappe.form_dict
    docname = frappe.form_dict.get('docname')

    frappe.set_value("customer", docname, 'cus_attention', 0)
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
    frappe.set_value("customer", docname, "cus_image", value)
    frappe.db.commit()
    # doc = frappe.get_doc("customer", frappe.form_dict.get('docname'))
    # frappe.db.set(doc,"cus_image",ret["file_url"])
    return ret
