# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import service_pb2 as service__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in service_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class EchoServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.LoginUser = channel.unary_unary(
                '/echo.EchoService/LoginUser',
                request_serializer=service__pb2.LoginUserRequest.SerializeToString,
                response_deserializer=service__pb2.LoginUserReply.FromString,
                _registered_method=True)
        self.RegisterUser = channel.unary_unary(
                '/echo.EchoService/RegisterUser',
                request_serializer=service__pb2.RegisterUserRequest.SerializeToString,
                response_deserializer=service__pb2.RegisterUserReply.FromString,
                _registered_method=True)
        self.AddTickerUtente = channel.unary_unary(
                '/echo.EchoService/AddTickerUtente',
                request_serializer=service__pb2.AddTickerUtenteRequest.SerializeToString,
                response_deserializer=service__pb2.AddTickerUtenteReply.FromString,
                _registered_method=True)
        self.ShowTickersUser = channel.unary_unary(
                '/echo.EchoService/ShowTickersUser',
                request_serializer=service__pb2.ShowTickersUserRequest.SerializeToString,
                response_deserializer=service__pb2.ShowTickersUserReply.FromString,
                _registered_method=True)
        self.DeleteTickerUser = channel.unary_unary(
                '/echo.EchoService/DeleteTickerUser',
                request_serializer=service__pb2.DeleteTickerUserRequest.SerializeToString,
                response_deserializer=service__pb2.DeleteTickerUserReply.FromString,
                _registered_method=True)
        self.UpdateUser = channel.unary_unary(
                '/echo.EchoService/UpdateUser',
                request_serializer=service__pb2.UpdateUserRequest.SerializeToString,
                response_deserializer=service__pb2.UpdateUserReply.FromString,
                _registered_method=True)
        self.DeleteUser = channel.unary_unary(
                '/echo.EchoService/DeleteUser',
                request_serializer=service__pb2.DeleteUserRequest.SerializeToString,
                response_deserializer=service__pb2.DeleteUserReply.FromString,
                _registered_method=True)
        self.GetLatestValue = channel.unary_unary(
                '/echo.EchoService/GetLatestValue',
                request_serializer=service__pb2.GetLatestValueRequest.SerializeToString,
                response_deserializer=service__pb2.GetLatestValueReply.FromString,
                _registered_method=True)
        self.GetAverageValue = channel.unary_unary(
                '/echo.EchoService/GetAverageValue',
                request_serializer=service__pb2.GetAverageValueRequest.SerializeToString,
                response_deserializer=service__pb2.GetAverageValueReply.FromString,
                _registered_method=True)
        self.UpdateMinMaxValue = channel.unary_unary(
                '/echo.EchoService/UpdateMinMaxValue',
                request_serializer=service__pb2.UpdateMinMaxValueRequest.SerializeToString,
                response_deserializer=service__pb2.UpdateMinMaxValueReply.FromString,
                _registered_method=True)


class EchoServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def LoginUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddTickerUtente(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ShowTickersUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteTickerUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetLatestValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAverageValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateMinMaxValue(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EchoServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'LoginUser': grpc.unary_unary_rpc_method_handler(
                    servicer.LoginUser,
                    request_deserializer=service__pb2.LoginUserRequest.FromString,
                    response_serializer=service__pb2.LoginUserReply.SerializeToString,
            ),
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=service__pb2.RegisterUserRequest.FromString,
                    response_serializer=service__pb2.RegisterUserReply.SerializeToString,
            ),
            'AddTickerUtente': grpc.unary_unary_rpc_method_handler(
                    servicer.AddTickerUtente,
                    request_deserializer=service__pb2.AddTickerUtenteRequest.FromString,
                    response_serializer=service__pb2.AddTickerUtenteReply.SerializeToString,
            ),
            'ShowTickersUser': grpc.unary_unary_rpc_method_handler(
                    servicer.ShowTickersUser,
                    request_deserializer=service__pb2.ShowTickersUserRequest.FromString,
                    response_serializer=service__pb2.ShowTickersUserReply.SerializeToString,
            ),
            'DeleteTickerUser': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteTickerUser,
                    request_deserializer=service__pb2.DeleteTickerUserRequest.FromString,
                    response_serializer=service__pb2.DeleteTickerUserReply.SerializeToString,
            ),
            'UpdateUser': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateUser,
                    request_deserializer=service__pb2.UpdateUserRequest.FromString,
                    response_serializer=service__pb2.UpdateUserReply.SerializeToString,
            ),
            'DeleteUser': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteUser,
                    request_deserializer=service__pb2.DeleteUserRequest.FromString,
                    response_serializer=service__pb2.DeleteUserReply.SerializeToString,
            ),
            'GetLatestValue': grpc.unary_unary_rpc_method_handler(
                    servicer.GetLatestValue,
                    request_deserializer=service__pb2.GetLatestValueRequest.FromString,
                    response_serializer=service__pb2.GetLatestValueReply.SerializeToString,
            ),
            'GetAverageValue': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAverageValue,
                    request_deserializer=service__pb2.GetAverageValueRequest.FromString,
                    response_serializer=service__pb2.GetAverageValueReply.SerializeToString,
            ),
            'UpdateMinMaxValue': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateMinMaxValue,
                    request_deserializer=service__pb2.UpdateMinMaxValueRequest.FromString,
                    response_serializer=service__pb2.UpdateMinMaxValueReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'echo.EchoService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('echo.EchoService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class EchoService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def LoginUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/LoginUser',
            service__pb2.LoginUserRequest.SerializeToString,
            service__pb2.LoginUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RegisterUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/RegisterUser',
            service__pb2.RegisterUserRequest.SerializeToString,
            service__pb2.RegisterUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AddTickerUtente(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/AddTickerUtente',
            service__pb2.AddTickerUtenteRequest.SerializeToString,
            service__pb2.AddTickerUtenteReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ShowTickersUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/ShowTickersUser',
            service__pb2.ShowTickersUserRequest.SerializeToString,
            service__pb2.ShowTickersUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteTickerUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/DeleteTickerUser',
            service__pb2.DeleteTickerUserRequest.SerializeToString,
            service__pb2.DeleteTickerUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/UpdateUser',
            service__pb2.UpdateUserRequest.SerializeToString,
            service__pb2.UpdateUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/DeleteUser',
            service__pb2.DeleteUserRequest.SerializeToString,
            service__pb2.DeleteUserReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetLatestValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/GetLatestValue',
            service__pb2.GetLatestValueRequest.SerializeToString,
            service__pb2.GetLatestValueReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetAverageValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/GetAverageValue',
            service__pb2.GetAverageValueRequest.SerializeToString,
            service__pb2.GetAverageValueReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateMinMaxValue(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/echo.EchoService/UpdateMinMaxValue',
            service__pb2.UpdateMinMaxValueRequest.SerializeToString,
            service__pb2.UpdateMinMaxValueReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)