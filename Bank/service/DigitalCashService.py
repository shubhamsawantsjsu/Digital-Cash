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

        return digitalCashService_pb2.Message(messageData="", numberOfMoneyOrders=-1)

    def ping(self, request, context):
        return digitalCashService_pb2.ack(success = True, message = "Successfully Pinged!!")

