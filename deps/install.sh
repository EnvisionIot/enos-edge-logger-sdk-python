#!/bin/bash
echo "Start to install Edge Logger for Python SDK dependent libs"

KVERSION=$(which kversion)
if [ -n "$KVERSION" ]; then
    KVERSION=$(kversion)
else
    KVERSION=""
fi

echo "start to install required libs"
apt-get install -y python3-pip python3-six

if [[ "${KVERSION}" == "EnHPUY" ]]; then
    echo "start to install pyzmq on HPU-Y"
    pip3 install pyzmq
    echo "install libzmq on HPU-Y success"
elif [[ "${KVERSION}" == "EnHPU" ]]; then
    echo "start to install pyzmq on HPU"
    tar zxf deps/pyzmq-hpu.tar.gz -C /usr/local/lib/python3.7/dist-packages/
    echo "install libzmq on HPU success"
elif [[ "$KVERSION" == "EnDTU-A" ]]; then
    echo "start to install pyzmq on DTU-A"
    pip3 install ./deps/pyzmq-26.0.3-cp37-cp37m-linux_armv7l.whl
    echo "install libzmq on DTU-A success"
else
    echo "start to install pyzmq"
    pip3 install pyzmq
    echo "install libzmq success"
fi
