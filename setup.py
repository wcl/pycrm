# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='pycrm',
    version=version,
    description='客户关系管理系统',
    author='doracl',
    author_email='doracl@rd.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
