'''
Created on 2014/11/30

@author: sushih-wen
'''
import logging
from app.models.user_info import UserInfo
from app.models.domain import Domain
from email import is_email_valid


def is_user_legit(email_or_user):
    """
    Check if the user is domain legit or self legit
    """
    if isinstance(email_or_user, str) or isinstance(email_or_user, unicode):
        email = email_or_user
        if not is_email_valid(email):
            logging.info('email_not_valid: %s' % email)
            return {'result': 0}
        user = UserInfo.find_by_properties(email=email)
    else:
        user = email_or_user
        email = user.email

    domain = email.split('@')[1].lower()
    domain = Domain.find_by_properties(domain=domain)
    if domain and domain.is_legit():
        logging.info('domain_is_legit: %s' % email)
        return {'result': 1}

    if user:
        if user.is_self_legit():
            logging.info('user_is_legit: %s' % email)
            return {'result': 1}
        else:
            logging.info('user_not_legit: %s' % email)
            return {'result': 0, 'error': 'user_not_legit'}
    else:
        logging.info('user_not_found: %s' % email)
        return {'result': 0, 'error': 'user_not_found'}
