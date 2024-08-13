from edgelogger.core.log.logger import log
from edgelogger.core.constant.Constant import *
import json


class ModelValue(object):
    """A Point's value in EnOS Cloud Model
    :deviceKey: the device key in EnOS Cloud Model
    :assetId: the assetId of this device in EnOS Cloud Model
    :domainName: the point's domain name in EnOS Cloud Model
    :domainValue: the point's value
    :domainValueType: the type of this point's value, default is 'DOUBLE'
    :flagUsingOem: the flag of whether using OEM time, default is False
    :timeValue: the timestamp of this point's value
    :oemTime: the oemTime value
    :quality: the quality of this model point
    """

    def __init__(self) -> None:
        self.deviceKey = ""  # the device key of this model point
        self.assetId = ""  # the assetId of this device
        self.domainName = ""  # the name of this model point
        self.domainValue = ""  # the value of this model point

        self.domainValueType = "DOUBLE"  # 1.DOUBLE (It may be int/float/double.) | 2.STRING
        self.flagUsingOem = False  # the flag of whether using OEM time
        self.timeValue = 0  # the time value
        self.oemTime = 0  # OEM time
        self.quality = 0  # the quality of this model point

        # self.productKey = ""
        # self.rawValueType = 2  # 0:int, 1:float, 2:double, 3:array, 4:string
        # self.attribute = ""
    def print(self) -> None:
        log.logger.debug("""domainName:%s, deviceKey:%s, assetId:%s, domainValue:%s, domainValueType:%s, flagUsingOem:%s, timeValue:%d,"""
                         """ oemTime:%d, quality:%d""" % (self.domainName, self.deviceKey, self.assetId, self.domainValue, self.domainValueType,
                                                          "True" if self.flagUsingOem else "False", self.timeValue, self.oemTime, self.quality))


class ModelSetValue(object):
    """It's used to set the point's value by App.
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
    """

    def __init__(self) -> None:
        """ Only domainName, deviceKey, domainValue is MUST required, others are optional
        """
        self.deviceKey = ""
        self.domainName = ""
        self.domainValue = ""

        # optional
        self.flagUsingOem = False
        self.timeValue = 0
        self.oemTime = 0
        self.quality = 0

        self.attribute = '{"timestamp":0,"quality":0,"transferWay":0,"flagUsingOem":false}'
        self.transferWay = 0  # 0: sent in real-time, 1:only change to sent, default is 0

    def UpdateAttribute(self) -> None:
        if self.oemTime != 0 or self.quality != 0 or self.transferWay != 0 or self.flagUsingOem != False:
            attr = {"timestamp": self.oemTime, "quality": self.quality,
                    "transferWay": self.transferWay, "flagUsingOem": self.flagUsingOem}
            self.attribute = json.dumps(attr)

    def isValid(self) -> bool:
        if isinstance(self.domainName, str) == False or len(self.domainName) == 0 or len(self.domainName) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("domainName's value is not valid")
            return False

        if isinstance(self.deviceKey, str) == False or len(self.deviceKey) == 0 or len(self.deviceKey) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("deviceKey's value is not valid")
            return False

        if isinstance(self.domainValue, str) == False or len(self.domainValue) == 0 or len(self.domainValue) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("domainValue's value is not valid")
            return False

        if not isinstance(self.oemTime, int):
            log.logger.error("oemTime's value is not valid")
            return False

        if not isinstance(self.flagUsingOem, bool):
            log.logger.error("flagUsingOem's value is not valid")
            return False

        if not isinstance(self.timeValue, int):
            log.logger.error("timeValue's value is not valid")
            return False

        if not isinstance(self.quality, int):
            log.logger.error("quality's value is not valid")
            return False

        if isinstance(self.attribute, str) == False or len(self.attribute) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("attribute's value is not valid")
            return False

        if not isinstance(self.transferWay, int):
            log.logger.error("transferWay's value is not valid")
            return False

        return True


class ControlPoint(object):
    """One Model Point which can be controled.
    :domainName: the point's domain name in EnOS Cloud Model
    :value: the value you want to set
    :type: the domainName's value's type, default is 'DOUBLE', it can be INT or FLOAT or DOUBLE or STRING or ARRAY
    """

    def __init__(self) -> None:
        self.domainName = ""
        self.value = ""
        self.type = "DOUBLE"  # INT or FLOAT or DOUBLE or STRING or ARRAY

    def isValid(self) -> bool:
        if isinstance(self.domainName, str) == False or len(self.domainName) == 0 or len(self.domainName) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the ControlPoint's domainName is not valid")
            return False

        if isinstance(self.value, str) == False or len(self.value) == 0 or len(self.value) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the ControlPoint's value is not valid")
            return False

        if isinstance(self.type, str) == False or (self.type != "INT" and self.type != "FLOAT" and self.type != "DOUBLE" and self.type != "STRING" and self.type != "ARRAY"):
            log.logger.error("the ControlPoint's type is not valid")
            return False

        return True


