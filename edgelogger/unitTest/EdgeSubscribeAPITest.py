from edgelogger.core.EdgeSubscribeAPI import *
import time

def test_func():
    box_ip = "127.0.0.1"
    edge_sub_api = EdgeSubscribeAPI(box_ip)

    app_name = "xfc_test"
    devices_points = {"INV_xfc_1055": ["fjxychm_double_ai_10", "fjxychm_double_ai_11",
                                       "fjxychm_double_ai_24", "fjxychm_double_ai_25", "fjxychm_double_ai_80"]}

    # step1: Register the device point
    ret = edge_sub_api.RegisterRequiredPoints(devices_points, app_name)
    if ret != 0:
        print("failed to register required points")
        return

    while True:
        models_list = edge_sub_api.SubcribeModelsValue()
        print("Zeromq get models count:%d" % len(models_list))
        for md in models_list:
            print("""domainName:%s, deviceKey:%s, assetId:%s, domainValue:%s, domainValueType:%s, flagUsingOem:%s, timeValue:%d,"""
                  """ oemTime:%d, quality:%d""" % (md.domainName, md.deviceKey, md.assetId, md.domainValue, md.domainValueType,
                                                   "True" if md.flagUsingOem else "False", md.timeValue, md.oemTime, md.quality))

        time.sleep(2)

if __name__ == "__main__":
    test_func()

