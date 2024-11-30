import re
import os
import sys
import random
import time


# 避免需要在不同的環境中更改路徑
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Enforcer:
    def __init__(self):
        try:
            print("Normalization Enforcer is ready.")
        except Exception as e:
            print(e)

    '''通用函數，用於嚴格檢查格式是否符合要求'''

    # Intent: 用來嚴格檢查格式是否符合要求
    # Input: 一個函數（生成結果），一個格式檢查函數，以及所需的所有參數
    # Output: 一個符合格式要求的結果
    # Note: 若格式不符合要求，則會持續要求重新輸入，直到格式符合要求或嘗試次數超過8次
    def strictlyFollowFormat(self, inputFunction, validationFunction, *args, **kwargs):
        flag = False  # 設定一個標誌，用來判斷是否已經通過格式檢查
        timesCount = 0  # 計數器，用來記錄嘗試次數

        while not flag:  # 當格式尚未通過檢查時，持續迴圈
            result = inputFunction(*args, **kwargs)  # 呼叫傳入的生成結果函數並取得結果

            # 使用傳入的檢查函數來檢查格式是否有效
            if validationFunction(result):
                flag = True  # 若格式有效，將標誌設為 True 結束迴圈
            else:
                timesCount += 1  # 格式無效時，計數器加1
                if timesCount > 8:  # 若嘗試次數超過8次，強制結束迴圈
                    flag = True

        return result  # 返回最終結果（無論格式是否有效）

    '''個別格式檢查函數'''

    # 檢查WorkSheet是否有效
    def is_valid_worksheet_format(self, input_string):
        # Format: Worksheet
        '''Worksheet
        Main problem: Create a program that can move a player around using console

        Member message: Help me create a class to represent the player and define its properties (position, direction, etc.)
        Member message: Help me write functions to handle player movement (up, down, left, right) and update the player's position accordingly
        Member message: Help me implement a function to display the player's current position on the console
        Member message: Help me write functions to handle player movement (up, down, left, right) and update the player's position accordingly
        '''

        # 將輸入按行分割，並移除每行的前後空白字符，過濾掉空行
        lines = [line.strip() for line in input_string.strip().split('\n') if line.strip()]

        # 檢查開頭和 Main problem 部分
        if not re.match(r'^\s*Worksheet\s*$', lines[0]):  # 忽略開頭空格
            return False
        if not re.match(r'^\s*Main problem:\s*', lines[1]):  # 忽略 Main problem 後的空格
            return False

        # 檢查中間的 Member message: 是否正確，忽略空格
        for line in lines[2:]:
            if not re.match(
                r'^\s*Member message:\s*Help me\s+', line
            ):  # 忽略 Member message: 和 Help me 之間的空格
                return False

        return True  # 所有檢查通過，返回 True

    # Check if GenerateOutput Result is valid
    def is_valid_generate_output_format(self, input_string):
        # Format: GenerateOutput
        '''
        Main target:
        (Always describe the primary problem or task clearly here.)

        Language use:
        (Specify the programming language to be used, such as Python, C++, etc.)

        Final output:
        (Provide the completed source code here. In other words, it's the program pool's content.)

        Other comment:
        (Add any additional notes, context, or requirements here that can help the user understand the code better.)
        '''
        # Define the required headers and their order
        required_headers = ["Main target:", "Language use:", "Final output:", "Other comment:"]

        # Remove extra newlines and spaces, condense the input into a single line
        condensed_input = re.sub(r'\s+', ' ', input_string.strip())

        # Create a regex pattern to check if the headers appear in the correct order
        header_pattern = '.*'.join(map(re.escape, required_headers))
        if not re.search(header_pattern, condensed_input):
            return False

        # Split the input into lines and remove empty lines
        lines = [line.strip() for line in input_string.strip().split('\n') if line.strip()]
        current_header_index = 0

        for i, line in enumerate(lines):
            # Match the format of a header
            match = re.match(r'^([A-Za-z ]+:)\s*$', line)
            if match:
                header = match.group(1).strip()

                # Check if the header matches the expected header in the required order
                if header == required_headers[current_header_index]:
                    # Check if the next header directly follows this header
                    if (
                        current_header_index < len(required_headers) - 1
                    ):  # If it's not the last header
                        next_expected_header = required_headers[current_header_index + 1]
                        if i + 1 < len(lines) and re.match(
                            r'^\s*' + re.escape(next_expected_header) + r'\s*$', lines[i + 1]
                        ):
                            return False  # Two consecutive headers without content
                    current_header_index += 1
                    if current_header_index > len(required_headers) - 1:
                        break

        # Ensure all headers are matched
        return current_header_index == len(required_headers)

    def is_valid_message_format(self, input_string):
        # Define the required headers and their order
        required_headers = ["Main problem:", "Program pool:", "Current job:", "Current job output:"]

        # Remove extra newlines and spaces, condense the input into a single line
        condensed_input = re.sub(r'\s+', ' ', input_string.strip())

        # Create a regex pattern to check if the headers appear in the correct order
        header_pattern = '.*'.join(map(re.escape, required_headers))
        if not re.search(header_pattern, condensed_input):
            return False

        # Split the input into lines and remove empty lines
        lines = [line.strip() for line in input_string.strip().split('\n') if line.strip()]
        current_header_index = 0
        last_header_line = -1  # Track the line number of the last processed header

        for i, line in enumerate(lines):
            # Match the format of a header
            match = re.match(r'^([A-Za-z ]+:)\s*', line)
            if match:
                header = match.group(1).strip()

                # Check if the header matches the expected header in the required order
                if header == required_headers[current_header_index]:
                    # Ensure there is content between the last header and the current one
                    if last_header_line != -1 and i - last_header_line == 1:
                        return False  # No content between consecutive headers

                    current_header_index += 1
                    last_header_line = i

                    # Break early if all headers have been processed
                    if current_header_index > len(required_headers) - 1:
                        break

        # Ensure all headers are matched
        if current_header_index != len(required_headers):
            return False

        # Ensure the last header has content after it
        if last_header_line != -1 and last_header_line == len(lines) - 1:
            return False  # No content after the last header

        return True
