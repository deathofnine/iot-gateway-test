# IoT Gateway Device Test Project

## 项目说明

针对 [iot-gateway-device](https://github.com/deathofnine/iot-gateway-device) 的自动化测试项目，实现传感器采集、远程控制、云平台对接的完整测试。

## 功能特性

- **RPC 功能测试**: 测试 LED 控制和 DHT11 温湿度读取
- **MQTT 集成测试**: 测试华为云 IoT 平台指令下发
- **pytest 测试框架**: 简洁高效的 Python 测试
- **YAML 配置管理**: 集中管理配置，便于维护

## 环境要求

- Python 3.7+
- 需要连接 i.MX6ULL 开发板
- 需要网络连接华为云 IoT 平台

## 安装依赖

```bash
cd 03_接口自动化
pip install -r requirements.txt
```

## 运行测试

```bash
# 进入测试目录
cd 03_接口自动化

# 运行所有测试
pytest

# 运行 RPC 测试
pytest tests/test_rpc.py -v

# 运行 MQTT 测试
pytest tests/test_mqtt.py -v

# 显示打印输出
pytest tests/test_rpc.py -v -s

# 运行特定标记的测试
pytest -m rpc -v
pytest -m mqtt -v
pytest -m "not slow" -v
```

## 项目结构

```
iot_test_project/
├── 01_测试文档/
│   ├── 测试计划.md      # 测试计划文档
│   ├── 测试用例.md      # 测试用例详细说明
│   └── 缺陷报告.md      # 缺陷报告模板
├── 02_手工测试/
│   └── 手工测试记录.md   # 手工测试记录模板
├── 03_接口自动化/
│   ├── tests/
│   │   ├── test_rpc.py  # RPC 功能测试
│   │   └── test_mqtt.py # MQTT 集成测试
│   ├── libs/
│   │   └── rpc_client.py # RPC 客户端封装
│   ├── pytest.ini        # pytest 配置
│   └── requirements.txt  # Python 依赖
├── 04_配置/
│   └── config.yaml       # 配置文件（MQTT/开发板配置）
└── README.md
```

## 配置说明

配置文件位于 `04_配置/config.yaml`，包含：

- **RPC**: 开发板 IP 地址和端口
- **MQTT**: 华为云 IoT 平台连接参数
- **Device**: 设备硬件配置
- **Test**: 测试参数（重试次数、延迟等）

## 测试用例说明

### test_rpc.py

| 用例 | 说明 | 验证点 |
|------|------|--------|
| test_dht11_read | 验证 DHT11 温湿度读取 | 返回值非空，温度0-50°C，湿度0-100% |
| test_led_control_on | 验证开灯功能 | RPC返回0 |
| test_led_control_off | 验证关灯功能 | RPC返回0 |
| test_led_control_twice | 验证连续开关 | 连续3次开关均成功 |

### test_mqtt.py

| 用例 | 说明 | 验证点 |
|------|------|--------|
| test_mqtt_led_on | MQTT下发开灯指令 | 云端指令执行成功 |
| test_mqtt_led_off | MQTT下发关灯指令 | 云端指令执行成功 |
| test_mqtt_led_toggle | MQTT连续控制LED | 3轮连续控制均成功 |

## 测试标记

使用 pytest markers 区分测试类型：

- `@pytest.mark.rpc` - RPC 相关测试
- `@pytest.mark.mqtt` - MQTT 相关测试
- `@pytest.mark.slow` - 耗时较长的测试

## 注意事项

- 测试 MQTT 功能需要有效的华为云设备凭证（配置在 config.yaml）
- 测试 RPC 功能需要开发板在线
- 建议先运行 RPC 测试，再运行 MQTT 测试
- 配置文件中的敏感信息请妥善保管