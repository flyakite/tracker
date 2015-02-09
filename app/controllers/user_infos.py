'''
Created on 2014/10/4

@author: sushih-wen
'''
import logging
import datetime
from ferris import scaffold
from ferris import route_with
from base import BaseController
from app.models.user_info import UserInfo


class UserInfos(BaseController):

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

#     @route_with('/updateuser')
#     def update(self):
#         self.meta.change_view('json')
#         d=self.request.get('d')
#         d=datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
#         logging.info(d)
#         u = UserInfo.find_by_properties(email='aab@cc.com')
#         u.orgs = ['asdf','qwer']
#         u.put()
#         self.context['data']={'d':d}
