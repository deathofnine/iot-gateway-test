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
        #路径拼接，找到配置文件
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            '04_配置', 'config.yaml'
        )
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) #转换为字典然后返回


#----------------------------------
# 作用：通用 RPC 请求发起函数，封装 TCP 通信 + JSON-RPC 报文组装，统一调用后端服务任意接口
# 返回值：RPC 数据包里面 result所对应结果
#参数含义：
# method：要调用的后端接口名，params：接口需要传的参数列表
#-----------------------------------
    def call(self, method, params=None):
        if params is None:
            params = []
       
        #JSON-RPC 请求报文
        request = {
            "method": method,
            "params": params,
            "id": "2"
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            #尝试连接
            sock.connect((self.host, self.port))
            sock.send(json.dumps(request).encode('utf-8'))
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            return response.get("result")
        except Exception as e:
            raise Exception(f"RPC call failed: {e}")
        finally:
            sock.close()

#----------------------------------
# 作用：调用 RPC 服务，读取 DHT11 温湿度传感器的数据，并整理数据
# 返回值：成功返回温湿度，失败返回空
#-----------------------------------
    def dht11_read(self):
        result = self.call("dht11_read", [0])
        if result and len(result) >= 2:
            return {"humi": result[0], "temp": result[1]}
        return None

#----------------------------------
# 作用：给云端 提供一个简单接口，用来远程控制 LED 灯的亮灭。
# 成功返回数值 0
#----------------------------------
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
