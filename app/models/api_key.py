'''
Created on 2014/12/25

@author: sushih-wen
'''
import logging
import hashlib
from uuid import uuid4
from datetime import datetime
from ferris import BasicModel
from google.appengine.ext import ndb
from ferris import settings
from libs.simpleAES import SimpleAES


class ApiKey(BasicModel):

    """
    Use stateless api key and secret
    secret is a hash of access_id, the key with salt
    """
    access_id = ndb.StringProperty(required=True)
    secret = ndb.TextProperty(required=True)
    owner = ndb.StringProperty(required=True)

    @classmethod
    def create_key(cls):
        return str(uuid4()).replace('-', '')

    @classmethod
    def create_secret(cls, key, salts=settings.get('API_SECRET_SALTS', [])):
        sha = hashlib.sha1()
        if not salts:
            salts = ['']
        sha.update(key + salts[0])
        return sha.hexdigest()

    @classmethod
    def verify_secret(cls, key, secret, salts=settings.get('API_SECRET_SALTS', [])):
        """
        veirfied if any of the salt works
        """
        if not salts:
            salts = ['']
        for salt in salts:
            secret_to_check = cls.create_secret(key, salts=[salt])
            if secret_to_check == secret:
                return True
        return False

    @classmethod
    def create_token(cls, access_id, secret, aes_cipher_key=settings.get('API_SECRET_AES_KEY', '')):
        if not aes_cipher_key:
            logging.error('NO_API_SECRET_AES_KEY_Error: %s' % access_id)
            return None

        text = access_id + "|" + \
            secret + "|" + \
            str(datetime.utcnow().isoformat()) + "|" + \
            str(uuid4())[:8]

        token = None
        try:
            cipher = SimpleAES(aes_cipher_key)
            token = cipher.encrypt(text)
        except Exception as ex:
            logging.info(text)
            logging.error("ApiKey_Cipher_Error")
            logging.error(ex)
        return token

    @classmethod
    def verify_token(cls, access_id, token, aes_cipher_key=settings.get('API_SECRET_AES_KEY', '')):
        #expire = settings.get('API_TOKEN_EXPIRE')
        cipher = SimpleAES(aes_cipher_key)
        try:
            decrpyted = cipher.decrypt(token)
        except:
            logging.error('des.decrypt_failed: %s' % access_id)
            return False
        origin = decrpyted.split('|')
        if len(origin) >= 2:
            if access_id == origin[0]:
                secret = origin[1]
                if cls.verify_secret(access_id, secret):
                    # TODO: verify timestamp
                    return True

        return False
