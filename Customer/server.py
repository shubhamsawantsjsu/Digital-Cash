from random import randrange, random
from fractions import gcd
import grpc
import random
import hashlib
import pickle
from Crypto.PublicKey import RSA
import sys
sys.path.append('./Service')
sys.path.append('./utils')
from MoneyOrderHelper import MoneyOrderHelper

from DigitalCashService import DigitalCashServer
import ssl

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
numberOfMoneyOrders = 5

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

def handleUserInputs():

    print("===================================")
    print("1. Make a money order.")
    print("2. Send a money order to the merchant.")
    print("===================================")
    option = input("Please choose an option.")

    if(option=='1'):
        makeMoneyOrder()
    elif(option=='2'):
        sendMoneyOrderToMerchant()

def makeMoneyOrder():
    customerAccountNumber = input("Please enter your account number.")
    customerName = input("Please enter your name")
    customerEmailId = input("Please enter your email address")

    moneyOrderAmount = input("Please enter the amount to create the Money Order")

    moneyOrderHelper = MoneyOrderHelper(numberOfMoneyOrders, pub_key)
    message, Identity = moneyOrderHelper.createMoneyOrder(customerAccountNumber, customerName, customerEmailId, moneyOrderAmount)

    m = [None] * numberOfMoneyOrders
    b = [None] * numberOfMoneyOrders

    for i in range(0, numberOfMoneyOrders):
        m[i],b[i] = moneyOrderHelper.BlindMessages(Msg[i], Identity)

    Message = "MO_request-*-*-" 
    for i in range(0, numberOfMoneyOrders):
        Message +=" "+m[i]

def run_server(customer_ip_address, bank_ip_address):

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add FileService to the server.
    digitalCashService_pb2_grpc.add_digitalCashServiceServicer_to_server(DigitalCashServer(), server)

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

    handleUserInputs()
    
    # Start the server
    run_server(customer_ip_address, bank_ip_address)