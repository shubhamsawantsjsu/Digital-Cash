from concurrent import futures
from BitVector import *

import sys
sys.path.append('./service')
sys.path.append('./utils')

import digitalCashService_pb2_grpc
import digitalCashService_pb2
from MerchantMOHelper import MerchantMOHelper
import random
import Crypto
from Crypto.PublicKey import RSA
import hmac
import grpc
from DigitalCashService import DigitalCashServer
import time

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

def run_server(bank_ip_address, customer_ip_address, merchant_port):

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    merchantMOHelper = MerchantMOHelper(pub_key)
    digitalCashServer = DigitalCashServer(merchantMOHelper, bank_ip_address, customer_ip_address)

    # # Add FileService to the server.
    digitalCashService_pb2_grpc.add_digitalCashServiceServicer_to_server(digitalCashServer, server)

    # # Start the server on server_port.
    server.add_insecure_port('[::]:{}'.format(merchant_port))
    server.start()

    print("------- Merchant server has been started on port {} -------".format(merchant_port))

    # Keep the server running for '_ONE_DAY_IN_SECONDS' seconds.
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

# ----------------------Main Method-------------------- #
if __name__ == '__main__':
    
    # Start the server
    run_server('localhost:3000', 'localhost:4000', '5000')