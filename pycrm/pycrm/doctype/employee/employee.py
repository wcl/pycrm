# -*- coding: utf-8 -*-
# Copyright (c) 2015, doracl and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
import time
import datetime
logging.basicConfig(filename="..//logs//api.log",
                    level=logging.DEBUG, format='%(asctime)s %(message)s')
import re


class Employee(Document):

    def before_insert(self):
        logging.debug(
            "编码={0},手机号={1}".format(self.em_Code, self.em_Mobile))
        # 验证编码
        code = self.em_Code
        codeIsint = True
        try:
            code = int(code)
            codeIsint = isinstance(code, int)
        except:
            codeIsint = False
        if codeIsint:
            if int(self.em_Code) > 9999 or int(self.em_Code) < 1:
                message = "编码应为1至9999之间的整数"
                raise Exception(message)
        else:
            message = "您输入的不是整数，编码应为1至9999之间的整数"
            logging.debug(message)
            raise Exception(message)
        # 验证手机号
        if re.search('1\d{10}', self.em_Mobile) == None:
            message = "手机号不合法,请重新录入"
            logging.debug(message)
            raise Exception(message)
        # 验证邮箱

        logging.debug(type(self.em_Email))
        if re.search('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', str(self.em_Email)) == None:
            message = "电子邮箱不合法,请重新录入"
            logging.debug(message)
            raise Exception(message)
