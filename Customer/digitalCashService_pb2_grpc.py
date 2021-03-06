# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import digitalCashService_pb2 as digitalCashService__pb2


class digitalCashServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.sendToBankFromCustomer = channel.unary_unary(
        '/digitalCashService/sendToBankFromCustomer',
        request_serializer=digitalCashService__pb2.Message.SerializeToString,
        response_deserializer=digitalCashService__pb2.Message.FromString,
        )
    self.sendToMerchantFromCustomer = channel.unary_unary(
        '/digitalCashService/sendToMerchantFromCustomer',
        request_serializer=digitalCashService__pb2.Message.SerializeToString,
        response_deserializer=digitalCashService__pb2.ack.FromString,
        )
    self.sendToBankFromMerchant = channel.unary_unary(
        '/digitalCashService/sendToBankFromMerchant',
        request_serializer=digitalCashService__pb2.Message.SerializeToString,
        response_deserializer=digitalCashService__pb2.Message.FromString,
        )
    self.sendToCustomerFromMerchant = channel.unary_unary(
        '/digitalCashService/sendToCustomerFromMerchant',
        request_serializer=digitalCashService__pb2.Message.SerializeToString,
        response_deserializer=digitalCashService__pb2.Message.FromString,
        )
    self.ping = channel.unary_unary(
        '/digitalCashService/ping',
        request_serializer=digitalCashService__pb2.pingMessage.SerializeToString,
        response_deserializer=digitalCashService__pb2.ack.FromString,
        )


class digitalCashServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def sendToBankFromCustomer(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def sendToMerchantFromCustomer(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def sendToBankFromMerchant(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def sendToCustomerFromMerchant(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ping(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_digitalCashServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'sendToBankFromCustomer': grpc.unary_unary_rpc_method_handler(
          servicer.sendToBankFromCustomer,
          request_deserializer=digitalCashService__pb2.Message.FromString,
          response_serializer=digitalCashService__pb2.Message.SerializeToString,
      ),
      'sendToMerchantFromCustomer': grpc.unary_unary_rpc_method_handler(
          servicer.sendToMerchantFromCustomer,
          request_deserializer=digitalCashService__pb2.Message.FromString,
          response_serializer=digitalCashService__pb2.ack.SerializeToString,
      ),
      'sendToBankFromMerchant': grpc.unary_unary_rpc_method_handler(
          servicer.sendToBankFromMerchant,
          request_deserializer=digitalCashService__pb2.Message.FromString,
          response_serializer=digitalCashService__pb2.Message.SerializeToString,
      ),
      'sendToCustomerFromMerchant': grpc.unary_unary_rpc_method_handler(
          servicer.sendToCustomerFromMerchant,
          request_deserializer=digitalCashService__pb2.Message.FromString,
          response_serializer=digitalCashService__pb2.Message.SerializeToString,
      ),
      'ping': grpc.unary_unary_rpc_method_handler(
          servicer.ping,
          request_deserializer=digitalCashService__pb2.pingMessage.FromString,
          response_serializer=digitalCashService__pb2.ack.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'digitalCashService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
