import sys
sys.path.append('../')
import digitalCashService_pb2_grpc
import digitalCashService_pb2
from BitVector import *
import sys
import random
import Crypto
import time
from Crypto.PublicKey import RSA

class DigitalCashServer(digitalCashService_pb2_grpc.digitalCashServiceServicer):

    def __init__(self, pub_key, pvt_key):
        self.pub_key = pub_key
        self.pvt_key = pvt_key

    def sendToBankFromCustomer(self, request, context):
        print("----------------------Inside sendToBankFromCustomer--------------")
        message = request.messageData
        numberOfMoneyOrders = request.numberOfMoneyOrders

        if (not message):
            print("Message is empty!!")
            return digitalCashService_pb2.Message(messageData="", numberOfMoneyOrders=-1)
        
        req = message.split('-*-*- ')

        print("Request is : ", req[0])

        if(req[0]=="MoneyOrder_Request"):
            MO = req[1]
            t = random.randint(0, numberOfMoneyOrders-1)
            msg ="Except-*-*- "+ str(t)
            print(msg)
            return digitalCashService_pb2.Message(messageData=msg, numberOfMoneyOrders=numberOfMoneyOrders)

        if(req[0] == "b-inverse"):
            b_inv = req[1]
            MOString = request.MOString.split('-*-*- ')
            msg = self.process_MO(MOString[1], b_inv, 0)
            M = msg.split("-*-*- ")
            print(M[0])
            return digitalCashService_pb2.Message(messageData=msg, numberOfMoneyOrders=numberOfMoneyOrders)

        return digitalCashService_pb2.Message(messageData="", numberOfMoneyOrders=-1)

    def ping(self, request, context):
        print(request.message)
        return digitalCashService_pb2.ack(success = True, message = "Successfully Pinged!!")

    def sendToBankFromMerchant(self, request, context):
        print("----------------------Inside sendToBankFromCustomer--------------")
        message = request.messageData

        if (not message):
            print("Message is empty!!")
            return digitalCashService_pb2.Message(messageData="")
        
        req = message.split('-*-*- ')

        print("Request is : ", req[0])

        #1. req[1] has the (amt+unique string) + (one of the four pairs)
        #2. decrypt the first message and check for unique string in DB
        #3. if unique string not present already, credit amount, else reply not credited

        #### TO DO:
        val = False#search_UniqueString(req[1])

        if val == False:
            msg = "credit_merchant"
            return digitalCashService_pb2.Message(messageData=msg)

        else:
            msg = "MO already used"
            return digitalCashService_pb2.Message(messageData=msg)

    def process_MO(self, MO1, b_inv, T):
        MO_ = MO1.split(" ")
        b = b_inv.split(" ")
        amt = 0
        V = True
        M_ = ''
        for i in range(0, len(b)):
            b_i = b[i].split(",")
            print("The blinding factor")
            #print b_i
            M, I = self.UnblindMessage(MO_[int(b_i[0])], int(b_i[1]))
            V = self.verify_secrets(I)
            if V == False: 
                return "Denied"
            if amt == 0:
                try:
                    amt = int(M[:5])
                except:
                    print("\n")
        
        if V == True:       
            # with open("customerAcc.txt", 'r') as fl:
            #     line = fl.readlines()
            # t = len(line)
            # bal = int(line[t-1])
            # print( bal)
            # print(amt)
            # print(type(amt))
            # if bal < amt:
            #     return "Denied"
            
            # else : 
            #     bal = bal - amt
            #     print(bal)
            #     with open("customerAcc.txt", 'a') as fl:
            #         fl.write(str(bal))
            #         fl.write("\n")

            #Msg = self.Sign(MO_[T],amt)
            Msg = self.Sign(MO_[T],1000)
            return Msg

    def UnblindMessage(self, Msg, b): #Msg - string, b - integer
        '''
        1. Splits Msg into msg + 4*secret pairs
        2. Unblinds each of the entities
        3. Returns msg and 4*Identites as calculated from the 4*secret pairs as strings
        '''

        vals = Msg.split(',')
        M_b = self.pvt_key.decrypt(int(vals[0])) #M_be = B_Msg**d,  where B_msg = M*(b_factor**e)%n ; Note ** = pow; Thus M_b = (M**d)*b_factor
        M_s = (M_b*b) % self.pub_key.n# M_signed = Msg**d as b_factor*b_inverse = 1; as b is b_inverse here
        e = self.pub_key.encrypt(M_s,None) #msg**(d*e); since d*e = 1, e = msg
        E = BitVector(intVal = e[0], size = 160)
        
        M = E.get_bitvector_in_ascii()
        I = []
        for i in range(1,len(vals),2):
            
            N1_b = self.pvt_key.decrypt(int(vals[i]))
            N1_s = (N1_b*b) % self.pub_key.n
            e = self.pub_key.encrypt(N1_s,None) #msg**(d*e); since d*e = 1, e = msg
            N1 = BitVector(intVal = e[0], size = 1024)

            N2_b = self.pvt_key.decrypt(int(vals[i+1]))
            N2_s = (N2_b*b) % self.pub_key.n
            e = self.pub_key.encrypt(N2_s,None) #msg**(d*e); since d*e = 1, e = msg
            N2 = BitVector(intVal = e[0], size = 1024)
            t = N1^N2
            I.append(t.get_bitvector_in_ascii())
        print("Identity string, after secret pair combination") 
        for i in I : print(i)
        print("MO: " +M) 
        return M, I #returns msg and I[] as strings

    def verify_secrets(self, I):#To make sure that all the Identity strings are the same - to avoid fraud
        Verify = True
        prev = I[0]
        for i in range(1,len(I)):
            if prev != I[i]: 
                Verify = False
                print(i)
                break
        return Verify

    def Sign(self, Msg, amt):
        msg = str(amt)+'-*-*-'
        vals = Msg.split(',')
        for i in range(0,len(vals)):
            M_b = self.pvt_key.decrypt(int(vals[i]))
            msg += " "+str(M_b)
        return msg

    def search_UniqueString(Msg):
        import codecs
        M = Msg.split(",")
        e = self.pub_key.encrypt(int(M[0]),None)
        msg = BitVector(intVal = e[0], size = 160)
        MO_string = msg.get_bitvector_in_ascii()
        amt = int(MO_string[:5])
        
        print("Amount is ", amt)
        
        Unique_str = MO_string[5:]
        #Unique_str = t.encode('utf-8')
        print(Unique_str)
        
        for l in Unique_str:
            if l == MO_string: 
                return True

        bal = 0

        with open("merchantAcc.txt",'r') as fl:
            line = fl.readlines()
        t = len(line)
        with open("merchantAcc.txt",'a') as fl:
            if (not line): 
                bal = 0
            else : 
                bal = int(line[t-1])
            Amt = bal + amt
            fl.write(str(Amt))
            fl.write('\n')
        
        #U_str.append(MO_string)
        return False
