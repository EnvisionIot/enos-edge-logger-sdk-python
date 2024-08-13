# Using EnOS Edge Logger SDK for Python
Table of Contents

* [Installation](#install)
    * [Prerequisites](#pre)
    * [Building From Source](#obtain)
* [Feature List](#feature)
* [Quick Start](#start)
* [Sample Codes](#sample)
* [Release Notes](#releasenotes)

The EnOS Edge Logger SDK for Python allows developers to communicate with EnOS Edge Logger, such as Get/Set the Model value, Send control command to device and Get the result of control, Maintain the app realted config,  etc.

<a name="install"></a>

<a name="pre"></a>

### Prerequisites

To use the EnOS Edge Logger SDK, you will need Python 3.5.3 or later. Note that Python 2.x is not supported as some functions might not be compatible with Python 2.x.

You can install the SDK by building from source.

<a name="obtain"></a>

### Building From Source

1. Obtain the source code of EnOS Edge Logger SDK for Python.
    ```
    git clone http://git.eniot.io/edge/edge-logger-sdk-python.git
    ```

2. From the directory where the source code is stored, run the following command(HPU as example):
   ```
   python3 setup.py install --install-lib=/usr/local/lib/python3.7/dist-packages/
   ```

<a name="feature"></a>

## Feature List

### There are two APIs for Logger:

#### 1. EdgeAPI (Loop Model, using Redis as Midware)
from edgelogger.core.EdgeAPI import *

#### 2. EdgeSubscribeAPI (Subscribe model, using ZeroMQ as Midware)
from edgelogger.core.EdgeSubscribeAPI import *

<a name="start"></a>

## Quick Start
For EdgeSubscribeAPI as Example:

### 1. Create the API instance
```python
edge_sub_api = EdgeSubscribeAPI()
```
### 2. Register your required device's points
```python
 devices_points = {"deviceKey001": ["domain001", "domain001_2", "domain001_3", "domain001_4"],
                   "deviceKey002": ["domain002", "domain002_2", "domain002_3", "domain002_4"],
                   "deviceKey003": ["domain003", "domain003_2", "domain003_3", "domain003_4"],
                   "deviceKey004": ["domain004", "domain004_2", "domain004_3", "domain004_4"]}
edge_sub_api.RegisterRequiredPoints(device_points, app_name)
```
### 3. Get the points' value
```python
    models_list = edge_sub_api.SubcribeModelsValue()
    for md in models_list:
        print("""domainName:%s, deviceKey:%s, assetId:%s, domainValue:%s, domainValueType:%s, flagUsingOem:%s, timeValue:%d,"""
              """ oemTime:%d, quality:%d""" % (md.domainName, md.deviceKey, md.assetId, md.domainValue, md.domainValueType,
                                               "True" if md.flagUsingOem else "False", md.timeValue, md.oemTime, md.quality))

```

<a name="sample"></a>

# Sample Codes
* [EdgeAPI] edgelogger/sample/EdgeAPISample.py
* [EdgeSubscribeAPI] edgelogger/sample/EdgeSubscribeAPISample.py

<a name="releasenotes"></a>

## Release Notes
- 2022/11/30(1.0.0): first released python sdk.
- 2023/10/09(): add GetAllDevicesNameAndModelIdPath and GetADeviceNameAndModelIdPath.