'''
Created on 2014/12/4

@author: sushih-wen
'''
import logging
import datetime
from ferris import scaffold
from ferris import route_with
from base import BaseController
from app.models.user_info import UserInfo


class ZenLog(BaseController):

    @route_with('/zenlog')
    def user_list(self):

        self.meta.change_view('json')
        package_version = self.request.get('zbversion')
        outlook_version = self.request.get('oversion')
        level = self.request.get('level', '').strip().lower()
        email = self.request.get('email').strip().lower()
        msg = self.request.get('msg')

        logging.info("version: " + package_version + " outlook: " + outlook_version)
        logging.info('zenlog_email: ' + email)

        if level == 'debug':
            msg = 'zenlog debug: ' + msg
            logging.debug(msg)
        elif level == 'info':
            msg = 'zenlog info: ' + msg
            logging.info(msg)
        elif level in ['warning', 'warn']:
            msg = 'zenlog warning: ' + msg
            logging.warn(msg)
        elif level == 'error':
            msg = 'zenlog error: ' + msg
            logging.error(msg)
        elif level in ['critical', 'fatal']:
            msg = 'zenlog fatal: ' + msg
            logging.fatal(msg)
        else:
            msg = 'zenlog error: ' + msg
            logging.error(msg)
