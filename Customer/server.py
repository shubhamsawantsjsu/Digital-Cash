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
import os

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
numberOfMoneyOrders = 5
numberOfSecretPairs = 4

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

def handleUserInputs(merchant_ip_address, bankStub, digitalCashServer):

    print("===================================")
    print("1. Make a money order.")
    print("2. Send a money order to the merchant.")
    print("===================================")
    option = input("Please choose an option.")

    if(option=='1'):
        makeMoneyOrder(bankStub)
    elif(option=='2'):
        sendMoneyOrderToMerchant(merchant_ip_address, bankStub, digitalCashServer)

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

    responseMessage = stub.sendToBankFromCustomer(digitalCashService_pb2.Message(messageData=Message, numberOfMoneyOrders=numberOfMoneyOrders))
    
    print("Printing the response:", responseMessage.messageData)

    result = responseMessage.messageData
    k = result.split('-*-*- ')
    print(k[0])

    ind = int(k[1])
    b_inverse = moneyOrderHelper.get_b_inverses(b,int(k[1]))
    print(b_inverse)

    #send blinding factors of the asked MO numbers to bank
    responseMessage = stub.sendToBankFromCustomer(digitalCashService_pb2.Message(messageData=b_inverse, numberOfMoneyOrders=numberOfMoneyOrders, MOString=Message))
    #recieve signed MO from bank

    MO = responseMessage.messageData
    req = MO.split("-*-*- ")
    print(req[0])
    
    if MO != "Denied":
        MO_signed = moneyOrderHelper.Multiply_inverse(req[1],b[ind],moneyOrderAmount)
        with open('Unused_MO.txt', 'a') as fh:
            fh.write(MO_signed)
            fh.write("\n")
    else: 
      print("MO request rejected!")

def sendMoneyOrderToMerchant(merchant_ip_address, stub, digitalCashServer):

    with open('Unused_MO.txt', 'r') as fh:
        line = fh.readlines()

    if not line: 
        print("No MOs to send, please select Mode = 1 next")
        return
    
    Request = line[0]
    line = line[1:]
    
    with open('Unused_MO.txt', 'w') as fh:
        for l in line: fh.write(l)
    
    with open('Used_MO.txt', 'a') as fh:
        fh.write(Request)
        fh.write("\n")
    
    d = Request.split(" ")

    digitalCashServer.MO_Pairs_data = d

    moneyOrderHelper = MoneyOrderHelper(numberOfMoneyOrders, numberOfSecretPairs, pub_key)

    Message = moneyOrderHelper.decrpyt_amount(d[1]) 

    key = random.randint(0,1234)
    #key = "\x00"+os.urandom(4)+"\x00"

    key = str(key)
    #print (BitVector(intVal = int(Message), size = 1024).get_bitvector_in_ascii())
    
    hash_val = moneyOrderHelper.generate_signature(key, Message)  #BitCommit (Message, key)
    Hash_and_key = hash_val + ',' + key

    with grpc.insecure_channel(merchant_ip_address) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            return None
        else:
            print("Connected")

        stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
        response = stub.sendToMerchantFromCustomer(digitalCashService_pb2.Message(messageData=Hash_and_key))
    
    
    # print(Hash_and_key)
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.sendto(Hash_and_key,merch_addr)
    # ii,add = s.recvfrom(BUFFER_SIZE)
    # print(ii)
    # p = response.messageData.split(",")
    # Msg_pairs = d[1] + "," + d[2+int(p[0])]+ "," + d[2+int(p[1])]+ "," + d[2+int(p[2])]+ "," + d[2+int(p[3])]#bad hard code on number of secret pairs, got to change
    # s.sendto(Msg_pairs,merch_addr)
    # op, add = s.recvfrom(BUFFER_SIZE)
    # print(op)
    # s.close()

def run_server(bank_ip_address, merchant_ip_address, customer_port):

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    digitalCashServer = DigitalCashServer()
    # # Add FileService to the server.
    digitalCashService_pb2_grpc.add_digitalCashServiceServicer_to_server(digitalCashServer, server)

    # # Start the server on server_port.
    server.add_insecure_port('[::]:{}'.format(customer_port))
    server.start()

    print("------- Customer server has been started on port {} -------".format(customer_port))

    with grpc.insecure_channel(bank_ip_address) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            #exit()
        else:
            print("Connected")

        stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
        response = stub.ping(digitalCashService_pb2.pingMessage(message="Trying to ping you!!"))
        handleUserInputs(merchant_ip_address, stub, digitalCashServer)

    # Keep the server running for '_ONE_DAY_IN_SECONDS' seconds.
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


# ----------------------Main Method-------------------- #
if __name__ == '__main__':
    
    # Start the server
    run_server('localhost:3000', 'localhost:5000', '4000')