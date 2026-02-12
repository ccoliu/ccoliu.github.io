# ---------------------------------------------------
# Codoctopus — Format Enforcer
# Refactored from Servers/FormatEnforcer.py
# Removed resource_path() — no longer needed.
# ---------------------------------------------------

import re


class Normalize:
    """Stores all format validation functions."""

    def extract_section_content(self, input_string, section_name):
        lines = input_string.split('\n')
        section_content = ""
        in_section = False

        for line in lines:
            stripped_line = line.strip()

            if stripped_line.startswith(section_name + ":"):
                in_section = True
                section_content += stripped_line[len(section_name) + 1:].strip() + "\n"
            elif in_section:
                if stripped_line.endswith(":") and stripped_line[0].isupper():
                    break
                section_content += line + "\n"

        if not section_content.strip():
            return "Warning: No content was found."
        return section_content.strip()

    def insert_section(self, input_string, insert_section_name, insert_section_content):
        insert_section_name = insert_section_name.strip()
        if not insert_section_name.endswith(":"):
            insert_section_name += ":"

        new_section = f"\n{insert_section_name}\n{insert_section_content.strip()}\n"
        result_string = input_string.rstrip() + new_section
        return result_string

    def is_valid_worksheet_format(self, input_string):
        lines = [line.strip() for line in input_string.strip().split('\n') if line.strip()]

        if not re.match(r'^\s*Worksheet\s*$', lines[0]):
            return False
        if not re.match(r'^\s*Main problem:\s*', lines[1]):
            return False

        for line in lines[2:]:
            if not re.match(r'^\s*Member message:\s*Help me\s+', line):
                return False

        return True

    def is_valid_generate_output_format(self, input_string):
        required_headers = ["Main target:", "Language use:", "Final output:", "Other comment:"]
        valid_headers = set(required_headers)
        input_headers = set()

        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        for header in required_headers:
            content = self.extract_section_content(input_string, header[:-1])
            if header != "Other comment:" and content == "Warning: No content was found.":
                return False

        return True

    def is_valid_message_format(self, input_string):
        required_headers = ["Main problem:", "Program pool:", "Current job:", "Current job output:"]
        valid_headers = set(required_headers)
        input_headers = set()

        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        for header in required_headers:
            content = self.extract_section_content(input_string, header[:-1])
            if content == "Warning: No content was found.":
                return False

        return True

    def is_valid_bullet_list_format(self, input_string):
        bullet_list_pattern = r"""
                ^(?:
                    No\sissues$
                    |
                    (?:
                        Problem\s\d+:
                        .+
                        \s*
                    )+
                )$
            """
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

        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        for header in required_headers:
            content = self.extract_section_content(input_string, header[:-1])
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

        for line in input_string.split('\n'):
            line = line.strip()
            if ':' in line:
                header = line.split(':', 1)[0].strip() + ":"
                input_headers.add(header)

        extra_headers = input_headers - valid_headers
        if extra_headers:
            return False

        for header in required_headers:
            content = self.extract_section_content(input_string, header[:-1])
            if content == "Warning: No content was found.":
                return False

        return True


class Enforcer(Normalize):
    """Executes format checks and control logic."""

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
