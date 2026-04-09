# CDCU MCU Requirements Converter Skill

## 概述

此技能专门用于将原始需求描述转换为标准化的CDCU MCU（中央域控制器微控制单元）系统需求。它遵循AUTOSAR架构标准，自动识别和处理嵌入式系统相关需求。

## 功能特点

- 🎯 **智能识别**: 自动区分CDCU MCU和SOC的职责范围
- 📋 **标准化格式**: 生成包含10个标准字段的系统需求
- 🔄 **批量处理**: 支持CSV文件批量转换
- 🚗 **汽车电子专用**: 支持CAN、LIN、UART、以太网等车载通信协议

## 使用方法

### 1. 准备输入文件

创建CSV文件，包含以下列：
- `需求描述`：原始需求文本
- `系统需求`：（可选）用于填充转换后的系统需求

### 2. 调用技能

```
用户: 请处理这个requirements.csv文件，将需求描述转换为CDCU MCU系统需求
```

### 3. 输出格式

每个系统需求包含以下标准字段：
- 前置条件/ Precondition
- 触发条件/ Trigger condition
- 执行输出/ Execution output
- 退出条件/ Exit condition
- 异常事件/ Exception event
- 发送信号
- 发送方式
- 发送时长
- 发送后动作
- 返回信号

## 示例

### 输入需求
```
当车速大于20km/h且用户按下ACC按钮时，CDCU MCU发送ACC激活信号到动力控制器
```

### 输出系统需求
```
前置条件/ Precondition: 用户按下ACC按钮
触发条件/ Trigger condition: 车速>20km/h
执行输出/ Execution output: 发送ACC激活信号到动力控制器
退出条件/ Exit condition: 未定义
异常事件/ Exception event: 未定义
发送信号: ACC激活信号
发送方式: 触发发送
发送时长: 未定义
发送后动作: 未定义
返回信号: 未定义
```

## 处理规则

1. **MCU业务范围判定**
   - 信号发送/接收 → MCU范围
   - 用户界面操作 → SOC范围
   - 逻辑处理 → 根据前置条件判定

2. **多条件处理**
   - 使用编号列表：1、2、3、4
   - 逻辑运算符：&&（与）、||（或）

3. **独立事件**
   - 每个独立事件生成单独的系统需求

## 依赖

- xlsx skill：用于读写CSV/Excel文件
- Python环境：运行处理脚本

## 文件结构

```
cdcu-mcu-requirements/
├── SKILL.md              # 技能定义文件
├── README.md             # 使用说明
├── scripts/
│   └── process_requirements.py  # 处理脚本
├── examples/
│   └── sample_requirements.csv  # 示例文件
└── evals/
    └── evals.json        # 测试用例
```

## 相关Agent

配套的`cdcu-mcu-requirements-agent`提供了专门的嵌入式系统工程师视角，可以处理更复杂的需求分析任务。

## 注意事项

- 输入CSV必须使用UTF-8编码
- 需求描述应尽可能详细以提高转换准确性
- 非CDCU MCU相关需求会被标记但不会处理
- 建议人工审核生成的系统需求以确保准确性