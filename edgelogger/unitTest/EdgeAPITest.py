from edgelogger.core.EdgeAPI import *

def test_func():
    edge_logger_ip = "127.0.0.1"
    edge_api = EdgeAPI(edge_logger_ip=edge_logger_ip)

    device_list = edge_api.GetAllDeviceKey()
    print(device_list)

    device_key = "INV_xfc_1055"
    domain_name = "fjxychm_double_ai_10"
    device_state = edge_api.GetDeviceState(device_key)
    print("device status: %d" % device_state)

    link_status = edge_api.GetDeviceLinkState(device_key)
    print("link_status: %d" % link_status)

    app_name = "Demo"
    devices_points = {"INV_xfc_1055": ["fjxychm_double_ai_10", "fjxychm_double_ai_11", "fjxychm_double_ai_8", "string_1024", "enum_001",
                                       "timestamp_001", "fjxychm_double_ai_24", "fjxychm_double_ai_25", "fjxychm_double_ai_80", "fjxychm_double_ai_40"]}
    ret = edge_api.RegisterRequiredPoints(devices_points, app_name)
    print("register result: %d" % ret)

    # ret = edge_api.UnRegisterApp()
    # print("unregister result: %d" % ret)

    device_key = "INV_xfc_1055"
    domain_name = "fjxychm_double_ai_10"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("int module value:%s" % value)

    domain_name = "fjxychm_double_ai_24"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("double module value:%s" % value)

    domain_name = "fjxychm_double_ai_40"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("array module value:%s" % value)

    domain_name = "fjxychm_double_ai_8"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("float module value:%s" % value)

    domain_name = "string_1024"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("text module value:%s" % value)

    domain_name = "enum_001"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("enum module value:%s" % value)

    domain_name = "timestamp_001"
    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("timestamp module value:%s" % value)

    value = edge_api.GetAModelValue(device_key, domain_name, True)
    print("module value:%s" % value)

    all_models_value = edge_api.GetAllModelValuesBydeviceKey(device_key)
    print("all models value count(%d):" % len(all_models_value))
    for value in all_models_value:
        print("device_key(%s) model(%s) value is:%s" % (value.deviceKey, value.domainName, value.domainValue))

    #test: SetModelValue
    set_domain_name = "fjxychm_double_ai_80"
    model = ModelSetValue()
    model.deviceKey = device_key
    model.domainName = set_domain_name
    model.domainValue = "100"
    model.oemTime = 23424243223242347
    model.flagUsingOem = True
    model.timeValue = 0
    model.quality = 2
    model.transferWay = 1

    set_domain_name = "fjxychm_double_ai_81afadfadfda"
    model2 = ModelSetValue()
    model2.deviceKey = device_key
    model2.domainName = set_domain_name
    model2.domainValue = "100"
    model2.oemTime = 23424243223242347
    model2.flagUsingOem = True
    model2.timeValue = 0
    model2.quality = 2
    model2.transferWay = 1

    ret = edge_api.SetModelsValue([model, model2])
    if ret == 0:
        print("set a model value success")
    else:
        print("failed to set model value")

    # test: GetAttributeValue
    device_key = "INV_xfc_1055"
    attribute = "invType"
    attr_vlaue = edge_api.GetAttributeValue(device_key, attribute)
    print(attr_vlaue)

    # test: SetAModelCmd
    cmd_domain_name = "fjxychm_double_ai_8"
    ret = edge_api.SetAModelCmd(device_key, cmd_domain_name, "20", "11121", "INT", False)
    if ret == 0:
        print("set a cmd success:%d" % ret)
    else:
        print("failed to set a cmd:%d" % ret)

    # test: SetModelsCmd
    ctrl_cmd = ControlCmd()
    ctrl_cmd.serialId = "234243"
    ctrl_cmd.deviceKey = device_key

    ctrl_cmd.checkResponse = True

    # CONTROL_REPLACE_N
    ctrl_point1 = ControlPoint()
    ctrl_point1.domainName = "fjxychm_double_ai_80"
    ctrl_point1.value = "111"
    ctrl_point1.type = "DOUBLE"

    # CONTROL_SET
    ctrl_point2 = ControlPoint()
    ctrl_point2.domainName = "fjxychm_double_ai_8"
    ctrl_point2.value = "800"
    ctrl_point2.type = "DOUBLE"

    # CONTROL_ENUM_N
    ctrl_point3 = ControlPoint()
    # ctrl_point3.domainName = "enum_001"
    ctrl_point3.domainName = "enum_001"
    ctrl_point3.value = "1"
    ctrl_point3.type = "DOUBLE"

    ctrl_cmd.points = [ctrl_point1, ctrl_point2, ctrl_point3]
    # ctrl_cmd.points = []

    ret = edge_api.SetModelsCmd(ctrl_cmd, 600)
    if ret == 0:
        print("SetModelsCmd success:%d" % ret)
    else:
        print("SetModelsCmd failed:%d" % ret)

    # test: GetAModelCmdResult
    cmd_ret_result = edge_api.GetAModelCmdResult(230)
    if cmd_ret_result is not None:
        print("serialId=%s, status=%d, desc=%s" % (cmd_ret_result.serialId, cmd_ret_result.status, cmd_ret_result.desc))
    else:
        print("cmd ret is empty")

    # test: GetAllCmdResult()
    cmd_ret_result_list = edge_api.GetAllCmdResult()
    if cmd_ret_result_list is not None:
        for cmd_ret_result in cmd_ret_result_list:
            print("serialId=%s, status=%d, desc=%s" % (cmd_ret_result.serialId, cmd_ret_result.status, cmd_ret_result.desc))
    else:
        print("cmd ret is empty, cannot get")

    # test: SetAppConfig
    app_key = "name"
    app_value = "EdgeAPISample"
    ret = edge_api.SetAppConfig(app_key, app_value)
    if ret == 0:
        print("set app config success")
    else:
        print("set app config failed")

    ret = edge_api.SetAppConfig("test", "test")
    # test: GetAppConfig
    value = edge_api.GetAppConfig(app_key)
    print("key=%s, value=%s" % (app_key, value))

    # test: DeleteAppConfig
    ret = edge_api.DeleteAppConfig(app_key)
    if ret == 0:
        print("delete app config success")
    else:
        print("app key(%s) is not exist" % app_key)

    # test: DeleteAppAllConfig
    ret = edge_api.DeleteAppAllConfig()
    if ret == None:
        print("no app config exist")
    elif ret == 0:
        print("delete app all config success")
    else:
        print("delete all app config failed")

if __name__ == "__main__":
    test_func()
