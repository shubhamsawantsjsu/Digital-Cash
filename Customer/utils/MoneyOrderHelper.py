from BitVector import *
import sys
sys.path.append('./service')
sys.path.append('./utils')
import random
import Crypto
from Crypto.PublicKey import RSA
import grpc
import hmac
import hashlib

class MoneyOrderHelper():

    def __init__(self, numberOfMoneyOrders, numberOfSecretPairs, publicKey):
        self.numberOfMoneyOrders = numberOfMoneyOrders
        self.pub_key = publicKey
        self.numberOfSecretPairs = numberOfSecretPairs
        self.identityMsg_len = 440
        self.amount_and_uniqueStringMsg_len = 160

    def createMoneyOrder(self, customerAccountNumber, customerName, customerEmailId, moneyOrderAmount):
        customerAccountNumber = self.EnforceLength(customerAccountNumber, 5)
        customerName = self.EnforceLength(customerName, 20)
        customerEmailId = self.EnforceLength(customerEmailId,30)

        moneyOrderAmount = str(moneyOrderAmount)

        if len(moneyOrderAmount) > 5 :
            print ("Money order amount should be less than $99999")
            return 0
        else :
            moneyOrderAmount = self.EnforceLength(moneyOrderAmount,5)

        #convert each element into bit strings
        customer_Account_Number_BitVector = BitVector(textstring = customerAccountNumber)
        customer_Name_BitVector = BitVector(textstring= customerName)
        customer_Email_Address_BitVector  = BitVector(textstring = customerEmailId)

        identity = customer_Account_Number_BitVector + customer_Name_BitVector + customer_Email_Address_BitVector
        
        msg = BitVector(textstring = moneyOrderAmount)
        Msg = []

        #add unique string to each make unique message strings
        for i in range(0, self.numberOfMoneyOrders):
            UniqueByte = random.getrandbits(120) 
            uv = BitVector( intVal = UniqueByte, size = 120)
            Msg.append(msg + uv)

        return Msg, identity

    def EnforceLength(self, STRING, n):
        t = len(STRING)
        if t < n :
            for i in range(0, n-t):
                STRING = '0' + STRING
        if t > n :
            STRING = STRING[:n]
        return STRING


    # 1. Finds secret splitting pairs for I
    # 2. Blinds msg and secret pairs
    # 3. Concatenates blinded msg and secret pairs of I as a string of comma separated ints to form Blinded Message
    # 4. Returns the Blinded message and inverse of blinding factor(int)
    def BlindMessages(self, msg , I):
        
        #Find the secret splitting pairs for each of the 
        N1,N2 = self.secret_splitting(I)
        
        #randomly generate blinding factors
        r = random.getrandbits(512) 
        #t = str(r)
        #find bitVector of blinding factor and its inverse
        b_factor = BitVector(intVal = r)
        b_inverse = b_factor.multiplicative_inverse(BitVector(intVal = self.pub_key.n)) #b_factor*b_inverse = 1; 

        #encrypt the blinding factor with Bank's public key
        encrypted = self.pub_key.encrypt(b_factor.int_val(), None) #blinding factor = "hello1"**e
        b_factor_pow_e = encrypted[0] #Blind_int = b_factor**e

        B_msg = (b_factor_pow_e * msg.int_val())% self.pub_key.n #B_msg = message * b_factor**e
        #B_msg = B_msg  # B_msg = message * (b_factor**e) % n ; Now msg is blinded
        
        B_N1 = []
        B_N2 = []
        for i in range(0, len(N1)):
            B_N1.append((b_factor_pow_e * N1[i].int_val())% self.pub_key.n)
            B_N2.append((b_factor_pow_e * N2[i].int_val()) % self.pub_key.n)
        
        Message = str(B_msg)
        for i in range(0, len(B_N1)):
            Message += ","+str(B_N1[i])+","+str(B_N2[i])

        return Message,b_inverse.int_val() #sends a string and integer

    def secret_splitting(self, I):
        N1 = []
        N2 = []
        for i in range(0, self.numberOfSecretPairs):
            n1 = random.getrandbits(self.identityMsg_len) #returns an random int with I_n bits
            N11 = BitVector(intVal = n1, size = self.identityMsg_len)
            N21 = I^N11 # ^ is XOR operation
            N1.append(N11)
            N2.append(BitVector(intVal = N21.int_val(),size = self.identityMsg_len))
    
        return N1,N2 #returns N1 and N2 as [] of BitVectors

    def get_b_inverses(self, b, t):
        #b_ = b.split(",")
        b_inverse ="b-inverse-*-*-"
        for i in range(0, self.numberOfMoneyOrders):
            if i != t:
                b_inverse += " "+str(i)+"," +str(b[i])
            else: print(i)
        return b_inverse

    def Multiply_inverse(self, Msg, b, amount): # Msg - string, b - integer
        vals = Msg.split(' ')
        t = self.EnforceLength(str(amount), 5)
        M_signed = t + '-*-*-' 
        l = [int(v) for v in vals]
        for i in range(0,len(l)):
            m = (l[i]*b) % self.pub_key.n
            M_signed += ' ' +str(m)
        return M_signed 

    def decrpyt_amount(self, mess):
        encrypted = self.pub_key.encrypt(int(mess), None) #blinding factor = "hello1"**e
        t = str(encrypted[0])
        return t

    def BitCommit (self, message, key):
        hashed = hmac.new(key, message, hashlib.sha1)
        # The signature
        return hashed.digest().encode("base64").rstrip('\n')

    def generate_signature(self, key, data):
        #key = 'key'
        key_bytes= bytes(key , 'latin-1')
        data_bytes = bytes(data, 'latin-1')
        return hmac.new(key_bytes, data_bytes , hashlib.sha256).hexdigest()
