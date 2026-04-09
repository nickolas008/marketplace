#!/usr/bin/env python3
"""
CDCU MCU Requirements Processor
Converts raw requirements to standardized CDCU MCU system requirements
Supports both CSV files and image inputs (via OCR)
"""

import re
import pandas as pd
from typing import List, Dict, Optional, Tuple


class CDCURequirementProcessor:
    """Process and standardize CDCU MCU requirements"""

    def __init__(self):
        # MCU direct attribution keywords
        self.mcu_direct_keywords = [
            'CDCU MCU', 'signal', '信号', 'CAN', 'LIN', 'UART', 'GPIO',
            'ETH', 'Ethernet', '以太网', 'send', '发送', 'receive', '接收',
            'forward', '透传', '转发', 'MCU', '控制器', 'controller',
            'ICAN', 'TPCAN', 'BCAN', 'ECAN', 'CCAN', 'DCAN', 'LPCAN',
            'CLIN1', 'CLIN2', 'CLIN3', 'CLIN4', 'CLIN5'
        ]

        # SOC/UI keywords
        self.soc_keywords = [
            'display', '显示', 'screen', '屏幕', 'UI', '界面', 'HMI',
            'user', '用户', 'touch', '触摸', 'SOC', '大屏', '界面点击',
            '设置项选择', '屏幕操作'
        ]

        # Communication channels
        self.can_channels = ['ICAN', 'TPCAN', 'BCAN', 'ECAN', 'CCAN', 'DCAN', 'LPCAN']
        self.lin_channels = ['CLIN1', 'CLIN2', 'CLIN3', 'CLIN4', 'CLIN5']

    def is_mcu_relevant(self, requirement: str) -> bool:
        """
        Determine if requirement is relevant to CDCU MCU using priority rules

        Args:
            requirement: Raw requirement text

        Returns:
            bool: True if MCU relevant
        """
        if not requirement:
            return False

        req_lower = requirement.lower()

        # Rule 1: Direct MCU Attribution
        if 'cdcu mcu' in req_lower or 'mcu' in req_lower:
            return True

        # Check for MCU-specific operations
        for keyword in self.mcu_direct_keywords:
            if keyword.lower() in req_lower:
                return True

        # Rule 2: Logic Attribution Judgment
        # If precondition is user/display operation, MCU only sends signals
        user_operations = ['用户操作', '屏幕操作', 'HMI操作', '大屏操作', '界面点击', '设置项选择']
        has_user_operation = any(op in requirement for op in user_operations)

        if has_user_operation and any(word in requirement for word in ['发送', '信号']):
            return True  # MCU handles signal sending even with user precondition

        # Rule 3: CDCU Ambiguous Reference
        if 'cdcu' in req_lower or 'CDCU' in requirement:
            # Communication/signal/control → MCU
            if any(word in req_lower for word in ['通信', 'communication', '信号', 'signal', '控制', 'control']):
                return True
            # UI/display/interaction → SOC (exclude)
            if any(word in req_lower for word in ['ui', 'display', '显示', '交互', 'interaction']):
                return False
            # Default signal operations to MCU
            if any(word in requirement for word in ['发送', 'send', '接收', 'receive']):
                return True

        # Check for explicit SOC mention without MCU
        if ('soc' in req_lower or '大屏' in requirement) and 'mcu' not in req_lower:
            if not any(word in requirement for word in ['发送', '信号']):
                return False

        return False

    def format_multiple_conditions(self, conditions: str) -> str:
        """
        Format multiple conditions with numbering and logical operators

        Args:
            conditions: Raw conditions text

        Returns:
            Formatted conditions
        """
        # Replace Chinese logical operators
        conditions = conditions.replace('且', ' && ').replace('或', ' || ')
        conditions = conditions.replace('并且', ' && ').replace('或者', ' || ')

        # Split by common delimiters
        parts = re.split(r'[,，、]|\s+&&\s+|\s+\|\|\s+', conditions)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) > 1:
            # Number the conditions
            numbered = []
            for i, part in enumerate(parts, 1):
                # Check if there's a logical operator after this part
                if '&&' in conditions or '且' in conditions:
                    if i < len(parts):
                        numbered.append(f"{i}. {part}")
                    else:
                        numbered.append(f"{i}. {part}")
                else:
                    numbered.append(f"{i}. {part}")

            # Determine the operator
            if '||' in conditions or '或' in conditions:
                return ' || '.join(numbered)
            else:
                return ' && '.join(numbered)

        return conditions

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

    def split_requirements(self, requirement: str) -> List[Tuple[str, str]]:
        """
        Split requirement if it contains multiple independent events

        Args:
            requirement: Raw requirement text

        Returns:
            List of tuples (requirement_name, requirement_text)
        """
        requirements = []

        # Check for multiple signal sendings
        signal_patterns = ['发送(.+?)信号', '发送(.+?)到', '输出(.+?)']
        signals = []
        for pattern in signal_patterns:
            signals.extend(re.findall(pattern, requirement))

        # Check for multiple independent actions
        if '同时' in requirement or '并且' in requirement:
            # Split by these keywords
            parts = re.split(r'[,，;；]|同时|并且', requirement)
            if len(parts) > 1:
                for i, part in enumerate(parts, 1):
                    if part.strip():
                        # Extract a brief summary for the requirement name
                        summary = self.extract_summary(part)
                        requirements.append((f"需求{i} {summary}", part.strip()))
                return requirements

        # If no splitting needed, return as single requirement
        summary = self.extract_summary(requirement)
        return [(f"需求1 {summary}", requirement)]

    def extract_summary(self, text: str) -> str:
        """
        Extract a brief summary from requirement text

        Args:
            text: Requirement text

        Returns:
            Brief summary
        """
        # Try to extract signal name or main action
        if '发送' in text:
            match = re.search(r'发送(.{1,10}?)(?:信号|到|给)', text)
            if match:
                return match.group(1).strip() + "信号"
        elif 'GPIO' in text:
            return "GPIO控制"
        elif 'CAN' in text or 'LIN' in text:
            return "通信控制"
        else:
            # Take first few characters as summary
            return text[:10] if len(text) > 10 else text

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

        # Split into multiple requirements if needed
        req_list = self.split_requirements(requirement)
        results = []

        for req_name, req_text in req_list:
            processed = self.process_single_requirement(req_name, req_text)
            if processed:
                results.append(processed)

        return '\n'.join(results) if results else None

    def process_single_requirement(self, req_name: str, requirement: str) -> str:
        """
        Process a single requirement into standardized format

        Args:
            req_name: Requirement name/number
            requirement: Requirement text

        Returns:
            Standardized requirement string
        """
        # Initialize all fields
        fields = {
            '前置条件 / Precondition': '未定义',
            '触发条件 / Trigger condition': '未定义',
            '执行输出 / Execution output': '未定义',
            '退出条件 / Exit condition': '未定义',
            '异常事件 / Exception event': '未定义'
        }

        # Extract preconditions - check for user operations
        user_operations = ['用户按下', '用户操作', '用户选择', '屏幕操作', 'HMI操作', '大屏操作']
        for op in user_operations:
            if op in requirement:
                # Extract the user operation as precondition
                match = re.search(f'{op}(.{{1,20}}?)(?:时|，|,|且)', requirement)
                if match:
                    fields['前置条件 / Precondition'] = op + match.group(1)
                    break

        # Check for explicit precondition
        if fields['前置条件 / Precondition'] == '未定义':
            if '前置' in requirement or 'precondition' in requirement.lower():
                pattern = r'前置条件?[:：]?\s*(.+?)(?:[,，]|$)'
                fields['前置条件 / Precondition'] = self.extract_conditions(requirement, pattern)

        # Extract trigger conditions with logical operators
        trigger_patterns = [
            r'当(.+?)时',
            r'when\s+(.+?)\s*,',
            r'如果(.+?)则',
            r'if\s+(.+?)\s+then',
            r'检测到(.+?)时'
        ]
        for pattern in trigger_patterns:
            match = re.search(pattern, requirement, re.IGNORECASE)
            if match:
                trigger = match.group(1).strip()
                # Process multiple conditions
                trigger = self.format_multiple_conditions(trigger)
                fields['触发条件 / Trigger condition'] = trigger
                break

        # Extract execution output
        output_patterns = [
            r'(?:则|就|执行|发送|输出)(.+?)(?:[。，,]|$)',
            r'(?:send|execute|output)\s+(.+?)(?:[.,]|$)',
            r'MCU(.+?)(?:[。，,]|$)'
        ]
        for pattern in output_patterns:
            match = re.search(pattern, requirement, re.IGNORECASE)
            if match:
                output = match.group(1).strip()
                # Preserve signal names and communication methods
                if any(chan in output for chan in self.can_channels + self.lin_channels):
                    fields['执行输出 / Execution output'] = output
                else:
                    fields['执行输出 / Execution output'] = output
                break

        # Extract signal information
        signal_info = self.extract_signal_info(requirement)

        # Build standardized requirement with requirement name header
        result_lines = [f"【{req_name}】", ""]  # Add requirement header

        # Add all fields
        for key, value in fields.items():
            result_lines.append(f"{key}: {value}")

        # Update signal info keys to match new format
        signal_info_formatted = {
            '发送信号 / Send signal': signal_info.get('发送信号', '未定义'),
            '发送方式 / Send method': signal_info.get('发送方式', '未定义'),
            '发送时长 / Send time': signal_info.get('发送时长', '未定义'),
            '发送后动作 / After-send operation': signal_info.get('发送后动作', '未定义'),
            '返回信号 / Response signal': signal_info.get('返回信号', '未定义')
        }

        for key, value in signal_info_formatted.items():
            result_lines.append(f"{key}: {value}")

        result_lines.append("")  # Empty line after each requirement

        return "\n".join(result_lines)

    def process_text_to_csv(self, text: str, output_file: str) -> None:
        """
        Process text (from OCR or other source) and save to CSV

        Args:
            text: Raw text containing requirements
            output_file: Output CSV path
        """
        # Split text into lines and identify requirements
        lines = text.split('\n')
        requirements = []

        for line in lines:
            line = line.strip()
            if line and self.is_mcu_relevant(line):
                requirements.append(line)

        # Create DataFrame
        df = pd.DataFrame({
            '需求描述': requirements,
            '系统需求': [''] * len(requirements)
        })

        # Process each requirement
        for idx, requirement in enumerate(requirements):
            processed = self.process_requirement(requirement)
            if processed:
                df.at[idx, '系统需求'] = processed
            else:
                df.at[idx, '系统需求'] = '非CDCU MCU相关需求'

        # Save output
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Processed requirements from text saved to: {output_file}")

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