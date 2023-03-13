from edgelogger.core.internal.RedisDataAPI import RedisDataAPI
from edgelogger.core.internal.EdgeDataType import *
from edgelogger.core.exception.EdgeLoggerError import *
from edgelogger.core.exception.EdgeLoggerException import EdgeLoggerException, EdgeLoggerRedisException
from edgelogger.core.log.logger import log
from edgelogger.core.constant.Constant import *
from typing import Dict, List
import socket


class EdgeAPI(object):
    """This class is used to communicate with logger via Redis.
    """

    def __init__(self, edge_logger_ip: str = "127.0.0.1"):
        """init the EdgeAPI
        :param edge_logger_ip: the IP of the Edge Logger box, default is 127.0.0.1
        """
        try:
            socket.inet_aton(edge_logger_ip)
        except socket.error:
            log.logger.error("edge_logger_ip's value is not valid")
            raise EdgeLoggerException("edge_logger_ip's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        redis_server = edge_logger_ip
        redis_port = 6379
        self.redis_api = RedisDataAPI(redis_server, redis_port)
        self.app_name = ""
        self.ctrl_channel_prefix = "api_prefix_"

    def GetAllDeviceKey(self) -> List[str]:
        """ Get all devices' key
        :return: the list of all devices' key
        """
        resource_status = self.redis_api.GetResourcePublishStatus()
        if resource_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if resource_status is False:
            log.logger.warn("resource is not ready")
            return []

        all_deivce_info = self.redis_api.GetAllDeviceKey()
        if all_deivce_info is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        return all_deivce_info

    def GetDeviceState(self, device_key: str) -> int:
        """ Get the device's login EnOS Cloud state via device key
        :return: -1:resource not ready, 1:online, 2:offline, 3:not exist, 4:unknown status
        """
        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        resource_status = self.redis_api.GetResourcePublishStatus()
        if resource_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if resource_status is False:
            log.logger.warn("resource is not ready")
            return -1

        device_status = self.redis_api.GetDeviceState(device_key)
        if device_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return device_status

    def GetDeviceLinkState(self, device_key: str) -> int:
        """ Get the device's link status via device key
        :return: -1:resource not ready, 1:online, 2:offline, 3:not exist, 4:unknown status
        """
        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        resource_status = self.redis_api.GetResourcePublishStatus()
        if resource_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if resource_status is False:
            log.logger.warn("resource is not ready")
            return -1

        link_status = self.redis_api.GetDeviceLinkState(device_key)
        if link_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        return link_status

    def RegisterRequiredPoints(self, devices_points: Dict[str, str], app_name: str = "channel_app2c") -> int:
        """Subscribe to the full set of required device point identifiers
        :param device_points, dict,  Contains device and point domainName identifier, device_key-->list of points
        :param app_name: The unique identifier of the application, used to distinguish different applications
        :return: 0: is success, -1: is failed
        """
        if isinstance(app_name, str) == False or app_name == "CLOUD" or len(app_name) == 0 or len(app_name) > 13 or app_name.find(":") >= 0:
            log.logger.error("the app_name " + app_name + " is not valid")
            raise EdgeLoggerException("app_name " + app_name + " is not valid", RET_APP_NAME_IS_NOT_VALID.get_error_code())

        if isinstance(devices_points, dict) == False:
            log.logger.error("the devices_points' value type is not valid")
            raise EdgeLoggerException("devices_points' value type is not valid", RET_APP_NAME_IS_NOT_VALID.get_error_code())

        #check whether the dict is valid or not
        for device_key in devices_points:
            if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
                log.logger.error("device_key's value(%s) is not valid" % device_key)
                raise EdgeLoggerException("device_key's value(%s) is not valid" % device_key, RET_PARAM_IS_INVALID.get_error_code())
            for domain_name in devices_points[device_key]:
                if isinstance(domain_name, str) == False or len(domain_name) == 0 or len(domain_name) > REDIS_MAX_KEY_LENGTH:
                    log.logger.error("domain_name's value(%s) is not valid" % domain_name)
                    raise EdgeLoggerException("domain_name's value(%s) is not valid" % domain_name, RET_PARAM_IS_INVALID.get_error_code())

        self.app_name = app_name

        status = self.redis_api.RegisterRequiredPoints(devices_points, app_name)
        if status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        return status

    def UnRegisterApp(self) -> int:
        """unregister app
        :return: 0: is success, 1: not exist
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        status = self.redis_api.UnRegisterSubscribeChannelName(self.app_name)
        if status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        if status == -1:
            return 1

        self.app_name = ""

        return status

    def GetAModelValue(self, device_key: str, domain_name: str, return_str: bool = True):
        """Get a point's value of a device, (the point should be registered by RegisterRequiredPoints)
        :param device_key: the device key in EnOS Cloud Model
        :param domain_name: the point's domain name in EnOS Cloud Model
        :param return_str: if return_str is True, this function will return the point's string value,
                           otherwise return ModelValue, default is True
        :return:  if return_str is True, return type is string/None, otherwise return type is ModelValue/None
        """
        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(domain_name, str) == False or len(domain_name) == 0 or len(domain_name) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("domain_name's value is not valid")
            raise EdgeLoggerException("domain_name's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(return_str, bool) == False:
            log.logger.error("return_str's value is not valid")
            raise EdgeLoggerException("return_str's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAModelValue(device_key, domain_name, return_str)
        # not exist
        if ret == -1:
            return None
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return ret

    def GetAllModelValuesBydeviceKey(self, device_key: str) -> List[ModelValue]:
        """Get all points value of a device, (the points should be registered by RegisterRequiredPoints)
        :param device_key: the device key in EnOS Cloud Model
        :return: the list of ModelValue
        """
        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAllModelValuesBydeviceKey(device_key)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return ret

    def SetModelsValue(self, point_list: List[ModelSetValue]) -> int:
        """Set Model Value
        :param point_list: list of ModelSetValue
         ModelSetValue: It's used to set the point's value by App.
            :deviceKey: the device key in EnOS Cloud Model
            :domainName: the point's domain name in EnOS Cloud Model
            :domainValue: the point's value
            :flagUsingOem: the flag of whether using OEM time, default is False
            :timeValue: the timestamp of this point's value, if the timeValue == 0, it will use current timestamp(ms)
            :oemTime: the oemTime value, default is 0
            :quality: the quality of this model point, default is 0
            :attribute: the attribute of this model, most case you donot need to set it,
                        if oemTime or quality or transferWay or flagUsingOem is not the default value(0/False), it will update attribute
            :transferWay: the way to send to cloud, 0:sent in real-time, 1:only change to sent, default is 0
        :return 0:success, -1:failed
        """
        if isinstance(point_list, list) == False:
            log.logger.error("point_list's value is not valid")
            raise EdgeLoggerException("point_list's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if len(point_list) == 0:
            return 0

        for point in point_list:
            if isinstance(point, ModelSetValue) == False:
                log.logger.error("the data type in the point_list is not ModelSetValue")
                raise EdgeLoggerException("data type in point_list is not valid", RET_PARAM_IS_INVALID.get_error_code())
            if point.isValid() == False:
                log.logger.error("the ModelSetValue data in the point_list is not valid")
                raise EdgeLoggerException("the ModelSetValue data in the point_list is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.SetModelValue(point_list)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return ret

    def GetAttributeValue(self, device_key: str, attribute: str) -> str:
        """Get the device's attribute's value
        :param device_key: the device key in EnOS Cloud Model
        :param attribute: the attribute of this device in EnOS Cloud Model
        :return: str or None if the attribute is not exist
        """

        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(attribute, str) == False or len(attribute) == 0 or len(attribute) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the attribute is not valid")
            raise EdgeLoggerException("attribute parameter is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAttributeValue(device_key, attribute)
        # not exist
        if ret == -1:
            return None
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return ret

    def SetAModelCmd(self, device_key: str, domain_name: str, value: str, serial_id: str, type: str = "DOUBLE", check_response: bool = True, expire_second: int = 600) -> int:
        """Set a point control command
        :param device_key: the device key in EnOS Cloud Model
        :param domain_name: the point's domain name in EnOS Cloud Model
        :param value: the point's value
        :param serial_id: this control unique serial id
        :param type: the value's type, default is DOUBLE(int/long/double), it can be INT or FLOAT or DOUBLE or STRING or ARRAY
        :param check_response: whether to check this control's response, default is true
        :param expire_second: when this control command will be expired, default is 600s
        :return: 0:success, -1:failed
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if isinstance(device_key, str) == False or len(device_key) == 0 or len(device_key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("device_key's value is not valid")
            raise EdgeLoggerException("device_key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(domain_name, str) == False or len(domain_name) == 0 or len(domain_name) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("domain_name's value is not valid")
            raise EdgeLoggerException("domain_name's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(value, str) == False or len(value) == 0 or len(value) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("value's value is not valid")
            raise EdgeLoggerException("value's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(serial_id, str) == False or len(serial_id) == 0 or len(serial_id) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("serial_id's value is not valid")
            raise EdgeLoggerException("serial_id's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(type, str) == False or (type != "INT" and type != "FLOAT" and type != "DOUBLE" and type != "STRING" and type != "ARRAY"):
            log.logger.error("type's value is not valid")
            raise EdgeLoggerException("type's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if not isinstance(check_response, bool):
            log.logger.error("check_response's value is not valid")
            raise EdgeLoggerException("check_response's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if not isinstance(expire_second, int):
            log.logger.error("expire_second's value is not valid")
            raise EdgeLoggerException("expire_second's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        resource_status = self.redis_api.GetResourcePublishStatus()
        if resource_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if resource_status is False:
            log.logger.warn("resource is not ready")
            return -1

        # add prefix in control channel
        channel = self.ctrl_channel_prefix + self.app_name
        ret = self.redis_api.SetAModelCmd(channel, device_key, domain_name, value, serial_id, type, check_response, expire_second)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if ret == -1:
            raise EdgeLoggerException("cannot find the control point mapping or the count of mapping more than one", RET_CONFIG_ERROR.get_error_code())
        if ret == -2:
            raise EdgeLoggerException("ctrl related config in resource package is not correct", RET_CONFIG_ERROR.get_error_code())
        if ret == -3:
            raise EdgeLoggerException("the control cmd value is not in the model enum list", RET_VALUE_IS_INVALID.get_error_code())
        if ret == -4:
            raise EdgeLoggerException("associated point not collected", RET_VALUE_IS_INVALID.get_error_code())
        if ret == -5:
            raise EdgeLoggerException("associated point collection timeout", RET_VALUE_IS_INVALID.get_error_code())
        if ret == -6:
            raise EdgeLoggerException("the control cmd value is invalid", RET_VALUE_IS_INVALID.get_error_code())


        return ret

    def SetModelsCmd(self, control_cmd: ControlCmd, expire_second: int = 600) -> int:
        """Set many points control command
        :param control_cmd: the ControlCmd type
        :param expire_second: when this control command will be expired, default is 600s
        :return: 0:success, -1:failed
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if isinstance(control_cmd, ControlCmd) == False:
            log.logger.error("control_cmd is not the type of ControlCmd")
            raise EdgeLoggerException("control_cmd is not the type of ControlCmd", RET_PARAM_IS_INVALID.get_error_code())

        if control_cmd.isValid() == False:
            log.logger.error("control_cmd is not valid")
            raise EdgeLoggerException("control_cmd is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if not isinstance(expire_second, int):
            log.logger.error("expire_second's value is not valid")
            raise EdgeLoggerException("expire_second's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        resource_status = self.redis_api.GetResourcePublishStatus()
        if resource_status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if resource_status is False:
            log.logger.warn("resource is not ready")
            return -1

        # add prefix in control channel
        control_cmd.setChannel(self.ctrl_channel_prefix + self.app_name)

        ret = self.redis_api.SetBatchModelsCmd(control_cmd, expire_second)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if ret == -1:
            raise EdgeLoggerException("cannot find the control point mapping or the count of mapping more than one", RET_CONFIG_ERROR.get_error_code())
        if ret == -2:
            raise EdgeLoggerException("ctrl related config in resource package is not correct", RET_CONFIG_ERROR.get_error_code())
        if ret == -3:
            raise EdgeLoggerException("the control cmd value is not in the model enum list", RET_VALUE_IS_INVALID.get_error_code())

        return ret

    def GetAModelCmdResult(self, expire_second: int = 600) -> ControlCmdResult:
        """Get a model control command result
        :return: ControlCmdResult
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if not isinstance(expire_second, int):
            log.logger.error("expire_second's value is not valid")
            raise EdgeLoggerException("expire_second's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAModelCmdResult(self.ctrl_channel_prefix + self.app_name, expire_second)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if ret == -2:
            raise EdgeLoggerException("the cmd result parsed failed", RET_VALUE_IS_INVALID.get_error_code())
        if ret == -1:
            return None

        return ret

    def GetAllCmdResult(self, expire_second: int = 600) -> List[ControlCmdResult]:
        """Get all model control command results
        :return: List[ControlCmdResult]
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if not isinstance(expire_second, int):
            log.logger.error("expire_second's value is not valid")
            raise EdgeLoggerException("expire_second's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAllCmdResult(self.ctrl_channel_prefix + self.app_name, expire_second)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return ret

    def SetAppConfig(self, key: str, value: str) -> int:
        """Set the App's config
        :param key: the config's key
        :param value: the config's value
        :return: 0: success
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if isinstance(key, str) == False or len(key) == 0 or len(key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("key's value is not valid")
            raise EdgeLoggerException("key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        if isinstance(value, str) == False or len(value) == 0 or len(value) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("value's value is not valid")
            raise EdgeLoggerException("value's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.SetAppConfig(self.app_name, key, value)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        return 0

    def GetAppConfig(self, key: str) -> str:
        """Get the App's config
        :param key: the config's key
        :return: 0: success, None:not exist
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if isinstance(key, str) == False or len(key) == 0 or len(key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("key's value is not valid")
            raise EdgeLoggerException("key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.GetAppConfig(self.app_name, key)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if ret == -1:
            return None

        return ret

    def DeleteAppConfig(self, key: str) -> int:
        """Delete the APP's config
        :param key: the config's key
        :return: 0: success, None:not exist
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        if isinstance(key, str) == False or len(key) == 0 or len(key) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("key's value is not valid")
            raise EdgeLoggerException("key's value is not valid", RET_PARAM_IS_INVALID.get_error_code())

        ret = self.redis_api.DeleteAppConfig(self.app_name, key)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())
        if ret == -1:
            return None

        return ret

    def DeleteAppAllConfig(self) -> int:
        """Delete this APP's all config
        :return: 0:success, None:not exist
        """
        if self.app_name == "":
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())

        ret = self.redis_api.DeleteAppAllConfig(self.app_name)
        if ret is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        if ret == 0:
            return None

        return 0
