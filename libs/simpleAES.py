'''
Created on 2014/12/27

@author: sushih-wen
'''
from Crypto.Cipher import AES
from Crypto import Random


class SimpleAESException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SimpleAES():
    
    def __init__(self, key):
        if len(key) % 16 != 0:
            raise SimpleAESException('Key length must be multiple of 16')
        self.key = key
        self.iv = None
       
    def encrypt(self, plaintext):
        try:
            self.iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        except Exception as ex:
            raise SimpleAESException(ex)
        try:
            return self.iv + cipher.encrypt(plaintext)
        except Exception as ex:
            raise SimpleAESException(ex)
    
    def decrypt(self, ciphertext):
        if not self.iv:
            self.iv = ciphertext[:AES.block_size]
        encrypted = ciphertext[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        try:
            return cipher.decrypt(encrypted)
        except Exception as ex:
            raise SimpleAESException(ex)