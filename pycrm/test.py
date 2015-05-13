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


@frappe.whitelist(allow_guest=True)
def query():
    # u = frappe.db.sql("select * from tabcustomer", as_dict=True)[0]
    # u = frappe.db.exists("customer", "d906c05bf9")
    # print frappe.local.form_dict.keys()
    #u = frappe.db.get_values("Customer", {"cus_name": ("!=", 'wwq')}, "*")
    u = frappe.db.exists(
                    "Employee", {"em_Mobile": "13212345625", "em_Name": "殷雄"})
    return u
