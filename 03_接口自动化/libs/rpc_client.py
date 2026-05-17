#!/usr/bin/env python3
import socket
import json
import time
import yaml
import os

class RPCClient:
    def __init__(self, host=None, port=None):
        config = self._load_config()
        self.host = host or config['rpc']['host']
        self.port = port or config['rpc']['port']
        self.timeout = config['rpc']['timeout']

    def _load_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            '04_配置', 'config.yaml'
        )
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def call(self, method, params=None):
        if params is None:
            params = []

        request = {
            "method": method,
            "params": params,
            "id": "2"
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        try:
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode('utf-8'))
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            return response.get("result")
        except Exception as e:
            raise Exception(f"RPC call failed: {e}")
        finally:
            sock.close()

    def dht11_read(self):
        result = self.call("dht11_read", [0])
        if result and len(result) >= 2:
            return {"humi": result[0], "temp": result[1]}
        return None

    def led_control(self, on):
        result = self.call("led_control", [on])
        return result


if __name__ == "__main__":
    client = RPCClient()

    print("测试读温湿度...")
    try:
        data = client.dht11_read()
        if data:
            print(f"温度: {data['temp']}°C, 湿度: {data['humi']}%")
        else:
            print("读取失败")
    except Exception as e:
        print(f"错误: {e}")

    print("\n测试 LED 控制...")
    try:
        result = client.led_control(1)
        print(f"开灯结果: {result}")
        time.sleep(1)
        result = client.led_control(0)
        print(f"关灯结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
