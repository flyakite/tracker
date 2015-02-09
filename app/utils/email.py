'''
Created on 2014/11/28

@author: sushih-wen
'''
import re


def is_email_valid(email):
    return re.match(r"[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\.\+_-]+\.[a-zA-Z0-9]+", email)
