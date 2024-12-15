import re
import os
import sys


# Function to get the file path after packaging
def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and PyInstaller executable.
    """
    # Check if running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):  # Check if application is bundled with PyInstaller
        base_path = os.path.dirname(sys.executable)  # Path to the folder containing the .exe
    else:
        base_path = os.path.abspath(".")  # Path for development environment

    return os.path.join(base_path, relative_path)


class Normalize:
    '''負責存放所有格式檢查函數'''

    # This function is used to extract the content of a specified section from a given input string.
    def extract_section_content(self, input_string, section_name):
        # Split the input string into lines
        lines = input_string.split('\n')

        # Initialize variables
        section_content = ""
        in_section = False

        # Iterate through each line to find the specified section
        for line in lines:
            stripped_line = line.strip()  # Remove leading/trailing whitespace

            # Check if the line is the start of the specified section
            if stripped_line.startswith(section_name + ":"):
                in_section = True
                # Extract content after the section name and include it in the result
                section_content += stripped_line[len(section_name) + 1 :].strip() + "\n"
            elif in_section:
                # Check if the line starts a new section (a valid header)
                # New section must start with an uppercase letter and end with a colon
                if stripped_line.endswith(":") and stripped_line[0].isupper():
                    break  # Stop at the beginning of the next Section
                # Otherwise, append the line as part of the current section
                section_content += line + "\n"

        # If no content is found, return a warning
        if not section_content.strip():
            return "Warning: No content was found."
        return section_content.strip()

    def insert_section(self, input_string, insert_section_name, insert_section_content):
        # Ensure the new section name ends with a colon
        insert_section_name = insert_section_name.strip()
        if not insert_section_name.endswith(":"):
            insert_section_name += ":"

        # Prepare the new section content
        new_section = f"\n{insert_section_name}\n{insert_section_content.strip()}\n"

        # Add the new section at the end of the input string
        result_string = input_string.rstrip() + new_section

        return result_string

    # 檢查 WorkSheet 是否有效
    def is_valid_worksheet_format(self, input_string):
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

    # Check if generate output format is valid
    def is_valid_generate_output_format(self, input_string):
        required_headers = ["Main target:", "Language use:", "Final output:", "Other comment:"]
        valid_headers = set(required_headers)
        input_headers = set()

        # Extract headers from the input string
        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        # Check for extra headers
        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        # Check content of required headers
        for header in required_headers:
            content = self.extract_section_content(
                input_string, header[:-1]
            )  # Remove the colon for section name
            if header != "Other comment:" and content == "Warning: No content was found.":
                return False

        return True

    # 檢查 Message 是否有效
    def is_valid_message_format(self, input_string):
        required_headers = ["Main problem:", "Program pool:", "Current job:", "Current job output:"]
        valid_headers = set(required_headers)
        input_headers = set()

        # Extract headers from the input string
        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        # Check for extra headers
        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        # Check content of required headers
        for header in required_headers:
            content = self.extract_section_content(
                input_string, header[:-1]
            )  # Remove the colon for section name
            if content == "Warning: No content was found.":
                return False

        return True

    def is_valid_bullet_list_format(self, input_string):
        # 定義正則表達式模式
        bullet_list_pattern = r"""
                ^(?:                             # 開始匹配
                    No\sissues$                  # 第一種情況: "No issues"
                    |                           # 或
                    (?:                         # 啟動多行模式
                        Problem\s\d+:           # 匹配 Problem + 數字 + 冒號
                        .+                      # 匹配至少一個非空內容
                        \s*                     # 允許任意空白
                    )+                          # 至少一組問題
                )$                              # 確保整個字符串都符合
            """

        # 使用正則表達式檢查格式
        return bool(re.match(bullet_list_pattern, input_string.strip(), re.VERBOSE | re.MULTILINE))

    def is_valid_ai_code_format(self, input_string):
        required_headers = [
            "Probability of AI code:",
            "Analysis:",
            "Final Judgement:",
            "Jugement Reason:",
        ]
        valid_headers = set(required_headers)
        input_headers = set()

        # Extract headers from the input string
        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        # Check for extra headers
        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        # Check content of required headers
        for header in required_headers:
            content = self.extract_section_content(
                input_string, header[:-1]
            )  # Remove the colon for section name
            if content == "Warning: No content was found.":
                return False

        return True

    def is_valid_plagiarism_code_format(self, input_string):
        required_headers = [
            "Probability of Plagiarism:",
            "Analysis:",
            "Final Judgement:",
            "Jugement Reason:",
        ]
        valid_headers = set(required_headers)
        input_headers = set()

        # Extract headers from the input string
        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        # Check for extra headers
        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        # Check content of required headers
        for header in required_headers:
            content = self.extract_section_content(
                input_string, header[:-1]
            )  # Remove the colon for section name
            if content == "Warning: No content was found.":
                return False

        return True


class Enforcer(Normalize):
    '''負責執行格式檢查和控制邏輯'''

    def __init__(self):
        try:
            print("Normalization Enforcer is ready.")
        except Exception as e:
            print(e)

    def strictlyFollowFormat(self, inputFunction, validationFunction, *args, **kwargs):
        flag = False
        timesCount = 0

        while not flag:
            result = inputFunction(*args, **kwargs)

            if validationFunction(result):
                flag = True
            else:
                timesCount += 1
                if timesCount > 8:
                    flag = True

        return result