class ControlCmd(object):
    """One control command, it can control multiple points.
    :serialId: the control command's unique serial id
    :deviceKey: the device key in EnOS Cloud Model
    :points: the list of ControlPoint
    :checkResponse: whether needing response, default is True.
    """

    def __init__(self) -> None:

        self.serialId = ""  # Required this control unique identifier, suggest to use timestamp
        self.deviceKey = ""  # Required device identifier
        self.points = []  # the list of ControlPoint

        # optional
        self.checkResponse = True  # The flag of whether needing response.

        # private
        self.__channel = ""  # it is filled by internal using app_name, keep it default ""

    def setChannel(self, channel: str) -> None:
        self.__channel = channel

    def getChannel(self) -> str:
        return self.__channel

    def isValid(self) -> bool:
        if isinstance(self.serialId, str) == False or len(self.serialId) == 0 or len(self.serialId) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the serialId's value is not valid")
            return False

        if isinstance(self.deviceKey, str) == False or len(self.deviceKey) == 0 or len(self.deviceKey) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the deviceKey's value is not valid")
            return False

        if not isinstance(self.checkResponse, bool):
            log.logger.error("the checkResponse's value is not valid")
            return False

        if not isinstance(self.points, list):
            log.logger.error("the points's value is not valid")
            return False

        if not isinstance(self.__channel, str):
            log.logger.error("the __channel's value is not valid")
            return False

        for point in self.points:
            if isinstance(point, ControlPoint) == False:
                return False

            if point.isValid() == False:
                return False

        return True


class ControlCmdResult(object):
    """control command's result
    :serialId: the control command's unique serial id
    :status: the control command's result, 1:success, other: failed
    :desc: the reason description if control failed
    """

    def __init__(self) -> None:
        self.serialId = ""  # the command serial id
        self.status = -1  # the control result, 1:success, other: failed
        self.desc = ""  # the description if control failed

    def isValid(self) -> bool:
        if len(self.serialId) == 0 or len(self.serialId) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the ControlCmdResult's serialId is not valid")
            return False

        return True


class ControlCmdFormulaBitsMToN(object):
    """BITS_M_TO_N formula info.
    :operandsSize: number of operands
    :relatedPoint: Association Model Point Identifier in EnOS Cloud Model
    :relatedPointTimeout: Association model point collection timeout
    :lowBit: low bit
    :highBit: high bit
    :defaultPoint: defaultPoint value
    :defaultPointLowBit: defaultPoint low bit
    :defaultPointHighBit: defaultPoint high bit
    :hasDefault: has defaultPoint 
    """

    def __init__(self) -> None:

        self.operandsSize = 0
        self.relatedPoint = ""
        self.relatedPointTimeout = 3600
        self.lowBit = 0
        self.highBit = 0
        self.defaultPoint = 0
        self.defaultPointLowBit = 0
        self.defaultPointHighBit = 0
        self.hasDefault = False

    def ParseOperands(self, operands: list) -> bool:
        self.operandsSize = len(operands)
        if self.operandsSize < 4:
            log.logger.error("the operands's size is not valid(%d)" % self.operandsSize)
            return False
        if self.operandsSize > 4 and self.operandsSize < 7:
            log.logger.error("the operands's size is not valid(%d)" % self.operandsSize)
            return False

        if isinstance(operands[0], str) == False:
            log.logger.error("the operands[0] is not valid")
            return False

        self.relatedPoint = operands[0]

        if isinstance(operands[1], str) == False:
            log.logger.error("the operands[1] is not valid")
            return False

        self.relatedPointTimeout = int(operands[1])

        if isinstance(operands[2], str) == False:
            log.logger.error("the operands[2] is not valid")
            return False

        self.lowBit = int(operands[2])

        if isinstance(operands[3], str) == False:
            log.logger.error("the operands[3] is not valid")
            return False

        self.highBit = int(operands[3])
        
        if self.operandsSize >= 7 and len(operands[4]) > 0 and len(operands[5]) > 0 and len(operands[6]) > 0:
            self.hasDefault = True
            if isinstance(operands[4],str) == False:
                log.logger.error("the operands[4] is not valid")
                return False
            self.defaultPoint = int(operands[4])
            
            if isinstance(operands[5],str) == False:
                log.logger.error("the operands[5] is not valid")
                return False
            self.defaultPointLowBit = int(operands[5])
            
            if isinstance(operands[6],str) == False:
                log.logger.error("the operands[6] is not valid")
                return False
            self.defaultPointHighBit = int(operands[6])
            
            
    def isValid(self) -> bool:
        if not isinstance(self.operandsSize, int):
            log.logger.error("the operandsSize's value is not valid")
            return False

        if isinstance(self.relatedPoint, str) == False or len(self.relatedPoint) == 0 or len(self.relatedPoint) > REDIS_MAX_KEY_LENGTH:
            log.logger.error("the relatedPoint's value is not valid")
            return False

        if not isinstance(self.relatedPointTimeout, int):
            log.logger.error("the relatedPointTimeout's value is not valid")
            return False

        if not isinstance(self.lowBit, int):
            log.logger.error("the lowBit's value is not valid")
            return False

        if not isinstance(self.highBit, int):
            log.logger.error("the highBit's value is not valid")
            return False
        
        if not isinstance(self.defaultPoint, int):
            log.logger.error("the defaultPoint's value is not valid")
            return False
        
        if not isinstance(self.defaultPointLowBit, int):
            log.logger.error("the defaultPointLowBit's value is not valid")
            return False
        
        if not isinstance(self.defaultPointHighBit, int):
            log.logger.error("the defaultPointHighBit's value is not valid")
            return False
        
        # check bit
        if self.highBit < self.lowBit:
            log.logger.error("the highBit and lowBit is not valid")
            return False
        
        if self.hasDefault == True:
            if self.defaultPointHighBit < self.defaultPointLowBit:
                log.logger.error("the defaultPointHighBit and defaultPointLowBit is not valid")
                return False
            
            #if self.lowBit <= self.defaultPointHighBit and self.highBit >= self.defaultPointLowBit:
            #    log.logger.error("the bits intersect is not valid")
            #    return False
        
        return True
