---
name: cdcu-mcu-requirements
description: 将原始需求转换为CDCU MCU系统需求。当用户需要处理CSV文件或图片中的"需求描述"并生成标准化的CDCU MCU嵌入式系统"系统需求"时使用此技能。触发场景包括：CDCU MCU的CSV/图片需求处理、从需求图片中OCR文字提取、嵌入式系统需求标准化、AUTOSAR架构需求、CAN/LIN/UART/GPIO信号处理需求。
---

# CDCU MCU 需求转换 - 执行手册

本技能负责**输入处理、工具调用和文件 I/O**的标准流程。  
领域判断规则（MCU 能力建模、需求识别过滤、逻辑标准化、结构化需求生成格式）统一由 Agent 负责，本技能不重复定义。

---

## 所需工具

| 工具 | 用途 |
|------|------|
| **xlsx** | 读写 CSV 文件 |
| **paddleocr-doc-parsing** | 图片 OCR 文字提取 |

---

## 输入处理流程

### 选项 A：CSV 文件输入

```
用户提供 CSV 文件路径
    → 在 workspace/requirements/ 下创建带时间戳的子目录（如 20260409_173100/）
    → 使用 xlsx 读取文件，获取「需求描述」列
    → 对每行调用 Agent 的功能1→2→3→4，完成需求转换
    → 使用 xlsx 将转换结果写入「系统需求」列，保存到该子目录
    → 输出：子目录内「系统需求」列已填充的 CSV 文件
```

### 选项 B：图片输入

```
用户提供图片（PNG / JPG 等）
    → 在 workspace/requirements/ 下创建带时间戳的子目录（如 20260409_173100/）
    → 使用 paddleocr-doc-parsing 提取文字
    → 将 OCR 原始文字保存为 requirements_input.csv 到该子目录
          列：「需求描述」（禁止任何修改）
    → 读取子目录中的 requirements_input.csv，对每行调用 Agent 的功能1→2→3→4
    → 生成 requirements_output.csv 到该子目录：
          列1：需求描述（直接复制自 input.csv，不得修改）
          列2：系统需求（Agent 转换结果）
```

---

## 数据完整性规则

| 检查项 | 要求 |
|--------|------|
| 行数 | 输入与输出行数严格一致，顺序不变 |
| 需求描述列 | 绝不修改 OCR 原始内容 |
| 系统需求列 | 仅由 Agent 转换后填充，不允许手动编辑 |
| 列对应关系 | 同一行的描述和需求必须对应同一条原始输入 |

### 常见错误预防

- ❌ 将系统需求内容覆盖到需求描述列
- ❌ 丢失或修改 OCR 识别的原始文字
- ❌ 输入输出行数不一致或顺序错乱
- ✅ 保留原始需求描述，仅填充系统需求列

---

## 输出目录规则

每次任务执行时，必须在 workspace 下创建独立子目录：

```
workspace/
└── requirements/
    └── {YYYYMMDD_HHMMSS}/   ← 每次任务新建，时间戳精确到秒
        ├── requirements_input.csv   （图片输入时有）
        └── requirements_output.csv
```

**规则：**
- 子目录名称使用 `YYYYMMDD_HHMMSS` 格式（如 `20260409_173100`）
- 任务的所有中间文件和最终结果都写入该子目录
- 不允许在 workspace 根目录或 requirements/ 目录下直接存放 CSV 文件
