import sys
sys.path.append('../')
import digitalCashService_pb2_grpc
import digitalCashService_pb2

class DigitalCashServer(digitalCashService_pb2_grpc.digitalCashServiceServicer):

    def sendToBankFromCustomer(self, request, context):
        message = request.messageData

        # do some calculations

        return digitalCashService_pb2.ack(success=False, message="File does not exist in the cluster.")


