class EdgeLoggerError(object):

    def __init__(self, error_code, error_message):
        self.__error_code = error_code
        self.__error_message = error_message

    def get_error_code(self):
        return self.__error_code

    def get_error_message(self):
        return self.__error_message


RET_SUCCESS = EdgeLoggerError(0, "success")
RET_APP_NAME_IS_NOT_VALID = EdgeLoggerError(-100, "app name is not valid")
RET_PARAM_IS_INVALID = EdgeLoggerError(-101, "parameter is not valid")
RET_REDIS_ERROR = EdgeLoggerError(-102, "Failed to communicate with Redis")
RET_APP_NAME_IS_NOT_REGISTER = EdgeLoggerError(-103, "app is not registered, please use RegisterRequiredPoints to register first")
RET_CONFIG_ERROR = EdgeLoggerError(-104, "the resource config is not correct")
RET_VALUE_IS_INVALID = EdgeLoggerError(-105, "the value is not valid")
RET_ZMQ_DATA_ERROR = EdgeLoggerError(-105, "the data in zmq is error")
