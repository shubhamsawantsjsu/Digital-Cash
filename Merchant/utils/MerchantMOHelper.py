from BitVector import *
import sys
import random
import Crypto
from Crypto.PublicKey import RSA
import hmac

class MerchantMOHelper():

    def __init__(self, pub_key):
        self.pub_key = pub_key

    # Selects random pairs and sends to the customer
    def RandomSelector(self):

        MyList = []

        x = random.randint (0, 1)
        MyList.append (str (x))
        x = random.randint (2, 3)
        MyList.append (str (x))
        x = random.randint (4, 5)
        MyList.append (str (x))
        x = random.randint (6, 7)
        MyList.append (str (x))

        MyStr = ",".join (MyList)
        return MyStr

    def BitCommit (self, message, key):
        from hashlib import sha1
        
        hashed = hmac.new(key, message, sha1)

        # The signature
        return hashed.digest().encode("base64").rstrip('\n')
        

    # This module verifies the value of the hash against the original message
    def Verify (self, hash_input, hash_key, hash_data):
        
        hashed = BitCommit (hash_input, hash_key)
        print "calculated Hash :"
        print hashed
        if (hash_data == hashed):
            return True
        else: 
            return False

    def decrpyt_amount(self, mess):
        encrypted = self.pub_key.encrypt(int(mess), None) #blinding factor = "hello1"**e
        t = str(encrypted[0])
        return t