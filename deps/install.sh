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

if [[ "${KVERSION}" == *"EnHPU"* ]]; then
    echo "This is EnHPU Edge box"
    tar zxf deps/pyzmq-hpu.tar.gz -C /usr/local/lib/python3.7/dist-packages/
    echo "install libzmq on HPU success"
else
    echo "start to install pyzmq"
    pip3 install pyzmq
fi