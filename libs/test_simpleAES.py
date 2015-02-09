'''
Created on 2014/12/27

@author: sushih-wen
'''

import unittest
from simpleAES import SimpleAES, SimpleAESException

class TestSimpleAES(unittest.TestCase):
    def test_aes(self):
        key = '1234567890123456'
        plaintext = 'abc'
        cipher = SimpleAES(key)
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        self.assertEqual(decrypted, plaintext)
        
        cipher2 = SimpleAES(key)
        decrypted2 = cipher2.decrypt(encrypted)
        self.assertEqual(decrypted2, plaintext)
        
    def test_aesexceptions(self):
        self.assertRaises(SimpleAESException, SimpleAES, 'fake_key')
        
        
if __name__ == '__main__':
    unittest.main()