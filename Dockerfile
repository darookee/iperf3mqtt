FROM python:3.7-alpine

RUN apk add iperf3 && \
        pip install \
        iperf3==0.1.11 \
        paho-mqtt==1.4.0 \
        pytimeparse==1.1.8 \
        PyYAML==5.1 \
        ping3==2.1.0

ENTRYPOINT ["/bin/iperf3mqtt.py"]

COPY ./iperf3mqtt.py /bin/iperf3mqtt.py
