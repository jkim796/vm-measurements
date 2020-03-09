FROM tensorflow/tensorflow:1.13.2

RUN apt-get update \
    && apt-get install -y git
    && apt-get install -y numactl
RUN git clone https://github.com/aymericdamien/TensorFlow-Examples.git
RUN python -m pip install -U pip setuptools
RUN python -m pip install matplotlib

WORKDIR /TensorFlow-Examples/examples

ENV PYTHONPATH="$PYTHONPATH:/TensorFlow-Examples/examples"

ENV workload "3_NeuralNetworks/convolutional_network.py"
CMD numactl -N 0 -m 0 python ${workload}
