from edgelogger.core.EdgeAPI import *
from edgelogger.core.log.logger import log


def testFunc():
    edge_api = EdgeAPI()

    app_name = "xfc_test"
    # devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4", "domain001_5"],
    #                   "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4", "domain002_5"],
    #                   "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4", "domain003_5"],
    #                   "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4", "domain004_5"]}

    devices_points = {"INV_xfc_1055": ["fjxychm_double_ai_10", "fjxychm_double_ai_11",
                                       "fjxychm_double_ai_24", "fjxychm_double_ai_25", "fjxychm_double_ai_80"]}

    # step1: Register the device point
    ret = edge_api.RegisterRequiredPoints(devices_points, app_name)
    if ret != 0:
        print("failed to register required points")
        return

    # step2: Get the device key
    device_key_list = edge_api.GetAllDeviceKey()
    print("there are %d devices in this Edge Logger" % len(device_key_list))
    for dev_key in device_key_list:
        print("device " + dev_key + "'s status is:%d, link's status is:%d" % (edge_api.GetDeviceState(dev_key), edge_api.GetDeviceLinkState(dev_key)))

    print(device_key_list)

    device_key = "uKCz5FfXOg"
    domain_name = "fjxychm_double_ai_10"

    # step3-0: Get the point's value, return str
    model_value = edge_api.GetAModelValue(device_key, domain_name)
    if model_value is not None:
        print("model(%s) value in device(%s) is:%s" % (domain_name, device_key, model_value))
    else:
        print("failed to get model(%s) value in device(%s)" % (domain_name, device_key))

    # step3-1: Get the point's value, return ModelValue
    model_value = edge_api.GetAModelValue(device_key, domain_name, False)
    if model_value is not None:
        print("model(%s) value in device(%s) is:%s" % (domain_name, device_key, model_value.domainValue))
    else:
        print("failed to get model(%s) value in device(%s)" % (domain_name, device_key))

    # step3-2: Get all points' value, return list of ModelValue
    all_models_value = edge_api.GetAllModelValuesBydeviceKey(device_key)
    print("all models value count(%d):" % len(all_models_value))
    for value in all_models_value:
        print("device_key(%s) model(%s) value is:%s" % (value.deviceKey, value.domainName, value.domainValue))
        # value.print()

    # step4: write Model value
    set_domain_name = "fjxychm_double_ai_80"
    model = ModelSetValue()
    model.deviceKey = device_key
    model.domainName = set_domain_name
    model.domainValue = "100"

    # optional
    model.oemTime = 23424243223242347
    model.flagUsingOem = True
    model.timeValue = 0
    model.quality = 2
    model.transferWay = 1
    ret = edge_api.SetModelsValue([model])
    if ret == 0:
        print("set a model value success")
    else:
        print("failed to set model value")

    model_value = edge_api.GetAModelValue(device_key, set_domain_name, False)
    if model_value is not None:
        print("model(%s) value in device(%s) is:%s" % (set_domain_name, device_key, model_value.domainValue))
    else:
        print("failed to get model(%s) value in device(%s)" % (set_domain_name, device_key))

    # step5-0: Set A Cmd
    cmd_domain_name = "AIMark11"
    ret = edge_api.SetAModelCmd(device_key, cmd_domain_name, "3", "1111111")
    if ret == 0:
        print("set a cmd success")
    else:
        print("failed to set a cmd")

    #step5-1: SetModelsCmd
    ctrl_cmd = ControlCmd()
    ctrl_cmd.serialId = "234243"
    ctrl_cmd.deviceKey = device_key

    ctrl_cmd.checkResponse = True

    ctrl_point1 = ControlPoint()
    ctrl_point1.domainName = "fjxychm_double_ai_80"
    ctrl_point1.value = "11"
    ctrl_point1.type = "DOUBLE"

    ctrl_point2 = ControlPoint()
    ctrl_point2.domainName = "fjxychm_double_ai_8"
    ctrl_point2.value = "800"
    ctrl_point2.type = "DOUBLE"

    ctrl_point3 = ControlPoint()
    ctrl_point3.domainName = "enum_001"
    ctrl_point3.value = "1"
    ctrl_point3.type = "DOUBLE"

    ctrl_cmd.points = [ctrl_point1, ctrl_point2, ctrl_point3]

    ret = edge_api.SetModelsCmd(ctrl_cmd, 600)
    if ret == 0:
        print("SetModelsCmd success")
    else:
        print("SetModelsCmd failed")

    # step6-0:Get Cmd return status
    cmd_ret_result = edge_api.GetAModelCmdResult()
    if cmd_ret_result is not None:
        print("serialId=%s, status=%d, desc=%s" % (cmd_ret_result.serialId, cmd_ret_result.status, cmd_ret_result.desc))
    else:
        print("cmd ret is empty")

    # step6-1:Get Cmd return status
    cmd_ret_result_list = edge_api.GetAllCmdResult()
    if cmd_ret_result_list is not None:
        for cmd_ret_result in cmd_ret_result_list:
            print("serialId=%s, status=%d, desc=%s" % (cmd_ret_result.serialId, cmd_ret_result.status, cmd_ret_result.desc))
    else:
        print("cmd ret is empty, cannot get")

    # step7-0: Set APP config
    app_key = "name"
    app_value = "EdgeAPISample"
    ret = edge_api.SetAppConfig(app_key, app_value)
    if ret == 0:
        print("set app config success")
    else:
        print("set app config failed")

    # step7-1: Get APP Config
    value = edge_api.GetAppConfig(app_key)
    print("key=%s, value=%s" % (app_key, value))

    # step7-2: Delete APP Config
    ret = edge_api.DeleteAppConfig(app_key)
    if ret == 0:
        print("delete app config success")
    else:
        print("app key(%s) is not exist" % app_key)

    # step7-3: Delete APP all Config
    ret = edge_api.DeleteAppAllConfig()
    if ret == None:
        print("no app config exist")
    elif ret == 0:
        print("delete app all config success")
    else:
        print("delete all app config failed")

