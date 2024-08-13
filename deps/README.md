# Install pyzmq manully on EnHPU Edge box
the pyzmq cannot install successfully via cmd `pip install pyzmq`, so it needs to be compiled manually.

The package pyzmq-hpu.tar.gz has already been built, you can follow the steps:
1) upload the pyzmq-hpu.tar.gz to your EnHPU box;
2) tar zxvf pyzmq-hpu.tar.gz
3) cp zmq/ /usr/lib64/python3/dist-packages/zmq -rf

After above three steps, you can use zmq lib now. You can test via command `python3 -c "import zmq"`