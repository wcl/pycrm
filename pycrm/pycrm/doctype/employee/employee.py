# -*- coding: utf-8 -*-
# Copyright (c) 2015, doracl and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import logging
logging.basicConfig(filename="..//logs//api.log",
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
class Employee(Document):
	def validate(self):
                try:
                    test=1/0
                except Exception, e:
                    logging.exception()
                    raise
        
