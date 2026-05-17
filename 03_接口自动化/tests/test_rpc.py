import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from libs.rpc_client import RPCClient

@pytest.fixture
def client():
    return RPCClient()

@pytest.mark.rpc
def test_dht11_read(client):
    """测试 DHT11 温湿度读取"""
    data = client.dht11_read()
    assert data is not None
    assert 0 <= data["temp"] <= 50
    assert 0 <= data["humi"] <= 100
    print(f"温度: {data['temp']}°C, 湿度: {data['humi']}%")

@pytest.mark.rpc
def test_led_control_on(client):
    """测试 LED 开灯"""
    result = client.led_control(1)
    assert result == 0
    print("开灯成功")

@pytest.mark.rpc
def test_led_control_off(client):
    """测试 LED 关灯"""
    result = client.led_control(0)
    assert result == 0
    print("关灯成功")

@pytest.mark.rpc
@pytest.mark.slow
def test_led_control_twice(client):
    """测试连续开关 LED"""
    for i in range(3):
        result_on = client.led_control(1)
        assert result_on == 0
        result_off = client.led_control(0)
        assert result_off == 0
    print("连续开关测试通过")
if __name__ == "__main__":
    print("=== 手动测试 RPC ===")
    
    client = RPCClient()
    
    print("\n>>> 测试 DHT11 温湿度读取")
    try:
        data = client.dht11_read()
        if data:
            print(f"✓ 成功 - 温度: {data['temp']}°C, 湿度: {data['humi']}%")
        else:
            print("✗ 失败 - 返回空数据")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print("\n>>> 测试 LED 控制")
    try:
        print("  开灯...")
        result = client.led_control(1)
        print(f"  RPC返回: {result}")
        if result == 0:
            print("  ✓ 开灯成功")
        else:
            print(f"  ✗ 开灯失败，返回值: {result}")
        
        time.sleep(1)
        
        print("  关灯...")
        result = client.led_control(0)
        print(f"  RPC返回: {result}")
        if result == 0:
            print("  ✓ 关灯成功")
        else:
            print(f"  ✗ 关灯失败，返回值: {result}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print("\n=== 测试完成 ===")
