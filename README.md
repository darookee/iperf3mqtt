# iperf3mqtt

This image runs iperf3 speedtests on servers specified in the configuration file
and publishes the results to MQTT.
This can be used to create a speedtest sensor in Home Assitant, especially when
running it on a RaspberryPi.

## Configuration

### config.yaml
```
interval: 2h
hosts:
  - host: ping.online.net
    ports:
      - 5201
      - 5202
  - host: bouygues.iperf.fr
    ports:
      - 5207
      - 5208
      - 5209
mqtt:
  host: mqtt.host
  username: speedtest
  password: speedtest
  topic: sensor/speedtest
```

The hosts are taken from the [iperf3 public server list](https://iperf.fr/iperf-servers.php)

### homeassistant

#### Download
```
platform: mqtt
name: "speedtest_download"
state_topic: "sensor/speedtest/download"
value_template: '{{ (value|float/1000000)|round(1) }}'
unit_of_measurement: "Mbit/s"
```

#### Upload
```
platform: mqtt
name: "speedtest_upload"
state_topic: "sensor/speedtest/upload"
value_template: '{{ (value|float/1000000)|round(1) }}'
unit_of_measurement: "Mbit/s"
```

#### Ping
```
platform: mqtt
name: "speedtest_ping"
state_topic: "sensor/speedtest/ping"
unit_of_measurement: "ms"
```

## Running

### from commandline

```
docker run --rm -v ${PWD}/config.yaml:/config.yaml darookee/iperf3mqtt
```

### using docker-compose

```
version: '3.7'

services:
  speedtest:
    image: darookee/iperf3mqtt
    restart: unless-stopped
    container_name: speedtest
    volumes:
      - ./config.yaml:/config.yaml:ro
```
