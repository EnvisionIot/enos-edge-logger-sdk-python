from edgelogger.core.EdgeAPI import *
from edgelogger.core.internal.ZmqSubDataAPI import ZmqSubDataAPI
import socket

class EdgeSubscribeAPI(EdgeAPI):
    """This class is used to communicate with logger via ZeroMQ.
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

        super().__init__(edge_logger_ip=edge_logger_ip)
        zmq_address = "tcp://" + edge_logger_ip + ":5556"
        log.logger.debug("use the zmq address:%s" % zmq_address)
        self.zmq_api = ZmqSubDataAPI(zmq_address)
        self.zmq_channel_prefix = "DATASVC.SUB.DPF_"

    def RegisterRequiredPoints(self, devices_points: Dict[str, str], app_name: str = "domainPointDefaulChannel") -> int:
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

        if self.zmq_api.started == True:
            log.logger.warn("the Zmq API has already started")
            self.zmq_api.StopSubscribe()

        self.zmq_api.StartSubscribe(self.zmq_channel_prefix + app_name)

        status = self.redis_api.RegisterRequiredPoints(devices_points, self.zmq_channel_prefix + app_name)
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

        status = self.redis_api.UnRegisterSubscribeChannelName(self.zmq_channel_prefix + self.app_name)
        if status is None:
            raise EdgeLoggerRedisException(RET_REDIS_ERROR.get_error_message(), RET_REDIS_ERROR.get_error_code())

        if status == -1:
            return 1

        self.app_name = ""

        return status

    def SubcribeModelsValue(self) -> List[ModelValue]:
        """Use ZeroMQ to subscribe Edge Logger Data
        :return: List[ModelValue]
        """
        ret = self.zmq_api.SubcribeModelsValue()
        if ret is None:
            raise EdgeLoggerRedisException(RET_ZMQ_DATA_ERROR.get_error_message(), RET_ZMQ_DATA_ERROR.get_error_code())
        if ret == -1:
            log.logger.error("app is not registered, please use RegisterRequiredPoints to register first")
            raise EdgeLoggerException(RET_APP_NAME_IS_NOT_REGISTER.get_error_message(), RET_APP_NAME_IS_NOT_REGISTER.get_error_code())
        return ret
