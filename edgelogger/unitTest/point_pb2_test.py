from sqlite3 import Timestamp
from edgelogger.core.protobuf.point_pb2 import DevicePoint, DevicePoints

def point_print(point):
    print("collectDeviceId=%s,poingName=%s,value=%s,type=%d,oemTime=%d,quality=%d,attributes=%s" % (
        point.colletDeviceId, point.pointName, point.value, point.type, point.oemTime, point.quality, point.attributes
    ))

def protobuf_test():
    dev_points = DevicePoints()
    timestamp = ""

    for i in range(4):
        point = dev_points.points.add()
        point.colletDeviceId = "11"
        point.pointName = "Temp"
        point.value = "11"
        point.type = 11 * (i + 1)
        point.oemTime = 11 * (i + 1)
        point.quality = 11 * (i + 1)
        point.attributes = "just for test attributes"

    dev_points.timestamp = 0

    data_str = dev_points.SerializeToString()
    print(data_str)

    recved_points = DevicePoints()
    recved_points.ParseFromString(data_str)
    print(len(recved_points.points))
    for point in recved_points.points:
        point_print(point)

if __name__ == "__main__":
    print("just for test protocol buffer")
    protobuf_test()
