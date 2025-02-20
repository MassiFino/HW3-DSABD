# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x04\x65\x63ho\"!\n\x10LoginUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\"I\n\x0eLoginUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x15\n\rsession_token\x18\x03 \x01(\t\"Z\n\x13RegisterUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x11\n\tmax_value\x18\x03 \x01(\x02\x12\x11\n\tmin_value\x18\x04 \x01(\x02\"L\n\x11RegisterUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x15\n\rsession_token\x18\x03 \x01(\t\"N\n\x16\x41\x64\x64TickerUtenteRequest\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\x11\n\tmax_value\x18\x02 \x01(\x02\x12\x11\n\tmin_value\x18\x03 \x01(\x02\"8\n\x14\x41\x64\x64TickerUtenteReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x18\n\x16ShowTickersUserRequest\"H\n\x14ShowTickersUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06ticker\x18\x03 \x01(\t\")\n\x17\x44\x65leteTickerUserRequest\x12\x0e\n\x06ticker\x18\x01 \x01(\t\"9\n\x15\x44\x65leteTickerUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"]\n\x11UpdateUserRequest\x12\x12\n\nticker_old\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x11\n\tmax_value\x18\x03 \x01(\x02\x12\x11\n\tmin_value\x18\x04 \x01(\x02\"3\n\x0fUpdateUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"P\n\x18UpdateMinMaxValueRequest\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\x11\n\tmax_value\x18\x02 \x01(\x02\x12\x11\n\tmin_value\x18\x03 \x01(\x02\"J\n\x16UpdateMinMaxValueReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06ticker\x18\x03 \x01(\t\"\x13\n\x11\x44\x65leteUserRequest\"3\n\x0f\x44\x65leteUserReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"\'\n\x15GetLatestValueRequest\x12\x0e\n\x06ticker\x18\x01 \x01(\t\"o\n\x13GetLatestValueReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06ticker\x18\x03 \x01(\t\x12\x13\n\x0bstock_value\x18\x04 \x01(\x01\x12\x11\n\ttimestamp\x18\x05 \x01(\t\"<\n\x16GetAverageValueRequest\x12\x0e\n\x06ticker\x18\x01 \x01(\t\x12\x12\n\nnum_values\x18\x02 \x01(\x05\"x\n\x14GetAverageValueReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x1b\n\x13\x61verage_stock_value\x18\x03 \x01(\x01\x12\x11\n\ttimestamp\x18\x04 \x01(\t\x12\x0e\n\x06ticker\x18\x05 \x01(\t2\xf0\x05\n\x0b\x45\x63hoService\x12;\n\tLoginUser\x12\x16.echo.LoginUserRequest\x1a\x14.echo.LoginUserReply\"\x00\x12\x44\n\x0cRegisterUser\x12\x19.echo.RegisterUserRequest\x1a\x17.echo.RegisterUserReply\"\x00\x12M\n\x0f\x41\x64\x64TickerUtente\x12\x1c.echo.AddTickerUtenteRequest\x1a\x1a.echo.AddTickerUtenteReply\"\x00\x12M\n\x0fShowTickersUser\x12\x1c.echo.ShowTickersUserRequest\x1a\x1a.echo.ShowTickersUserReply\"\x00\x12P\n\x10\x44\x65leteTickerUser\x12\x1d.echo.DeleteTickerUserRequest\x1a\x1b.echo.DeleteTickerUserReply\"\x00\x12>\n\nUpdateUser\x12\x17.echo.UpdateUserRequest\x1a\x15.echo.UpdateUserReply\"\x00\x12>\n\nDeleteUser\x12\x17.echo.DeleteUserRequest\x1a\x15.echo.DeleteUserReply\"\x00\x12J\n\x0eGetLatestValue\x12\x1b.echo.GetLatestValueRequest\x1a\x19.echo.GetLatestValueReply\"\x00\x12M\n\x0fGetAverageValue\x12\x1c.echo.GetAverageValueRequest\x1a\x1a.echo.GetAverageValueReply\"\x00\x12S\n\x11UpdateMinMaxValue\x12\x1e.echo.UpdateMinMaxValueRequest\x1a\x1c.echo.UpdateMinMaxValueReply\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_LOGINUSERREQUEST']._serialized_start=23
  _globals['_LOGINUSERREQUEST']._serialized_end=56
  _globals['_LOGINUSERREPLY']._serialized_start=58
  _globals['_LOGINUSERREPLY']._serialized_end=131
  _globals['_REGISTERUSERREQUEST']._serialized_start=133
  _globals['_REGISTERUSERREQUEST']._serialized_end=223
  _globals['_REGISTERUSERREPLY']._serialized_start=225
  _globals['_REGISTERUSERREPLY']._serialized_end=301
  _globals['_ADDTICKERUTENTEREQUEST']._serialized_start=303
  _globals['_ADDTICKERUTENTEREQUEST']._serialized_end=381
  _globals['_ADDTICKERUTENTEREPLY']._serialized_start=383
  _globals['_ADDTICKERUTENTEREPLY']._serialized_end=439
  _globals['_SHOWTICKERSUSERREQUEST']._serialized_start=441
  _globals['_SHOWTICKERSUSERREQUEST']._serialized_end=465
  _globals['_SHOWTICKERSUSERREPLY']._serialized_start=467
  _globals['_SHOWTICKERSUSERREPLY']._serialized_end=539
  _globals['_DELETETICKERUSERREQUEST']._serialized_start=541
  _globals['_DELETETICKERUSERREQUEST']._serialized_end=582
  _globals['_DELETETICKERUSERREPLY']._serialized_start=584
  _globals['_DELETETICKERUSERREPLY']._serialized_end=641
  _globals['_UPDATEUSERREQUEST']._serialized_start=643
  _globals['_UPDATEUSERREQUEST']._serialized_end=736
  _globals['_UPDATEUSERREPLY']._serialized_start=738
  _globals['_UPDATEUSERREPLY']._serialized_end=789
  _globals['_UPDATEMINMAXVALUEREQUEST']._serialized_start=791
  _globals['_UPDATEMINMAXVALUEREQUEST']._serialized_end=871
  _globals['_UPDATEMINMAXVALUEREPLY']._serialized_start=873
  _globals['_UPDATEMINMAXVALUEREPLY']._serialized_end=947
  _globals['_DELETEUSERREQUEST']._serialized_start=949
  _globals['_DELETEUSERREQUEST']._serialized_end=968
  _globals['_DELETEUSERREPLY']._serialized_start=970
  _globals['_DELETEUSERREPLY']._serialized_end=1021
  _globals['_GETLATESTVALUEREQUEST']._serialized_start=1023
  _globals['_GETLATESTVALUEREQUEST']._serialized_end=1062
  _globals['_GETLATESTVALUEREPLY']._serialized_start=1064
  _globals['_GETLATESTVALUEREPLY']._serialized_end=1175
  _globals['_GETAVERAGEVALUEREQUEST']._serialized_start=1177
  _globals['_GETAVERAGEVALUEREQUEST']._serialized_end=1237
  _globals['_GETAVERAGEVALUEREPLY']._serialized_start=1239
  _globals['_GETAVERAGEVALUEREPLY']._serialized_end=1359
  _globals['_ECHOSERVICE']._serialized_start=1362
  _globals['_ECHOSERVICE']._serialized_end=2114
# @@protoc_insertion_point(module_scope)
