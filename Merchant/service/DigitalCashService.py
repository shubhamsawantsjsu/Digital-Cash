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
        print("Successfully pinged!!!!!")
        return digitalCashService_pb2.ack(success = True, message = "Successfully Pinged!!")

    def sendToMerchantFromCustomer(self, request, context):
        print("----------------------Inside sendToMerchantFromCustomer-----------------")
        data = request.messageData
        d = data.split(",")
        hash_op = d[0]
        key = d[1] #hash output and key recieved
        print(data)
        SendStr = self.merchantMOHelper.RandomSelector()
        print(SendStr)
        
        with grpc.insecure_channel(self.customer_address) as channel:
            try:
                grpc.channel_ready_future(channel).result(timeout=1)
            except grpc.FutureTimeoutError:
                print("Connection timeout. Unable to connect to port ")
                return None
            else:
                print("Connected")

            stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
            response = stub.sendToCustomerFromMerchant(digitalCashService_pb2.Message(messageData=SendStr))
            message = response.messageData

            mess = message.split(',')
            hash_ip = self.merchantMOHelper.decrpyt_amount(mess[0])

            print(hash_ip)
            verify = self.merchantMOHelper.Verify (hash_ip, key, hash_op)

            print("Verification Status: " + str (verify))

            message = "MO_deposit-*-*- " + message
            if verify == True: 
                with grpc.insecure_channel(self.bank_address) as channel:
                    try:
                        grpc.channel_ready_future(channel).result(timeout=1)
                    except grpc.FutureTimeoutError:
                        print("Connection timeout. Unable to connect to port ")
                        return None
                    else:
                        print("Connected")

                    bankStub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
                    
                    print("Sending the message to bank----------------------------------")
                    responseFromBank = bankStub.sendToBankFromMerchant(digitalCashService_pb2.Message(messageData=message))
                    
                    print ("Received from Bank: " + responseFromBank.messageData)

                    if(responseFromBank.messageData=="credit_merchant"):
                        return digitalCashService_pb2.ack(success = True, messageData="Successfully credited the Merchant.")
                    else:
                        return digitalCashService_pb2.ack(success = False, messageData="Fraud has been detected")

        return digitalCashService_pb2.Message(success = False, messageData="Fraud has been detected")

