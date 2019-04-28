import sys
sys.path.append('../')
import digitalCashService_pb2_grpc
import digitalCashService_pb2
from BitVector import *
import random
import Crypto
import time
from Crypto.PublicKey import RSA

class DigitalCashServer(digitalCashService_pb2_grpc.digitalCashServiceServicer):

    def __init__(self):
        self.MO_Pairs_data = None

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
            return digitalCashService_pb2.Message(messageData=msg, numberOfMoneyOrders=numberOfMoneyOrders)

        return digitalCashService_pb2.Message(messageData="", numberOfMoneyOrders=-1)

    def ping(self, request, context):
        print(request.message)
        return digitalCashService_pb2.ack(success = True, message = "Successfully Pinged!!")
        
    def sendToCustomerFromMerchant(self, request, context):
        d = self.MO_Pairs_data
        bitList = request.messageData
        p = bitList.split(",")
        message_pairs = d[1] + "," + d[2+int(p[0])]+ "," + d[2+int(p[1])]+ "," + d[2+int(p[2])]+ "," + d[2+int(p[3])]
        return digitalCashService_pb2.Message(messageData=message_pairs)

    def sendToMerchantFromCustomer(self, request, context):
        return digitalCashService_pb2.Message(success = False, messageData="Fraud has been detected")



