from concurrent import futures

import grpc
import sys
import time
import os
import digitalCashService_pb2_grpc
import digitalCashService_pb2

def run_client(serverAddress):
    with grpc.insecure_channel(serverAddress) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
        except grpc.FutureTimeoutError:
            print("Connection timeout. Unable to connect to port ")
            #exit()
        else:
            print("Connected")

        stub = digitalCashService_pb2_grpc.digitalCashServiceStub(channel)
        
        response = stub.ping(digitalCashService_pb2.pingMessage(message="Trying to ping you!!"))

        print(response.message)


if __name__ == '__main__':
    run_client('localhost:3000')