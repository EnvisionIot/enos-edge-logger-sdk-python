# coding=utf-8
import redis
import json
import time
from edgelogger.core.exception.EdgeLoggerError import *
from edgelogger.core.exception.EdgeLoggerException import EdgeLoggerException
from edgelogger.core.log.logger import log
from edgelogger.core.constant.Constant import *
from edgelogger.core.protobuf.point_pb2 import DevicePoint, DevicePoints
from edgelogger.core.internal.EdgeDataType import *
from typing import Dict, List, Tuple


class ControlMapping(object):
    def __init__(self, mapping_json_str: str) -> None:
        self.mapping_json_str = mapping_json_str
        self.valueType = ""
        self.pointNo = ""
        self.predefinedValue = ""
        self.valueMapping = {}
        self.argCount = 0
        self.mappingType = 0  # 0:control_set, 1:replace, 2:enum, 3:BITS_M_TO_N
        self.formulaBitsMToNParam = ControlCmdFormulaBitsMToN()  # Only used when mappingType=3

    def Parse(self):
        try:
            mapping_json = json.loads(self.mapping_json_str)
        except Exception as e:
            log.logger.warning("failed to decode json str:" + self.mapping_json_str)
            return None

        if "featureValueType" in mapping_json:
            if isinstance(mapping_json["featureValueType"], str):
                featureValueType = mapping_json["featureValueType"]
                log.logger.debug("featureValueType=%s, (%s)" % (featureValueType, self.mapping_json_str))
                if featureValueType == "TEXT" or featureValueType == "STRING":
                    self.valueType = "STRING"
                elif featureValueType == "INT" or featureValueType == "FLOAT" or featureValueType == "DOUBLE":
                    self.valueType = "DOUBLE"
                elif featureValueType == "ARRAY":
                    self.valueType = "ARRAY"
                else:
                    log.logger.error("featureValueType(%s) is err" % featureValueType)
                    return -1

        if "arguments" in mapping_json:
            args = mapping_json["arguments"]
            arg_size = len(args)

            if arg_size == 1:
                if isinstance(args[0], str):
                    self.pointNo = args[0]
                    self.argCount = 1
                else:
                    log.logger.error("the arguments is not valid(%s)" % args[0])
                    return -1
            elif arg_size == 2:
                if isinstance(args[0], str) and isinstance(args[1], str):
                    self.pointNo = args[0]
                    self.predefinedValue = args[1]
                    self.argCount = 2
                elif isinstance(args[0], str):
                    self.pointNo = args[0]
                    self.argCount = 1
                else:
                    return -1
            else:
                log.logger.error("the arguments size is not valid(%d)" % arg_size)
                return -1
        else:
            log.logger.error("control mapping(%s) str does not contain arguments" % self.mapping_json_str)
            return -1

        if "mappingFxStr" in mapping_json:
            mappingFx = mapping_json["mappingFxStr"]
            log.logger.debug("mappingFx=%s" % mappingFx)
            if not isinstance(mappingFx, str):
                log.logger.error("mappingFxStr(%s) is not valid" % mappingFx)
                return -1

            if mappingFx == "CONTROL_REPLACE_N" or mappingFx == "CONTROL_ENUM_N":
                if "operands" in mapping_json and isinstance(mapping_json["operands"], list):
                    oper = mapping_json["operands"]
                    oper_size = len(oper)
                    for i in range(oper_size//2):
                        self.valueMapping[oper[i]] = oper[oper_size//2 + i]

                if mappingFx == "CONTROL_REPLACE_N":
                    self.mappingType = 1
                else:
                    self.mappingType = 2
            elif mappingFx == "CONTROL_BITS_M_TO_N":
                if "operands" in mapping_json and isinstance(mapping_json["operands"], list):
                    oper = mapping_json["operands"]
                    self.formulaBitsMToNParam.ParseOperands(oper)

                    if self.formulaBitsMToNParam.isValid() == False:
                        log.logger.error("mappingFxStr(%s) ParseOperands is not valid" % mappingFx)
                        return -1

                self.mappingType = 3
            else:
                log.logger.error("mappingFxStr(%s) is not valid" % mappingFx)
                return -1


        return 0

    def newValue(self, value):
        if value in self.valueMapping:
            return self.valueMapping[value]
        return value


class RedisDataAPI(object):
    def __init__(self, redis_server="127.0.0.1", redis_port=6379):
        redis_pool = redis.ConnectionPool(host=redis_server, port=redis_port, decode_responses=True)
        self.__redis_conn = redis.StrictRedis(connection_pool=redis_pool)
        # self.__redis_conn = redis.Redis(host=redis_server, port=redis_port, decode_responses=True)
        self.__ctrlPublishMethod = 0  # 0:redis, 1:zeroMQ

    def GetResourcePublishStatus(self):
        redis_key_resource = "local:c2app.resource.publish.finish.status"
        try:
            value = self.__redis_conn.get(redis_key_resource)
            if value == "true":
                return True
            return False
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def GetAllDeviceKey(self) -> List[str]:
        redis_key_assetid_to_devicekey = "conf:c2cw.assetid.devicekey"
        try:
            assetid_to_devicekey = self.__redis_conn.hgetall(redis_key_assetid_to_devicekey)
            devicekeys = []
            for key in assetid_to_devicekey:
                devicekeys.append(assetid_to_devicekey[key])

            return devicekeys
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def GetDeviceState(self, device_key: str) -> int:
        """ Get the device's status
        :return: 1:online, 2:offline, 3:not exist, 4:unknown status
        """
        redis_key_device_status = "collect:c2app.device.status"
        try:
            status = self.__redis_conn.hget(redis_key_device_status, device_key)
            if status is None:
                return 3

            if status == "1" or status == "2":
                return int(status)

            return 4
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def GetDeviceIdsByDeviceKey(self, device_key) -> List[str]:
        """ Get the device Ids via device key
        :return: device id list
        """
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        try:
            deviceid_2_devicekey = self.__redis_conn.hgetall(redis_key_deviceid_2_devicekey)
            ids = []
            for key in deviceid_2_devicekey:
                if deviceid_2_devicekey[key] == device_key:
                    ids.append(key)

            return ids
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def GetDeviceLinkState(self, device_key: str) -> int:
        """ Get the device's link status via device key
        :return: 1:online, 2:offline, 3:not exist, 4:unknown status, None:run redis cmd failed
        """
        device_ids = self.GetDeviceIdsByDeviceKey(device_key)
        if device_ids is None:
            return None
        if len(device_ids) <= 0:
            return 3

        log.logger.debug(device_ids)

        for id in device_ids:
            redis_key_deviceid_2_status = "collect:d2cw.device.status"
            try:
                status = self.__redis_conn.hget(redis_key_deviceid_2_status, id)
                log.logger.debug("id=%s, status=%s" % (id, status))
                if status == "1":
                    return 1
                elif status != "0":
                    return 4
            except redis.RedisError as e:
                log.logger.error("failed to run redis cmd(%s)" % e)
                return None

        return 2

    def RemoveSubscribeChannelName(self, channel_name):
        redis_key_subscribe_channel = "subscribe:dapp2c.channel.name"
        try:
            return self.__redis_conn.srem(redis_key_subscribe_channel, channel_name)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def AddSubscribeChannelName(self, channel_name):
        redis_key_subscribe_channel = "subscribe:dapp2c.channel.name"
        try:
            return self.__redis_conn.sadd(redis_key_subscribe_channel, channel_name)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def GetSubscribeDevicesByChannelName(self, channel_name):
        redis_key = "subscribe:dapp2c:" + channel_name
        try:
            return self.__redis_conn.smembers(redis_key)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def UnRegisterSubscribeChannelName(self, channel_name):
        status = self.RemoveSubscribeChannelName(channel_name)
        if status is None:
            return None

        devices = self.GetSubscribeDevicesByChannelName(channel_name)
        if devices is None:
            return None

        log.logger.debug("the devices in channel " + channel_name + ":")
        log.logger.debug(devices)
        if devices is None:
            return None

        redis_key_devices = "subscribe:dapp2c:" + channel_name
        try:
            self.__redis_conn.delete(redis_key_devices)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

        for dev_key in devices:
            redis_key_points = "subscribe:dapp2c:" + channel_name + "." + dev_key
            try:
                self.__redis_conn.delete(redis_key_points)
            except redis.RedisError as e:
                log.logger.error("failed to run redis cmd(%s)" % e)
                return None

        return 0

    def GetDeviceKeyByAssetId(self, assetId):
        redis_key = "conf:c2cw.assetid.devicekey"
        try:
            return self.__redis_conn.hget(redis_key, assetId)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

    def RegisterSubscribeChannelName(self, channel_name, devices_points, use_device_key=False):
        """Register subscribe channel
        :param channel_name: the app name
        :param device_points, dict,  assetid/device_key-->list of points
        :param use_device_key, False: devices_points's key is assetid, otherwise it is device_key, default is False

        :return: 0: is success, -1: some points' asset id is not exist, otherwise is failed
        """
        log.logger.debug("register subscribe channel_name " + channel_name)
        log.logger.debug(devices_points)

        ret = 0

        # add channel
        status = self.AddSubscribeChannelName(channel_name)
        if status is None:
            return None

        for device in devices_points:
            redis_key_devices = "subscribe:dapp2c:" + channel_name
            device_key = ""

            if use_device_key:
                device_key = device
            else:
                device_key = self.GetDeviceKeyByAssetId(device)
                if device_key is None:
                    log.logger.warning("failed to get the device key via asset id " + device)
                    ret = -1
                    continue

            log.logger.debug("device_key is: " + device_key)
            # add device_key
            try:
                self.__redis_conn.sadd(redis_key_devices, device_key)
            except redis.RedisError as e:
                log.logger.error("failed to run redis cmd(%s)" % e)
                return None

            # add points
            redis_key_point = "subscribe:dapp2c:" + channel_name + "." + device_key
            for point in devices_points[device]:
                try:
                    self.__redis_conn.sadd(redis_key_point, point)
                except redis.RedisError as e:
                    log.logger.error("failed to run redis cmd(%s)" % e)
                    return None

        return ret

    def RegisterRequiredPoints(self, devices_points: Dict[str, str], channel_name: str = "channel_app2c") -> int:
        status = self.UnRegisterSubscribeChannelName(channel_name)
        if status is None:
            return None

        return self.RegisterSubscribeChannelName(channel_name, devices_points, True)

    def __UnpackModelValue(self, message):
        try:
            json_msg = json.loads(message)
        except Exception as e:
            log.logger.warning("failed to decode json str:" + message)
            return None

        sub_data = ModelValue()

        if "domainName" in json_msg:
            if isinstance(json_msg["domainName"], str):
                sub_data.domainName = json_msg["domainName"]
            else:
                log.logger.error("the domain name's value is not str(%s)" % json_msg["domainName"])
                return None

        if "value" in json_msg:
            if isinstance(json_msg["value"], str):
                sub_data.domainValue = json_msg["value"]
            else:
                log.logger.error("the domain value's value is not str(%s)" % json_msg["value"])
                return None

        if "assetId" in json_msg:
            if isinstance(json_msg["assetId"], str):
                sub_data.assetId = json_msg["assetId"]
            else:
                log.logger.error("the domain assetId's value is not str(%s)" % json_msg["assetId"])
                return None

        if "deviceKey" in json_msg:
            if isinstance(json_msg["deviceKey"], str):
                sub_data.deviceKey = json_msg["deviceKey"]
            else:
                log.logger.error("the domain deviceKey's value is not str(%s)" % json_msg["deviceKey"])
                return None

        if "domainValueType" in json_msg:
            if isinstance(json_msg["domainValueType"], str):
                sub_data.domainValueType = json_msg["domainValueType"]
            else:
                log.logger.error("the domain domainValueType's value is not str(%s)" % json_msg["domainValueType"])
                return None

        if "timestamp" in json_msg:
            if isinstance(json_msg["timestamp"], int):
                sub_data.timeValue = json_msg["timestamp"]
            else:
                log.logger.error("the domain timestamp's value is not str(%s)" % json_msg["timestamp"])
                return None

        if "oemTime" in json_msg:
            if isinstance(json_msg["oemTime"], int):
                sub_data.oemTime = json_msg["oemTime"]
            else:
                log.logger.error("the domain oemTime's value is not str(%s)" % json_msg["oemTime"])
                return None

        if "quality" in json_msg:
            if isinstance(json_msg["quality"], int):
                sub_data.quality = json_msg["quality"]
            else:
                log.logger.error("the domain quality's value is not str(%s)" % json_msg["quality"])
                return None

        if "flagUsingOem" in json_msg:
            if isinstance(json_msg["flagUsingOem"], bool):
                sub_data.flagUsingOem = json_msg["flagUsingOem"]
            else:
                log.logger.error("the domain flagUsingOem's value is not str(%s)" % json_msg["flagUsingOem"])
                return None

        sub_data.print()

        return sub_data

    def GetAModelValue(self, device_key: str, domain_name: str, return_str: bool = True):
        redis_key_model_value = "subscribe:c2dapp:" + device_key + ":points.value"
        try:
            json_value = self.__redis_conn.hget(redis_key_model_value, domain_name)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

        if json_value is None:
            log.logger.warning("failed to get device (%s) domain (%s) value" % (device_key, domain_name))
            return -1
        log.logger.debug("device(%s) domain(%s) value is:%s" % (device_key, domain_name, json_value))

        sub_data = self.__UnpackModelValue(json_value)

        if return_str:
            return sub_data.domainValue if sub_data is not None else None

        return sub_data

    def GetAllModelValuesBydeviceKey(self, device_key: str) -> List[ModelValue]:
        redis_key_model_value = "subscribe:c2dapp:" + device_key + ":points.value"
        try:
            key_value = self.__redis_conn.hgetall(redis_key_model_value)
        except redis.RedisError as e:
            log.logger.error("failed to run redis cmd(%s)" % e)
            return None

        if key_value is None:
            return []

        all_model_value = []
        for key in key_value:
            log.logger.debug("domain " + key + "'s value is " + key_value[key])

            sub_data = self.__UnpackModelValue(key_value[key])
            if sub_data is not None:
                all_model_value.append(sub_data)

        return all_model_value

    def WriteModelValueToRedis(self, point_list: List[ModelSetValue]):
        """Write Model value to redis stream
        """
        if len(point_list) == 0:
            return 0

        points_pb = DevicePoints()
        timestamp = 0
        for point in point_list:
            point_pb = points_pb.points.add()
            point_pb.colletDeviceId = point.deviceKey
            point_pb.pointName = point.domainName
            point_pb.value = point.domainValue
            point_pb.type = 2  # 1:Int, 2:Double, 3:String
            point_pb.oemTime = point.oemTime
            point_pb.quality = point.quality
            point_pb.attributes = point.attribute
            timestamp = point.timeValue

        points_pb.timestamp = timestamp

        redis_key = "collect:app2c.points.value"
        serial_str = points_pb.SerializeToString()
        log.logger.debug(serial_str)

        redis_data = {"value": serial_str}
        try:
            self.__redis_conn.xadd(redis_key, redis_data)
            return 0
        except redis.RedisError as e:
            log.logger.error("cat a RedisError when writing to redis(%s)" % e)
            return None

    def SetModelValue(self, point_list: List[ModelSetValue]) -> int:
        """Set Model Value
        :param point_list: list of ModelSetValue, if the timeValue == 0, it will use current time
        """
        if point_list == 0:
            return 0

        ret = 0

        for point in point_list:
            if point.isValid() == False:
                ret = -1
                break

            if point.timeValue <= 0:
                point.timeValue = int(round(time.time() * 1000))

            # update the attribute
            point.UpdateAttribute()

        if ret == -1:
            return -1

        return self.WriteModelValueToRedis(point_list)

    def GetAttributeValue(self, device_key: str, attribute: str) ->str:
        redis_key = "conf:c2c.device.attri:" + device_key
        attr_value = ""
        try:
            attr_value = self.__redis_conn.hget(redis_key, attribute)
            if attr_value is None:
                log.logger.debug("the attribute(%s) in device(%s) does not exist" % (attribute, device_key))
                return -1
            return attr_value
        except redis.RedisError as e:
            log.logger.error("cat a RedisError when writing to redis(%s)" % e)
            return None

    def __JudgeMultipleMaps(self, device_key: str, domain_name: str) -> Tuple[bool, str, str]:
        device_ids = self.GetDeviceIdsByDeviceKey(device_key)
        redis_key = "conf:c2cw.deviceid.templateid"
        map_count = 0
        device_id_ret = ""
        ctrl_map_ret = ""

        for device_id in device_ids:
            try:
                template_id = self.__redis_conn.hget(redis_key, device_id)
                if template_id is None:
                    log.logger.error("failed to get template_id for device (deviceKey:%s, deviceId:%s)" % (device_key, device_id))
                    return (False, None, None)
            except redis.RedisError as e:
                log.logger.error("cat a RedisError when writing to redis(%s)" % e)
                return (False, None, None)

            redis_key_tempid_ctrlmap = "conf:c2cpa.template.ctrl:" + template_id
            try:
                ctrl_map = self.__redis_conn.hget(redis_key_tempid_ctrlmap, domain_name)
                if ctrl_map is not None:
                    map_count = map_count + 1
                    device_id_ret = device_id
                    ctrl_map_ret = ctrl_map
                    continue
            except redis.RedisError as e:
                log.logger.error("cat a RedisError when writing to redis(%s)" % e)
                return (False, None, None)

        if map_count != 1:
            log.logger.error("%s %s has multi ctrl mapping error, count:%d" % (device_key, domain_name, map_count))
            return (False, device_id_ret, ctrl_map_ret)

        return (True, device_id_ret, ctrl_map_ret)

    def __publishCtrlMsg(self, cmd_str: str, expire_second: int):
        log.logger.debug("send ctrl msg:%s" % cmd_str)
        # zeromq way
        if self.__ctrlPublishMethod == 1:
            return

        # redis
        redis_key_ctrl = "ctrl:cpa2d.cmd"
        try:
            self.__redis_conn.expire(redis_key_ctrl, expire_second)
        except redis.RedisError as e:
            log.logger.error("failed to set key(%s) expire to (%d) due to(%s)" % (redis_key_ctrl, expire_second, e))
            return None

        try:
            log.logger.debug("add cmd: key(%s), cmd:(%s)" % (redis_key_ctrl, cmd_str))
            self.__redis_conn.lpush(redis_key_ctrl, cmd_str)
        except redis.RedisError as e:
            log.logger.error("failed to lpush ctrl to key(%s) due to(%s)" % (redis_key_ctrl, e))
            return None

        return 0

    def SetAModelCmd(self, channel_name: str, device_key: str, domain_name: str, value: str, serial_id: str, type: str = "DOUBLE", check_response: bool = True, expire_second: int = 600) -> int:
        if len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device key is not valid")
            return -1
        ctrl_point = ControlPoint()
        ctrl_point.domainName = domain_name
        ctrl_point.value = value
        ctrl_point.type = type

        ctrl_cmd = ControlCmd()
        ctrl_cmd.serialId = serial_id
        ctrl_cmd.deviceKey = device_key
        # ctrl_cmd.assetId = asset_id
        ctrl_cmd.checkResponse = check_response
        ctrl_cmd.points = [ctrl_point]
        ctrl_cmd.setChannel(channel_name)

        return self.SetBatchModelsCmd(ctrl_cmd, expire_second)

    def SetBatchModelsCmd(self, control_cmd: ControlCmd, expire_second: int = 600) -> int:
        if len(control_cmd.points) == 0:
            log.logger.info("there is no point in this control command")
            return 0

        device_id = ""
        points_json = {}
        types_json = {}

        for point in control_cmd.points:
            point_value = point.value
            point_type = point.type
            point_domain_name = point.domainName

            only_one_map, device_id, ctrl_map_json = self.__JudgeMultipleMaps(control_cmd.deviceKey, point.domainName)
            log.logger.debug("dk=%s, point=%s, only_one_map=%s, device_id=%s, ctrl_map_json=%s" % (
                control_cmd.deviceKey, point.domainName, str(only_one_map), device_id, ctrl_map_json
            ))
            # redis error
            if only_one_map == False and device_id == None:
                return None

            # has more than one mapping
            if only_one_map == False and device_id != None:
                return -1

            # only one mapping
            ctrl_mapping = ControlMapping(ctrl_map_json)
            ret = ctrl_mapping.Parse()
            if ret != 0:
                log.logger.error("failed to parse control mapping(%s)" % ctrl_map_json)
                return -2

            # has control formula mapping
            log.logger.debug("ctrl_mapping.valueMapping's len=%d" % len(ctrl_mapping.valueMapping))
            if len(ctrl_mapping.valueMapping) > 0:
                log.logger.debug(ctrl_mapping.valueMapping)
                if ctrl_mapping.mappingType == 1:
                    point_value = ctrl_mapping.newValue(point.value)
                elif ctrl_mapping.mappingType == 2:
                    if point.value in ctrl_mapping.valueMapping:
                        point_value = ctrl_mapping.newValue(point.value)
                    else:
                        log.logger.error("value(%s) is not in Enum ctrl mapping" % point.value)
                        return -3
            if ctrl_mapping.mappingType == 3:
                result, value = self.__CalcFormulaValue(
                    control_cmd.deviceKey, point_value, ctrl_mapping.formulaBitsMToNParam)
                if result < 0:
                    log.logger.error("control formula calculation failed")
                    return result
                point_value = value
                ctrl_mapping.valueType = "DOUBLE"

            if ctrl_mapping.predefinedValue != "":
                point_value = ctrl_mapping.predefinedValue

            point_type = ctrl_mapping.valueType
            points_json[ctrl_mapping.pointNo] = point_value
            types_json[ctrl_mapping.pointNo] = point_type

        cmdJson = {}
        cmdJson["deviceid"] = device_id
        cmdJson["channel"] = control_cmd.getChannel()
        cmdJson["serialid"] = control_cmd.serialId
        cmdJson["checkResponse"] = control_cmd.checkResponse
        cmdJson["points"] = points_json
        cmdJson["types"] = types_json

        return self.__publishCtrlMsg(json.dumps(cmdJson), expire_second)

    def __CalcFormulaValue(self, device_key, value, param) -> Tuple[int, str]:

        t = time.time()

        try:
            model_value = self.GetAModelValue(
                device_key, param.relatedPoint, False)
            if model_value == -1:
                log.logger.error("failed to get model(%s) value in device(%s)" % (
                    param.relatedPoint, device_key))
                return (-4, "")
            if model_value is None:
                log.logger.error("failed to get model(%s) value(null) in device(%s)" % (
                    param.relatedPoint, device_key))
                return (-4, "")

            model_value.print()
            if int(model_value.timeValue) + param.relatedPointTimeout * 1000 < int(t) * 1000:
                log.logger.error("'CONTROL_BITS_M_TO_N' get deviceKey=%s,domain=%s value timeout,(nowtime=%d)" % (
                    device_key, param.relatedPoint, int(t)))
                return (-5, "")

            model_value.domainValue = model_value.domainValue.replace('"', '')
            log.logger.debug("relatedPointValue(%s),controlValueIn(%s),[%d,%d]" % (
                model_value.domainValue, value, param.lowBit, param.highBit))

            input_value = int((float)(value))
            base_value = int((float)(model_value.domainValue))
            high_bit = param.highBit
            low_bit = param.lowBit
        except Exception as e:
            log.logger.warning(
                "failed to get param's value form 'CONTROL_BITS_M_TO_N' :%s(%s)" % (value, e))
            return (-6, "")

        log.logger.debug("relatedPointValue(%d),controlValueIn(%d),[%d,%d]" % (
            base_value, input_value, param.lowBit, param.highBit))

        value_tmp = (input_value & (
            (2 << ((high_bit - low_bit + 1) - 1)) - 1)) << low_bit
        base_value_tmp = base_value & ~(
            ((2 << ((high_bit - low_bit + 1) - 1)) - 1) << low_bit)
        output = value_tmp | base_value_tmp

        log.logger.info("relatedPointValue(%d),controlValueIn(%d),[%d,%d],output=%d" % (
            base_value, input_value, low_bit, high_bit, output))

        return (0, output)




    def __ParseCmdResult(self, cmd_ret: str) -> ControlCmdResult:

        try:
            log.logger.debug("cmd result:%s" % cmd_ret)
            cmd_ret_json = json.loads(cmd_ret)
            ctrl_cmd_result = ControlCmdResult()

            if "serialid" in cmd_ret_json and isinstance(cmd_ret_json["serialid"], str):
                ctrl_cmd_result.serialId = cmd_ret_json["serialid"]
            if "status" in cmd_ret_json and isinstance(cmd_ret_json["status"], int):
                ctrl_cmd_result.status = cmd_ret_json["status"]
            if "desc" in cmd_ret_json and isinstance(cmd_ret_json["desc"], str):
                ctrl_cmd_result.dest = cmd_ret_json["desc"]

            log.logger.debug("cmd result: serial_id=%s, status=%d, desc=%s" %
                             (ctrl_cmd_result.serialId, ctrl_cmd_result.status, ctrl_cmd_result.desc))

            return ctrl_cmd_result
        except Exception as e:
            log.logger.warning("failed to decode json str:%s(%s)" % (cmd_ret, e))
            return None

    def GetAModelCmdResult(self, channel_name: str, expire_second: int = 600) -> ControlCmdResult:
        redis_key_ctrl = "ctrl:d2cap:" + channel_name + ":cmd.result"
        try:
            self.__redis_conn.expire(redis_key_ctrl, expire_second)
        except redis.RedisError as e:
            log.logger.error("failed to set key(%s) expire to (%d) due to(%s)" % (redis_key_ctrl, expire_second, e))
            return None

        try:
            cmd_ret = self.__redis_conn.rpop(redis_key_ctrl)
            if cmd_ret is None:
                return -1

            cmd_result = self.__ParseCmdResult(cmd_ret)
            if cmd_result is None:
                return -2

            return cmd_result
        except redis.RedisError as e:
            log.logger.error("failed to lpush ctrl to key(%s) due to(%s)" % (redis_key_ctrl, e))
            return None

    def GetAllCmdResult(self, channel_name: str, expire_second: int = 600) -> List[ControlCmdResult]:
        redis_key_ctrl = "ctrl:d2cap:" + channel_name + ":cmd.result"
        try:
            self.__redis_conn.expire(redis_key_ctrl, expire_second)
        except redis.RedisError as e:
            log.logger.error("failed to set key(%s) expire to (%d) due to(%s)" % (redis_key_ctrl, expire_second, e))
            return None

        try:
            count = self.__redis_conn.llen(redis_key_ctrl)
            if count == 0:
                return []

            cmd_ret_list = self.__redis_conn.lrange(redis_key_ctrl, -count, -1)
            self.__redis_conn.ltrim(redis_key_ctrl, 0, -count-1)

            ctrl_cmd_list = []
            for cmd_ret in cmd_ret_list:
                ctrl_cmd = self.__ParseCmdResult(cmd_ret)
                if ctrl_cmd is not None:
                    ctrl_cmd_list.append(ctrl_cmd)

            return ctrl_cmd_list
        except redis.RedisError as e:
            log.logger.error("failed to get ctrl from redis key(%s) due to(%s)" % (redis_key_ctrl, e))
            return None

    def SetAppConfig(self, app_name: str, key: str, value: str) -> int:
        redis_key_app = "conf:app2app:" + app_name + ":config"
        try:
            self.__redis_conn.hset(redis_key_app, key, value)
            return 0
        except redis.RedisError as e:
            log.logger.error("failed to hset to key(%s) due to(%s)" % (redis_key_app, e))
            return None

    def GetAppConfig(self, app_name: str, key: str) -> str:
        redis_key_app = "conf:app2app:" + app_name + ":config"
        try:
            value = self.__redis_conn.hget(redis_key_app, key)
            if value is None:
                return -1

            return value
        except redis.RedisError as e:
            log.logger.error("failed to hget from key(%s) due to(%s)" % (redis_key_app, e))
            return None

    def DeleteAppConfig(self, app_name: str, key: str) -> int:
        redis_key_app = "conf:app2app:" + app_name + ":config"
        try:
            count = self.__redis_conn.hdel(redis_key_app, key)
            if count == 1:
                return 0
            return -1
        except redis.RedisError as e:
            log.logger.error("failed to hget from key(%s) due to(%s)" % (redis_key_app, e))
            return None

    def DeleteAppAllConfig(self, app_name) ->int:
        redis_key_app = "conf:app2app:" + app_name + ":config"
        try:
            count = self.__redis_conn.delete(redis_key_app)
            return count
        except redis.RedisError as e:
            log.logger.error("failed to hget from key(%s) due to(%s)" % (redis_key_app, e))
            return None

if __name__ == "__main__":
    def test_SetModelValue():
        point_list = []
        for i in range(4):
            point = ModelSetValue()
            point.domainName = "Temp"
            point.deviceKey = "deviceKey00" + str(i)
            point.assetId = "assetId00" + str(i)
            point.domainValue = str(i)

            point.oemTime = 0
            point.flagUsingOem = False
            point.timeValue = 0

            point_list.append(point)

        api = RedisDataAPI()
        api.SetModelValue(point_list)

    device_key = "deviceKey001"
    channel_name = "xfc_test"
    app_name = channel_name
    asset_id = "assetId_001"
    devices_points = {"deviceKey001": ["Temp", "Sensor"]}
    domain_name = "Temp"

    api = RedisDataAPI()
    api.GetResourcePublishStatus()
    api.GetAllDeviceInfo()
    api.GetDeviceState(device_key)
    api.GetDeviceIdsByDeviceKey(device_key)
    api.GetDeviceLinkState(device_key)
    api.RemoveSubscribeChannelName(channel_name)
    api.AddSubscribeChannelName(channel_name)
    api.GetSubscribeDevicesByChannelName(channel_name)
    api.UnRegisterSubscribeChannelName(channel_name)
    api.GetDeviceKeyByAssetId(asset_id)
    api.RegisterSubscribeChannelName(channel_name, devices_points, True)
    api.RegisterRequiredPoints(devices_points, app_name)
    api.GetAModelValue(device_key, domain_name)
    api.GetAllModelValuesBydeviceKey(device_key)
    test_SetModelValue()
