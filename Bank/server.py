from concurrent import futures

from random import randrange, random
from fractions import gcd
import grpc
import time
import random
import hashlib
import pickle
import Crypto
from Crypto.PublicKey import RSA
import digitalCashService_pb2_grpc
import digitalCashService_pb2
import sys
sys.path.append('./service')
sys.path.append('./utils')

from DigitalCashService import DigitalCashServer
import ssl

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

with open('publicKeyRsa.pub', 'r') as pub_file:
    pub_key = RSA.importKey(pub_file.read())

with open('privateKeyRsa.pvt', 'r') as pvt_file:
    pvt_key = RSA.importKey(pvt_file.read())

def run_server(bank_host_name, bank_port):

    # Declare the gRPC server with 10 max_workers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add FileService to the server.
    digitalCashService_pb2_grpc.add_digitalCashServiceServicer_to_server(DigitalCashServer(pub_key, pvt_key), server)

    # Start the server on server_port.
    server.add_insecure_port('[::]:{}'.format(bank_port))
    server.start()
    print("------- Bank server has been started on port {} -------".format(bank_port))

    # Keep the server running for '_ONE_DAY_IN_SECONDS' seconds.
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


# ----------------------Main Method-------------------- #
if __name__ == '__main__':
    
    bank_host_name = "localhost"
    bank_port = "3000"
    
    # Start the server
    run_server(bank_host_name, bank_port)