import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import json
import yaml
import paho.mqtt.client as mqtt
from libs.rpc_client import RPCClient

def load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        '04_配置', 'config.yaml'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

class MQTTCloudSimulator:
    def __init__(self):
        self.client = None
        self.received_responses = []

    def connect(self):
        self.client = mqtt.Client(client_id=config['mqtt']['client_id'])
        self.client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        print(f"连接到: {config['mqtt']['broker']}:{config['mqtt']['port']}")
        self.client.connect(config['mqtt']['broker'], config['mqtt']['port'])
        self.client.loop_start()
        time.sleep(2)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 连接成功")
        else:
            print(f"MQTT 连接失败，错误码: {rc}")

    def _on_message(self, client, userdata, msg):
        print(f"收到设备响应: {msg.topic} -> {msg.payload.decode()}")
        self.received_responses.append({
            "topic": msg.topic,
            "payload": msg.payload.decode()
        })

    def send_led_command(self, status, request_id="test123"):
        topic = f"$oc/devices/{config['mqtt']['device_id']}/sys/commands/request_id={request_id}"
        payload = json.dumps({
            "paras": {
                "status": status
            }
        })
        print(f"下发指令: {topic}")
        print(f"内容: {payload}")
        self.client.publish(topic, payload)
        time.sleep(config['test']['delay_seconds'])

    def get_last_response(self):
        if self.received_responses:
            return self.received_responses[-1]
        return None

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


@pytest.fixture(scope="module")
def cloud():
    c = MQTTCloudSimulator()
    c.connect()
    yield c
    c.disconnect()


@pytest.fixture
def rpc():
    return RPCClient()


@pytest.mark.mqtt
def test_mqtt_led_on(cloud, rpc):
    """通过 MQTT 测试开灯"""
    print("\n=== MQTT 测试: 开灯 ===")

    rpc.led_control(0)
    time.sleep(config['test']['delay_seconds'])

    cloud.send_led_command("ON", "test_led_on")
    time.sleep(1)

    result = rpc.led_control(1)
    assert result == 0
    print("✓ MQTT 开灯指令成功")


@pytest.mark.mqtt
def test_mqtt_led_off(cloud, rpc):
    """通过 MQTT 测试关灯"""
    print("\n=== MQTT 测试: 关灯 ===")

    rpc.led_control(1)
    time.sleep(config['test']['delay_seconds'])

    cloud.send_led_command("OFF", "test_led_off")
    time.sleep(1)

    result = rpc.led_control(0)
    assert result == 0
    print("✓ MQTT 关灯指令成功")


@pytest.mark.mqtt
@pytest.mark.slow
def test_mqtt_led_toggle(cloud, rpc):
    """通过 MQTT 连续开关 LED"""
    print("\n=== MQTT 测试: 连续开关 ===")

    for i in range(3):
        print(f"\n--- 第 {i+1} 轮 ---")

        cloud.send_led_command("ON", f"toggle_on_{i}")
        time.sleep(config['test']['delay_seconds'])
        assert rpc.led_control(1) == 0
        print(f"  ✓ 第 {i+1} 轮开灯成功")

        cloud.send_led_command("OFF", f"toggle_off_{i}")
        time.sleep(config['test']['delay_seconds'])
        assert rpc.led_control(0) == 0
        print(f"  ✓ 第 {i+1} 轮关灯成功")

    print("\n✓ MQTT 连续开关测试通过")


if __name__ == "__main__":
    print("=== 手动测试 MQTT ===")

    cloud = MQTTCloudSimulator()
    cloud.connect()

    rpc = RPCClient()

    print("\n>>> 测试开灯")
    cloud.send_led_command("ON", "manual_on")
    time.sleep(1)
    rpc.led_control(1)

    print("\n>>> 测试关灯")
    cloud.send_led_command("OFF", "manual_off")
    time.sleep(1)
    rpc.led_control(0)

    cloud.disconnect()
    print("\n=== 手动测试完成 ===")