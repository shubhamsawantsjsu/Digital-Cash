import sys
sys.path.append('../')
import digitalCashService_pb2_grpc
import digitalCashService_pb2

class DigitalCashServer(digitalCashService_pb2_grpc.digitalCashServiceServicer):

    def send(self, request, context):
        


