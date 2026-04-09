# CDCU MCU Requirements Converter Skill

## 概述

此技能专门用于将原始需求描述转换为标准化的CDCU MCU（中央域控制器微控制单元）系统需求。支持从CSV文件和图片中提取需求，遵循AUTOSAR架构标准，自动识别和处理嵌入式系统相关需求。

## 功能特点

- 🎯 **智能识别**: 自动区分CDCU MCU和SOC的职责范围
- 📋 **标准化格式**: 生成包含10个标准字段的系统需求
- 🔄 **多源输入**: 支持CSV文件和图片（OCR）输入
- 🚗 **汽车电子专用**: 支持CAN、LIN、UART、以太网、GPIO等车载通信协议
- ✂️ **需求拆分**: 自动识别并拆分多个独立事件
- 🔍 **精准过滤**: 基于优先级规则准确判定MCU职责

## 使用方法

### 方式1: CSV文件处理

准备CSV文件，包含以下列：
- `需求描述`：原始需求文本
- `系统需求`：（可选）用于填充转换后的系统需求

```
用户: 请处理这个requirements.csv文件，将需求描述转换为CDCU MCU系统需求
```

### 方式2: 图片处理

上传包含需求文字的图片：

```
用户: 请从这张图片中提取需求并转换为CDCU MCU系统需求
```

技能会使用paddleocr-doc-parsing skill进行OCR文字识别，然后处理提取的需求。

### 3. 输出格式

每个系统需求包含以下10个标准字段：
- 前置条件 / Precondition
- 触发条件 / Trigger condition
- 执行输出 / Execution output
- 退出条件 / Exit condition
- 异常事件 / Exception event
- 发送信号 / Send signal
- 发送方式 / Send method
- 发送时长 / Send time
- 发送后动作 / After-send operation
- 返回信号 / Response signal

## 依赖

- **xlsx skill**：用于读写CSV/Excel文件
- **paddleocr-doc-parsing skill**：用于从图片中提取文字（OCR功能）
- **Python环境**：运行处理脚本

## 文件结构

```
cdcu-mcu-requirements/
├── SKILL.md              # 技能定义文件
├── README.md             # 使用说明
├── scripts/
│   └── process_requirements.py  # 处理脚本
```

## 相关Agent

配套的`cdcu-mcu-requirements-agent`提供了专门的嵌入式系统工程师视角，可以处理更复杂的需求分析任务。

## 注意事项

- 输入CSV必须使用UTF-8编码
- 需求描述应尽可能详细以提高转换准确性
- 非CDCU MCU相关需求会被标记但不会处理
- 建议人工审核生成的系统需求以确保准确性