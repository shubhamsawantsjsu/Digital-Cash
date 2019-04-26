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

    def __init__(self, merchantMOHelper, bankStub, customerStub):
        self.merchantMOHelper = merchantMOHelper
        self.bankStub = bankStub
        self.customerStub = customerStub

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

    def sendToMerchantFromCustomer(self, request, context):
        data = request.messageData
        d = data.split(",")
        hash_op = d[0]
        key = d[1] #hash output and key recieved
        print data
        SendStr = self.merchantMOHelper.RandomSelector()
        print SendStr
        
        response = self.customerStub.sendToCustomerFromMerchant(digitalCashService_pb2.Message(messageData=SendStr))
        message = response.messageData

        mess = message.split(',')
        hash_ip = self.merchantMOHelper.decrpyt_amount(mess[0])

        print hash_ip
        verify = self.merchantMOHelper.Verify (hash_ip, key, hash_op)

        print ("Verification Status: " + str (verify))

        message = "MO_deposit-*-*- "+message
        if verify == True: 
            responseFromBank = self.bankStub.sendToBankFromMerchant(digitalCashService_pb2.Message(messageData=message))
            print ("Received from Bank: " + str (responseFromBank.messageData))
            return digitalCashService_pb2.Message(success = True, messageData="Successfully credited the Merchant.")

        return digitalCashService_pb2.Message(success = False, messageData="Fraud has been detected")

