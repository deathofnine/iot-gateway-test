#!/usr/bin/env python3
# rpc_client.py
import socket
import json
import time

class RPCClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def call(self, method, params=None):
        """
        调用 JSON-RPC 接口
        :param method: 方法名，如 "dht11_read"
        :param params: 参数列表，如 [0] 或 [1]
        :return: 服务端返回的 result
        """
        if params is None:
            params = []

        # 构造 JSON-RPC 请求（格式与你 C 代码一致）
        request = {
            "method": method,
            "params": params,
            "id": "2"
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode('utf-8'))

            # 接收响应
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)

            # 返回 result 部分
            return response.get("result")
        except Exception as e:
            raise Exception(f"RPC call failed: {e}")
        finally:
            sock.close()

    def dht11_read(self):
        """读取温湿度"""
        result = self.call("dht11_read", [0])
        if result and len(result) >= 2:
            return {"humi": result[0], "temp": result[1]}
        return None

    def led_control(self, on):
        """控制 LED
        :param on: 1 开，0 关
        """
        result = self.call("led_control", [on])
        return result


if __name__ == "__main__":
    client = RPCClient("192.168.137.114", 1234)

    # 测试读取 DHT11
    print("测试读温湿度...")
    try:
        data = client.dht11_read()
        if data:
            print(f"温度: {data['temp']}°C, 湿度: {data['humi']}%")
        else:
            print("读取失败")
    except Exception as e:
        print(f"错误: {e}")

    # 测试 LED 控制
    print("\n测试 LED 控制...")
    try:
        # 开灯
        result = client.led_control(1)
        print(f"开灯结果: {result}")
        time.sleep(1)

        # 关灯
        result = client.led_control(0)
        print(f"关灯结果: {result}")
    except Exception as e:
        print(f"错误: {e}")