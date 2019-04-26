from BitVector import *

import sys
sys.path.append('./service')
sys.path.append('./utils')

from MerchantMOHelper import MerchantMOHelper
import random
import Crypto
from Crypto.PublicKey import RSA
import hmac
from DigitalCashService import DigitalCashServer

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

def getStubForChannel(ip_address):
    with grpc.insecure_channel(ip_address) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            return None
        else:
            print("Connected")

        stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
        response = stub.ping(digitalCashService_pb2.pingMessage(message="Trying to ping you!!"))
        return stub

def run_server(bank_ip_address, customer_ip_address, merchant_port):

    bankStub = getStubForChannel(bank_ip_address)
    if(bankStub is None):
        print("Bank server is not available!!")
        return
    customerStub = getStubForChannel(customer_ip_address)
    if(customerStub is None):
        print("Customer server is not available!!")
        return

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    merchantMOHelper = MerchantMOHelper(pub_key)
    digitalCashServer = DigitalCashServer(merchantMOHelper, bankStub, customerStub)

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
    run_server('localhost:3000', '4000')