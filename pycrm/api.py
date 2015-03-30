import frappe
import json


@frappe.whitelist()
def query():
    # u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
    # u = frappe.db.exists("customer", "d906c05bf9")
    return 123


@frappe.whitelist()
def newcustomer():
    inputdata = frappe.local.request.stream.readlines()

    data = json.loads(inputdata[0])
    name = data["name"]
    if frappe.db.exists("customer", name):
        return "already exists recode with name is " + name
    data.update({"doctype": "customer"})

    frappe.local.response.update(
        {"data": frappe.get_doc(data).insert().as_dict()})

    frappe.db.commit()
