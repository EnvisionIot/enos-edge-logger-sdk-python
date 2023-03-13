# coding=utf-8
from edgelogger.core.internal.RedisDataAPI import RedisDataAPI
import redis
import unittest


class RedisDataAPITest(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)
        self.__redis_conn = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
        self.redis_api = RedisDataAPI()

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    #
    # GetResourcePublishStatus
    #
    def test_GetResourcePublishStatus_001(self):
        redis_key_resource = "local:c2app.resource.publish.finish.status"
        self.__redis_conn.delete(redis_key_resource)
        self.assertEqual(self.redis_api.GetResourcePublishStatus(), False)

    def test_GetResourcePublishStatus_002(self):
        redis_key_resource = "local:c2app.resource.publish.finish.status"
        self.__redis_conn.set(redis_key_resource, "true")
        self.assertEqual(self.redis_api.GetResourcePublishStatus(), True)

    def test_GetResourcePublishStatus_003(self):
        redis_key_resource = "local:c2app.resource.publish.finish.status"
        self.__redis_conn.set(redis_key_resource, "True")
        self.assertEqual(self.redis_api.GetResourcePublishStatus(), False)

    def test_GetResourcePublishStatus_004(self):
        redis_key_resource = "local:c2app.resource.publish.finish.status"
        self.__redis_conn.set(redis_key_resource, "false")
        self.assertEqual(self.redis_api.GetResourcePublishStatus(), False)

    #
    # GetAllDeviceKey
    #
    def test_GetAllDeviceKey_case_001(self):
        redis_key_assetid_to_devicekey = "conf:c2cw.assetid.devicekey"
        self.__redis_conn.delete(redis_key_assetid_to_devicekey)
        self.assertEqual(self.redis_api.GetAllDeviceKey(), [])

    def test_GetAllDeviceKey_case_002(self):
        redis_key_assetid_to_devicekey = "conf:c2cw.assetid.devicekey"
        self.__redis_conn.hset(redis_key_assetid_to_devicekey, "asset001", "deviceKey001")
        self.__redis_conn.hset(redis_key_assetid_to_devicekey, "asset002", "deviceKey002")
        self.__redis_conn.hset(redis_key_assetid_to_devicekey, "asset003", "deviceKey003")
        self.__redis_conn.hset(redis_key_assetid_to_devicekey, "asset004", "deviceKey004")
        self.__redis_conn.hset(redis_key_assetid_to_devicekey, "asset005", "deviceKey005")
        self.assertEqual(self.redis_api.GetAllDeviceKey(), ['deviceKey001', 'deviceKey002', 'deviceKey003', 'deviceKey004', 'deviceKey005'])

    #
    # GetDeviceState
    #
    def test_GetDeviceState_case_001(self):
        redis_key_device_status = "collect:c2app.device.status"
        self.__redis_conn.delete(redis_key_device_status)
        self.assertEqual(self.redis_api.GetDeviceState("deviceKey001"), 3)

    def test_GetDeviceState_case_002(self):
        redis_key_device_status = "collect:c2app.device.status"
        self.__redis_conn.hset(redis_key_device_status, "deviceKey001", 1)
        self.assertEqual(self.redis_api.GetDeviceState("deviceKey001"), 1)

    def test_GetDeviceState_case_003(self):
        redis_key_device_status = "collect:c2app.device.status"
        self.__redis_conn.hset(redis_key_device_status, "deviceKey001", 2)
        self.assertEqual(self.redis_api.GetDeviceState("deviceKey001"), 2)

    def test_GetDeviceState_case_003(self):
        redis_key_device_status = "collect:c2app.device.status"
        self.__redis_conn.hset(redis_key_device_status, "deviceKey001", 3)
        self.assertEqual(self.redis_api.GetDeviceState("deviceKey001"), 4)

    #
    # GetDeviceIdsByDeviceKey
    #
    def test_GetDeviceIdsByDeviceKey_case_001(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        self.__redis_conn.delete(redis_key_deviceid_2_devicekey)
        self.assertEqual(self.redis_api.GetDeviceIdsByDeviceKey("deviceKey001"), [])

    def test_GetDeviceIdsByDeviceKey_case_002(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId001", "deviceKey001")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId002", "deviceKey002")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_1", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_2", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_3", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId004", "deviceKey004")
        self.assertEqual(self.redis_api.GetDeviceIdsByDeviceKey("deviceKey003"), ['deviceId003', 'deviceId003_1', 'deviceId003_2', 'deviceId003_3'])

    #
    # GetDeviceLinkState
    #
    def test_GetDeviceLinkStatus_case_001(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        redis_key_deviceid_2_status = "collect:d2cw.device.status"
        self.__redis_conn.delete(redis_key_deviceid_2_devicekey)
        self.__redis_conn.delete(redis_key_deviceid_2_status)
        self.assertEqual(self.redis_api.GetDeviceLinkState("deviceKey001"), 3)

    def test_GetDeviceLinkStatus_case_002(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId001", "deviceKey001")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId002", "deviceKey002")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_1", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_2", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_3", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId004", "deviceKey004")

        redis_key_deviceid_2_status = "collect:d2cw.device.status"
        self.__redis_conn.delete(redis_key_deviceid_2_status)
        self.assertEqual(self.redis_api.GetDeviceLinkState("deviceKey001"), 4)

    def test_GetDeviceLinkStatus_case_003(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId001", "deviceKey001")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId002", "deviceKey002")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_1", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_2", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_3", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId004", "deviceKey004")

        redis_key_deviceid_2_status = "collect:d2cw.device.status"
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003", 0)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_1", 1)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_2", 0)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_3", 0)
        self.assertEqual(self.redis_api.GetDeviceLinkState("deviceKey003"), 1)

    def test_GetDeviceLinkStatus_case_003(self):
        redis_key_deviceid_2_devicekey = "conf:c2cw.deviceid.devicekey"
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId001", "deviceKey001")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId002", "deviceKey002")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_1", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_2", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId003_3", "deviceKey003")
        self.__redis_conn.hset(redis_key_deviceid_2_devicekey, "deviceId004", "deviceKey004")

        redis_key_deviceid_2_status = "collect:d2cw.device.status"
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003", 0)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_1", 0)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_2", 0)
        self.__redis_conn.hset(redis_key_deviceid_2_status, "deviceId003_3", 0)
        self.assertEqual(self.redis_api.GetDeviceLinkState("deviceKey003"), 2)

    #
    # RegisterSubscribeChannelName
    #
    def test_RegisterSubscribeChannelName_case_001(self):
        channel_name = "xfc_test"
        devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
                          "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
                          "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
                          "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}
        ret = self.redis_api.RegisterSubscribeChannelName(channel_name, devices_points, True)
        self.assertEqual(ret, 0)

    def test_RegisterSubscribeChannelName_case_002(self):
        channel_name = "xfc_test"
        devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
                          "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
                          "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
                          "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}
        ret = self.redis_api.RegisterSubscribeChannelName(channel_name, devices_points, False)
        self.assertEqual(ret, -1)

    def test_RegisterSubscribeChannelName_case_003(self):
        channel_name = "xfc_test"
        devices_points = {"assetId001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
                          "assetId002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
                          "assetId003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
                          "assetId004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}

        self.__redis_conn.hset("conf:c2cw.assetid.devicekey", "assetId001", "deviceKey001")
        self.__redis_conn.hset("conf:c2cw.assetid.devicekey", "assetId002", "deviceKey002")
        self.__redis_conn.hset("conf:c2cw.assetid.devicekey", "assetId003", "deviceKey003")
        self.__redis_conn.hset("conf:c2cw.assetid.devicekey", "assetId004", "deviceKey004")
        ret = self.redis_api.RegisterSubscribeChannelName(channel_name, devices_points, False)
        self.assertEqual(ret, 0)

    #
    # RegisterRequiredPoints
    #
    def test_RegisterRequiredPoints_case_001(self):
        channel_name = "xfc_test"
        devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
                          "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
                          "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
                          "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}
        ret = self.redis_api.RegisterRequiredPoints(devices_points, channel_name)
        self.assertEqual(ret, 0)

    def test_RegisterRequiredPoints_case_002(self):
        devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
                          "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
                          "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
                          "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}
        ret = self.redis_api.RegisterRequiredPoints(devices_points)
        self.assertEqual(ret, 0)

    #
    # GetAModelValue
    #
    def test_GetAModelValue_case_001(self):
        device_key = "deviceKey001"
        domain_name = "domain_001_2"
        redis_key_model_value = "subscribe:c2dapp:" + device_key + ":points.value"
        self.__redis_conn.delete(redis_key_model_value)
        ret = self.redis_api.GetAModelValue(device_key, domain_name, True)
        self.assertEqual(ret, -1)

    def test_GetAModelValue_case_002(self):
        device_key = "deviceKey001"
        domain_name = "domain_001_2"
        domain_value = ""
        redis_key_model_value = "subscribe:c2dapp:" + device_key + ":points.value"
        self.__redis_conn.hset(redis_key_model_value, domain_name, domain_value)
        ret = self.redis_api.GetAModelValue(device_key, domain_name, True)
        self.assertEqual(ret, None)

    def test_GetAModelValue_case_003(self):
        device_key = "deviceKey001"
        domain_name = "domain_001"
        domain_value = '{"domainName": "domain001","value": "value001", "assetId":"assetId_001", "deviceKey":"deviceKey_001", "domainValueType": "DOUBLE", "timestamp":100, "oemtime": 1000, "quality":10, "flagUsingOem":false}'
        redis_key_model_value = "subscribe:c2dapp:" + device_key + ":points.value"
        self.__redis_conn.hset(redis_key_model_value, domain_name, domain_value)
        ret = self.redis_api.GetAModelValue(device_key, domain_name, True)
        self.assertEqual(ret, "value001")

    #
    # SetModelValue
    #

if __name__ == "__main__":
    print("Start to run RedisDataAPI Unit Test")
    unittest.main()

    redis_conn = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
    redis_key = "not_valid"
    value = redis_conn.hget(redis_key, "hello")
    print(value)