def SetAModelCmdTest():
    app_name = "chm_test"
    edge_api = EdgeAPI()
    status = edge_api.RegisterRequiredPoints({"test":[]}, app_name)
    print(status)
    
    device_key = "uKCz5FfXOg"
    #cmd_domain_name = "AIMark11"
    #ret = edge_api.SetAModelCmd(device_key, cmd_domain_name, "3", "1")
    #if ret == 0:
    #    print("set a cmd success")
    #else:
    #    print("failed to set a cmd")
    #    
    #cmd_domain_name = "AOMark1"
    #ret = edge_api.SetAModelCmd(device_key, cmd_domain_name, "3", "2")
    #if ret == 0:
    #    print("set a cmd success")
    #else:
    #    print("failed to set a cmd")
        
    cmd_domain_name = "AIMark11"
    ret = edge_api.SetAModelCmd(device_key, cmd_domain_name, "7", "2")
    if ret == 0:
        print("set a cmd success")
    else:
        print("failed to set a cmd")
        

def GetAllDevicesNameAndModelIdPathTest():
    edge_api = EdgeAPI()
    all_device_info = edge_api.GetAllDevicesNameAndModelIdPath()
    print("get all device name and modelId")
    print(all_device_info)

    device_key = "logger_dev_1302"
    device_info = edge_api.GetADeviceNameAndModelIdPath(device_key)
    print("get deviceKey(%s) name and modelId(%s)" % (device_key, device_info))


if __name__ == "__main__":
    app_name = "xfc_test"
    edge_api = EdgeAPI()
    status = edge_api.RegisterRequiredPoints({"test":[]}, app_name)
    print(status)

    # edge_api.DeleteAppAllConfig()
    edge_api.UnRegisterApp()

    device_key = "INV_xfc_1055"
    attribute = "invType"
    attr_vlaue = edge_api.GetAttributeValue(device_key, attribute)
    print(attr_vlaue)

    SetAModelCmdTest()

    # testFunc()

