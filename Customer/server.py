from concurrent import futures

from random import randrange, random
from fractions import gcd
import grpc
import random
import hashlib
import pickle
import Crypto
import time
from Crypto.PublicKey import RSA
import digitalCashService_pb2_grpc
import digitalCashService_pb2
import sys
sys.path.append('./service')
sys.path.append('./utils')
from MoneyOrderHelper import MoneyOrderHelper

from DigitalCashService import DigitalCashServer
import ssl

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
numberOfMoneyOrders = 5
numberOfSecretPairs = 4

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

def handleUserInputs(stub):

    print("===================================")
    print("1. Make a money order.")
    print("2. Send a money order to the merchant.")
    print("===================================")
    option = input("Please choose an option.")

    if(option=='1'):
        makeMoneyOrder(stub)
    elif(option=='2'):
        sendMoneyOrderToMerchant()

def makeMoneyOrder(stub):
    customerAccountNumber = input("Please enter your 5 digit account number :: ")
    customerName = input("Please enter your name :: ")
    customerEmailId = input("Please enter your email address :: ")

    moneyOrderAmount = input("Please enter the amount to create the Money Order :: ")

    moneyOrderHelper = MoneyOrderHelper(numberOfMoneyOrders, numberOfSecretPairs, pub_key)
    message, Identity = moneyOrderHelper.createMoneyOrder(customerAccountNumber, customerName, customerEmailId, moneyOrderAmount)

    m = [None] * numberOfMoneyOrders
    b = [None] * numberOfMoneyOrders

    for i in range(0, numberOfMoneyOrders):
        m[i],b[i] = moneyOrderHelper.BlindMessages(message[i], Identity)

    Message = "MoneyOrder_Request-*-*-" 
    for i in range(0, numberOfMoneyOrders):
        Message +=" "+m[i]
    
    print("Came here and printing the message!!")

    print(stub)
    responseMessage = stub.sendToBankFromCustomer(digitalCashService_pb2.Message(messageData=Message, numberOfMoneyOrders=numberOfMoneyOrders))
    
    print("Printing the response:", responseMessage.messageData)

def run_server(customer_ip_address, bank_ip_address, customer_port, bank_port):

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add FileService to the server.
    digitalCashService_pb2_grpc.add_digitalCashServiceServicer_to_server(DigitalCashServer(), server)

    # Start the server on server_port.
    server.add_insecure_port('[::]:{}'.format(customer_port))
    server.start()

    with grpc.insecure_channel(bank_ip_address) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            exit()
        else:
            print("Connected")
    
    stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)

    response = stub.ping(digitalCashService_pb2.pingMessage(message="Want to ping you!!!"))

    print(response.message)

    handleUserInputs(stub)

    # Keep the server running for '_ONE_DAY_IN_SECONDS' seconds.
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


# ----------------------Main Method-------------------- #
if __name__ == '__main__':
    
    bank_ip_address = "localhost:3000"
    customer_ip_address = "localhost:4000"
    customer_port = "4000"
    bank_port = "3000"
    
    # Start the server
    run_server(customer_ip_address, bank_ip_address, customer_port, bank_port)