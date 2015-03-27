import frappe

@frappe.whitelist()
def get_logged_user():
	u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
	return u.cus_name