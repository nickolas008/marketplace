---
name: cdcu-mcu-requirements
description: Convert raw requirements to CDCU MCU system requirements. Use this skill whenever users need to process requirement CSV files containing "需求描述" field to generate standardized "系统需求" for CDCU MCU embedded systems. Triggers include: CSV requirements processing for CDCU MCU, embedded system requirement standardization, AUTOSAR architecture requirements, CAN/LIN/UART signal processing requirements, converting informal requirements to formal system specifications.
---

# CDCU MCU Requirements Converter

This skill processes raw requirements and converts them into standardized CDCU MCU system requirements following embedded system engineering best practices.

## Overview

CDCU MCU (Center Domain Controller Unit Micro Control Unit) is responsible for:
- Logic processing
- Signal sending/receiving/forwarding
- Communication via multiple protocols (CAN, LIN, UART, Ethernet, GPIO)

The MCU software uses standard AUTOSAR architecture with the following capabilities:
- **CAN Communication**: 7 CAN channels (ICAN, TPCAN, BCAN, ECAN, CCAN, DCAN, LPCAN)
- **LIN Communication**: 5 LIN channels as master (CLIN1-5)
- **UART Communication**: Communication with display (CDCU SOC) via carservice interface
- **Ethernet Communication**: Via internal Switch to other domain controllers
- **GPIO Interface**: External signal reception and control execution
- **Logic Processing**: Process received signals and send results

## Workflow

### Step 1: Load and Process Input CSV

Use the xlsx skill to read the input CSV file containing:
- `需求描述` (requirement_description) column
- `系统需求` (system_requirement) column (to be filled)

### Step 2: Process Each Requirement

For each requirement in the `需求描述` column:

1. **Filter by Relevance**
   - Extract only CDCU MCU-related requirements
   - When "CDCU" is mentioned without specifying MCU/SOC, analyze context:
     - Signal sending/receiving → CDCU MCU scope
     - User/display operations → CDCU SOC scope

2. **Analyze Preconditions**
   - If precondition is user/display operation → logic in SOC, MCU only sends signals
   - If signal judgment needed without explicit SOC assignment → MCU logic

3. **Apply Standardized Format**

Generate system requirements with these mandatory fields:

```
前置条件/ Precondition: [Extract or "未定义"]
触发条件/ Trigger condition: [Extract or "未定义"]
执行输出/ Execution output: [Extract or "未定义"]
退出条件/ Exit condition: [Extract or "未定义"]
异常事件/ Exception event: [Extract or "未定义"]
发送信号: [Signal name or "未定义"]
发送方式: [周期发送/事件发送/触发发送 or "未定义"]
发送时长: [Duration in ms/frames or "未定义"]
发送后动作: [Post-send action or "未定义"]
返回信号: [Return signal or "未定义"]

[Empty line after each requirement]
```

### Step 3: Formatting Rules

1. **Multiple Conditions**: List as 1, 2, 3, 4...
2. **Logical Operators**: Use && (AND), || (OR)
3. **Undefined Fields**: Fill with "未定义"
4. **Multiple Independent Events**: Create separate requirements

### Step 4: Generate Output CSV

Use the xlsx skill to:
1. Create a new CSV with all original columns
2. Fill the `系统需求` column with generated requirements
3. Save the processed CSV file

## Implementation Steps

1. Read the input CSV file using xlsx skill
2. Create a list to store processed requirements
3. For each row:
   - Extract the `需求描述` content
   - Apply filtering and analysis rules
   - Generate standardized system requirement
   - Store in the corresponding `系统需求` field
4. Write the complete CSV with filled requirements
5. Return the file path to the user

## Example Transformation

**Input (需求描述)**:
```
当用户按下启动按钮且车速为0时，CDCU MCU发送启动信号给动力系统
```

**Output (系统需求)**:
```
前置条件/ Precondition: 用户按下启动按钮
触发条件/ Trigger condition: 车速为0
执行输出/ Execution output: 发送启动信号给动力系统
退出条件/ Exit condition: 未定义
异常事件/ Exception event: 未定义
发送信号: 启动信号
发送方式: 触发发送
发送时长: 未定义
发送后动作: 未定义
返回信号: 未定义
```

## Important Notes

- Signal sending strategies are always within CDCU MCU scope
- Logic processing location depends on preconditions
- Each independent event generates a separate requirement
- Maintain consistency with AUTOSAR architecture standards
- Preserve all original CSV data while adding system requirements