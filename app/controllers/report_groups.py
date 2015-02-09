'''
Created on 2014/10/4

@author: sushih-wen
'''
import logging
import datetime
from ferris import scaffold
from ferris import route_with
from base import BaseController
from app.models.report_group import ReportGroup


class ReportGroups(BaseController):

    """
    We can also use ferris pagination, messages
    """
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding,)

    admin_list = scaffold.list
    admin_view = scaffold.view
    admin_add = scaffold.add
    admin_edit = scaffold.edit
    admin_delete = scaffold.delete
