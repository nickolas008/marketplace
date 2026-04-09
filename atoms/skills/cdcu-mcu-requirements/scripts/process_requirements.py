#!/usr/bin/env python3
"""
CDCU MCU Requirements Processor
Converts raw requirements to standardized CDCU MCU system requirements
"""

import re
import pandas as pd
from typing import List, Dict, Optional


class CDCURequirementProcessor:
    """Process and standardize CDCU MCU requirements"""

    def __init__(self):
        self.mcu_keywords = [
            'signal', '信号', 'CAN', 'LIN', 'UART', 'GPIO',
            'send', '发送', 'receive', '接收', 'forward', '透传',
            'MCU', '控制器', 'controller'
        ]

        self.soc_keywords = [
            'display', '显示', 'screen', '屏幕', 'UI', '界面',
            'user', '用户', 'touch', '触摸', 'SOC', '大屏'
        ]

    def is_mcu_relevant(self, requirement: str) -> bool:
        """
        Determine if requirement is relevant to CDCU MCU

        Args:
            requirement: Raw requirement text

        Returns:
            bool: True if MCU relevant
        """
        req_lower = requirement.lower()

        # Explicit MCU mention
        if 'mcu' in req_lower or 'cdcu mcu' in req_lower:
            return True

        # Explicit SOC mention without MCU
        if ('soc' in req_lower or '大屏' in requirement) and 'mcu' not in req_lower:
            return False

        # Check for MCU-specific operations
        mcu_score = sum(1 for keyword in self.mcu_keywords if keyword in req_lower)
        soc_score = sum(1 for keyword in self.soc_keywords if keyword in req_lower)

        # If CDCU mentioned without specification, check context
        if 'cdcu' in req_lower or 'CDCU' in requirement:
            # Signal operations default to MCU
            if any(word in req_lower for word in ['发送', 'send', '接收', 'receive', '信号', 'signal']):
                return True

        return mcu_score > soc_score

    def extract_conditions(self, text: str, pattern: str) -> str:
        """
        Extract conditions from requirement text

        Args:
            text: Requirement text
            pattern: Regex pattern to match conditions

        Returns:
            str: Extracted conditions or "未定义"
        """
        matches = re.findall(pattern, text, re.IGNORECASE)
        if not matches:
            return "未定义"

        conditions = []
        for i, match in enumerate(matches, 1):
            if len(matches) > 1:
                conditions.append(f"{i}. {match}")
            else:
                conditions.append(match)

        return " && ".join(conditions) if len(conditions) > 1 else conditions[0]

    def extract_signal_info(self, requirement: str) -> Dict[str, str]:
        """
        Extract signal-related information

        Args:
            requirement: Requirement text

        Returns:
            dict: Signal information
        """
        signal_info = {
            '发送信号': '未定义',
            '发送方式': '未定义',
            '发送时长': '未定义',
            '发送后动作': '未定义',
            '返回信号': '未定义'
        }

        # Extract signal name
        signal_patterns = [
            r'发送(.+?)(?:信号|到|给)',
            r'send\s+(\w+)\s+signal',
            r'(\w+)\s*信号'
        ]

        for pattern in signal_patterns:
            match = re.search(pattern, requirement, re.IGNORECASE)
            if match:
                signal_info['发送信号'] = match.group(1).strip()
                break

        # Determine sending method
        if any(word in requirement for word in ['周期', 'periodic', '定期']):
            signal_info['发送方式'] = '周期发送'
        elif any(word in requirement for word in ['事件', 'event', '触发']):
            signal_info['发送方式'] = '事件发送'
        elif '当' in requirement or 'when' in requirement.lower():
            signal_info['发送方式'] = '触发发送'

        # Extract duration
        duration_pattern = r'(\d+)\s*(ms|毫秒|帧|frame)'
        match = re.search(duration_pattern, requirement, re.IGNORECASE)
        if match:
            signal_info['发送时长'] = match.group(0)

        # Determine post-send action
        if '持续' in requirement or 'maintain' in requirement.lower():
            signal_info['发送后动作'] = '持续发有效值'
        elif '回0' in requirement or 'zero' in requirement.lower():
            signal_info['发送后动作'] = '发送后回0'
        elif '默认' in requirement or 'default' in requirement.lower():
            signal_info['发送后动作'] = '发送后恢复默认值'

        return signal_info

    def process_requirement(self, requirement: str) -> Optional[str]:
        """
        Process a single requirement into standardized format

        Args:
            requirement: Raw requirement text

        Returns:
            str: Standardized requirement or None if not MCU relevant
        """
        if not requirement or pd.isna(requirement):
            return None

        if not self.is_mcu_relevant(requirement):
            return None

        # Initialize all fields
        fields = {
            '前置条件/ Precondition': '未定义',
            '触发条件/ Trigger condition': '未定义',
            '执行输出/ Execution output': '未定义',
            '退出条件/ Exit condition': '未定义',
            '异常事件/ Exception event': '未定义'
        }

        # Extract preconditions
        if '前置' in requirement or 'precondition' in requirement.lower():
            pattern = r'前置条件?[:：]?\s*(.+?)(?:[,，]|$)'
            fields['前置条件/ Precondition'] = self.extract_conditions(requirement, pattern)

        # Extract trigger conditions
        trigger_patterns = [
            r'当(.+?)时',
            r'when\s+(.+?)\s*,',
            r'如果(.+?)则',
            r'if\s+(.+?)\s+then'
        ]
        for pattern in trigger_patterns:
            match = re.search(pattern, requirement, re.IGNORECASE)
            if match:
                fields['触发条件/ Trigger condition'] = match.group(1).strip()
                break

        # Extract execution output
        output_patterns = [
            r'(?:则|就|执行|发送|输出)(.+?)(?:[。，,]|$)',
            r'(?:send|execute|output)\s+(.+?)(?:[.,]|$)'
        ]
        for pattern in output_patterns:
            match = re.search(pattern, requirement, re.IGNORECASE)
            if match:
                fields['执行输出/ Execution output'] = match.group(1).strip()
                break

        # Extract signal information
        signal_info = self.extract_signal_info(requirement)

        # Build standardized requirement
        result_lines = []
        for key, value in fields.items():
            result_lines.append(f"{key}: {value}")

        for key, value in signal_info.items():
            result_lines.append(f"{key}: {value}")

        result_lines.append("")  # Empty line after each requirement

        return "\n".join(result_lines)

    def process_csv(self, input_file: str, output_file: str) -> None:
        """
        Process entire CSV file

        Args:
            input_file: Input CSV path
            output_file: Output CSV path
        """
        # Read CSV
        df = pd.read_csv(input_file, encoding='utf-8-sig')

        # Find requirement description column
        desc_col = None
        for col in df.columns:
            if '需求描述' in col or 'requirement_description' in col.lower():
                desc_col = col
                break

        if not desc_col:
            raise ValueError("Cannot find requirement description column")

        # Ensure system requirement column exists
        sys_req_col = '系统需求'
        if sys_req_col not in df.columns:
            df[sys_req_col] = ''

        # Process each requirement
        for idx, row in df.iterrows():
            requirement = row[desc_col]
            processed = self.process_requirement(requirement)
            if processed:
                df.at[idx, sys_req_col] = processed
            else:
                df.at[idx, sys_req_col] = '非CDCU MCU相关需求'

        # Save output
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Processed requirements saved to: {output_file}")


def main():
    """Main entry point for standalone execution"""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python process_requirements.py <input_csv> <output_csv>")
        sys.exit(1)

    processor = CDCURequirementProcessor()
    processor.process_csv(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()