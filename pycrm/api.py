import frappe
import json


@frappe.whitelist()
def query():
    # u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
    # u = frappe.db.exists("customer", "d906c05bf9")
    print frappe.local.form_dict.keys()
    return 123


@frappe.whitelist()
def newcustomer():
    inputdata = frappe.local.request.stream.readlines()
    name = ""
    if inputdata:
    	data = json.loads(inputdata[0])
    	name = data["name"]
    if frappe.db.exists("customer", name):
        return "already exists recode with name is " + name
    data.update({"doctype": "customer"})

    frappe.local.response.update(
        {"data": frappe.get_doc(data).insert().as_dict()})

    frappe.db.commit()


@frappe.whitelist()
def cancel():
    pass

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
    frappe.db.set("customer","cus_image",ret["file_url"])
    return ret