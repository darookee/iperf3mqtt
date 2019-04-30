#!/usr/bin/env python

import sys
import time
import random
import iperf3
import paho.mqtt.client as mqtt
from ping3 import ping
from pytimeparse import parse
import yaml


def clamp(n, maxn, minn):
    return max(min(maxn, n), minn)

def run_tests(config, mqtt_config, mqttc):
    """ run both tests """
    try_count = 0
    result_down = None
    while result_down is None:
        result_down = run_test('received_bps', config)
        if result_down is None:
            try_count = try_count + 1
            print("Try %d" % try_count, file=sys.stderr)
            time.sleep(clamp(try_count*5, 60, 5))

    try_count = 0
    result_up = None
    while result_up is None:
        result_up = run_test('sent_bps', config)
        if result_up is None:
            try_count = try_count + 1
            print("Try %d" % try_count, file=sys.stderr)
            time.sleep(clamp(try_count*5, 60, 5))

    ping_result = ping(random.choice(config["hosts"])["host"], unit='ms')

    print("Down: %f, Up: %f, Ping: %f" % (result_down, result_up,
                                          ping_result))

    mqtt_port = mqtt_config.get("port", 1883)
    mqttc.connect(mqtt_config.get("host", "127.0.0.1"),
                  port=mqtt_port)

    mqttc.publish(config["mqtt"]["topic"] + "/upload", "%f" % result_up,
                  retain=True)

    mqttc.publish(config["mqtt"]["topic"] + "/download", "%f" %
                  result_down, retain=True)

    mqttc.publish(config["mqtt"]["topic"] + "/ping", "%f" %
                  ping_result, retain=True)


def run_test(test_type, config):
    """ run the actual test """
    print("Running %s" % test_type, file=sys.stderr)

    server = random.choice(config["hosts"])
    print("Using %s" % server.get("host", None), file=sys.stderr)
    client = iperf3.Client()
    client.server_hostname = server["host"]
    client.port = random.choice(server["ports"])
    client.verbose = False
    client.zerocopy = True

    if test_type == 'received_bps':
        client.reverse = True

    result = client.run()

    if result is not None and \
            hasattr(result, 'error') and \
            result.error is not None:
        print("Iperf3 error: (%s:%d) - %s" % (client.server_hostname,
                                              client.port, result.error),
              file=sys.stderr)

        return None

    return getattr(result, test_type, None)


def run():
    """ run the script """
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = "/config.yml"

    mqttc = mqtt.Client("Speedtest")

    (config, mqtt_config) = load_config(config_file, mqttc)

    while True:
        run_tests(config, mqtt_config, mqttc)
        time.sleep(config.get("interval", 3600))


def load_config(config_file, mqttc):
    """ load config from file and interpret values """
    try:
        config = yaml.load(open(config_file), Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print("Config not found. Using default values.", file=sys.stderr)
        config = {
            "interval": "90m",
            "hosts": [
                {
                    "hostname": "ping.online.net",
                    "ports": [
                        5200,
                        5201,
                        5202,
                    ]
                }
            ],
            "mqtt": {
                "host": "127.0.0.1",
                "port": "1883",
                "username": "",
                "password": "",
            }
        }

    config["interval"] = parse(config.get("interval", "60m"))
    mqtt_config = config.get("mqtt", {"username": "", "password": ""})
    print("Using MQTT-Server %s:%s" % (mqtt_config.get("host", "127.0.0.1"),
                                       mqtt_config.get("port", 1883)),
          file=sys.stderr)
    mqttc.username_pw_set(mqtt_config.get("username", ""),
                          mqtt_config.get("password", ""))

    return (config, mqtt_config)


run()
