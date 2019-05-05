import sys
sys.path.append('../')
import digitalCashService_pb2_grpc
import digitalCashService_pb2
from BitVector import *
import random
import Crypto
import time
from Crypto.PublicKey import RSA
import grpc

class DigitalCashServer(digitalCashService_pb2_grpc.digitalCashServiceServicer):

    def __init__(self, merchantMOHelper, bank_address, customer_address):
        self.merchantMOHelper = merchantMOHelper
        self.bank_address = bank_address
        self.customer_address = customer_address

    def sendToBankFromCustomer(self, request, context):
        message = request.messageData
        numberOfMoneyOrders = request.numberOfMoneyOrders

        if (not message):
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
        return digitalCashService_pb2.ack(success = True, message = "Successfully Pinged!!")

    def sendToMerchantFromCustomer(self, request, context):
        data = request.messageData
        d = data.split(",")
        hash_op = d[0]
        key = d[1]
        
        SendStr = self.merchantMOHelper.RandomSelector()
        
        with grpc.insecure_channel(self.customer_address) as channel:
            try:
                grpc.channel_ready_future(channel).result(timeout=1)
            except grpc.FutureTimeoutError:
                print("Connection timeout. Unable to connect to port ", self.customer_address)
                return None

            stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
            response = stub.sendToCustomerFromMerchant(digitalCashService_pb2.Message(messageData=SendStr))
            message = response.messageData

            mess = message.split(',')
            hash_ip = self.merchantMOHelper.decrpyt_amount(mess[0])

            verify = self.merchantMOHelper.Verify (hash_ip, key, hash_op)

            message = "MO_deposit-*-*- " + message

            if verify == True: 
                with grpc.insecure_channel(self.bank_address) as channel:
                    try:
                        grpc.channel_ready_future(channel).result(timeout=1)
                    except grpc.FutureTimeoutError:
                        print("Connection timeout. Unable to connect to port ", self.bank_address)
                        return None

                    bankStub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
                    
                    responseFromBank = bankStub.sendToBankFromMerchant(digitalCashService_pb2.Message(messageData=message))
                    
                    if(responseFromBank.messageData=="credit_merchant"):
                        print("***INFORMATION*** :: Your account has been successfully credited!!")
                        return digitalCashService_pb2.ack(success = True, message="Successfully credited the Merchant.")
                    else:
                        print("***CRITICAL WARNING*** :: MO is already used, fraudulent transaction has been detected!!")
                        return digitalCashService_pb2.ack(success = False, message="Fraud has been detected")

        return digitalCashService_pb2.ack(success = False, message="Fraud has been detected")

