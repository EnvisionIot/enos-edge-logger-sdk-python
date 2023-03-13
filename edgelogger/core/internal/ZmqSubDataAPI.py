import zmq
from edgelogger.core.internal.EdgeDataType import *
from edgelogger.core.log.logger import log
from typing import List


class ZmqSubDataAPI(object):
    def __init__(self, zmq_address) -> None:
        self.__address = zmq_address
        self.started = False

    def StartSubscribe(self, topic) -> None:
        self.__topic = topic
        self.context = zmq.Context()
        self.socket_sub = self.context.socket(zmq.SUB)
        self.socket_sub.connect(self.__address)
        self.socket_sub.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.started = True

    def StopSubscribe(self) -> None:
        self.socket_sub.close()
        self.started = False

    def __CheckCS(self, data) -> int:
        num = 0
        for i in range(len(data)):
            num = (num + (int(data[i]) & 0xFF)) % 256

        return num

    def __UnpackModelsValue(self, msg) -> List[ModelValue]:
        try:
            data_list = json.loads(msg)
        except Exception as e:
            log.logger.error("failed to decode json str:%s" % msg)
            return None

        if not isinstance(data_list, list):
            log.logger.error("the json data type is not array")
            return None

        model_list = []
        for json_msg in data_list:
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
            model_list.append(sub_data)

        return model_list

    def SubcribeModelsValue(self) -> List[ModelValue]:
        if self.started == False:
            log.logger.error("Please start to call StartSubscribe first")
            return -1

        # Data format: [topic][' '][0xAA,0x88][CSCode][json msg][0xBB,0x77,'\0'] + '\0'
        recv_raw_data = self.socket_sub.recv_multipart()
        log.logger.debug("zmq recv data:")
        log.logger.debug(recv_raw_data)
        if len(recv_raw_data) == 0 or len(recv_raw_data[0]) == 0:
            log.logger.error("the zmq data size is zero, invalid data")
            return None

        recv_data = recv_raw_data[0]

        recv_data_len = len(recv_data)
        log.logger.debug("recv from zmq:%s(%d)" % (recv_data, recv_data_len))
        topic_len = len(self.__topic)

        if recv_data_len < topic_len + 8:
            log.logger.error("the zmq data size is error, invalid data")
            return None

        for i in range(len(self.__topic)):
            if chr(recv_data[i]) != self.__topic[i]:
                log.logger.error("the zmq data is error, not start with topic(%d)(%c)(%c)" % (
                                 i, recv_data[i], self.__topic[i]))
                return None

        if chr(recv_data[topic_len]) != ' ':
            log.logger.error("the zmq data is error, not blank after topic")
            return None

        if (int(recv_data[topic_len + 1]) & 0xFF) != 0xAA or (int(recv_data[topic_len + 2] & 0xFF) != 0x88):
            log.logger.error("the zmq data is error, not contains with starting magic code")
            return None

        if chr(recv_data[recv_data_len-1]) != '\0':
            log.logger.error("the zmq data is error, the tail is not 0")
            return None

        if chr(recv_data[recv_data_len - 2]) != '\0':
            log.logger.error("the zmq data, last but two is not 0")
            return None

        tail_magic_index = recv_data_len - 3

        if (int(recv_data[tail_magic_index - 1]) & 0xFF != 0xBB or (int(recv_data[tail_magic_index] & 0xFF) != 0x77)):
            log.logger.error("the zmq data is error, not contains with tail magic code")
            return None

        cscode = int(recv_data[topic_len+3])
        json_msg = recv_data[topic_len+4:tail_magic_index-1]
        log.logger.debug("zmq json msg:%s" % json_msg)

        check_code = self.__CheckCS(json_msg)
        log.logger.debug("zmq msg: cscode=%d, check_code=%d" % (cscode, check_code))
        if check_code != cscode:
            log.logger.error("the zmq data,check CS error, checkCode=%d, msg code=%d" % (check_code, cscode))
            return None

        return self.__UnpackModelsValue(json_msg)
