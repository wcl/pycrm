# -*- coding: utf-8 -*-
# Copyright (c) 2015, doracl and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import logging
logging.basicConfig(filename="..//logs//api.log", level=logging.DEBUG)
class Employee(Document):
	def validate(self):
                try:
                    currentTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                    test=1/0
                except Exception, e:
                    logging.exception(currentTime)
                    raise
        
