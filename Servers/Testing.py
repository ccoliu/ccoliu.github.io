import os
import sys
import configparser
import time
import threading
import random
import unittest
from flask import Flask, request, jsonify, redirect, Response
from flask_cors import CORS
from openai import OpenAI

# 自訂義模組
from dataBase import dataBaseTools
import FormatEnforcer

testEnforcer = FormatEnforcer.Enforcer()


# Function to get the file path after packaging
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 讀取 API 金鑰
key_file_path = resource_path("key.txt")
with open(key_file_path, "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# 初始化 OpenAI 模型
client_model_1 = OpenAI(api_key=api_key_model_1)
client_model_2 = OpenAI(api_key=api_key_model_2)
client_model_3 = OpenAI(api_key=api_key_model_3)

# 常數與格式
WORKSHEET_FORMAT = '''
Worksheet
Main problem: (understand what the user want to do and put it here)
(How many members are needed is up to you...)
...
'''

BOSS = "You are a software company boss skilled at dividing work into parts..."
PRESENTER = "You are the last person responsible for presenting the program..."
FRONTED_OUTPUT_FORMAT = '''
Main target:
(Always describe the primary problem or task clearly here.)
...
'''
MESSAGE_FORMAT = '''
Main problem:
(Always put the main problem here)
Program pool:
(Add your completed work to the program pool.)
...
'''
MESSAGE_FORMAT_V2 = '''
Main problem:
(Put the project main target here to understand what the user wants.)
...
'''


# 創建 Worksheet
def createWorkSheet(request, language):
    response = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": BOSS},
            {
                "role": "user",
                "content": "Please strictly follow the format below..."
                + WORKSHEET_FORMAT
                + "The main target is:\n"
                + request
                + "\nPlease make sure all members use the language: "
                + language,
            },
        ],
    )
    return response.choices[0].message.content


# 格式化輸出
def finalOutputDisplayer(currentProgress, mainTarget):
    response = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": PRESENTER},
            {
                "role": "user",
                "content": "Here is the main target\n"
                + mainTarget
                + "\nHere is the final result:\n"
                + currentProgress
                + "\n"
                + FRONTED_OUTPUT_FORMAT,
            },
        ],
    )
    return response.choices[0].message.content


# 執行員工工作 (V1)
def employeeWork(mainTarget, systemRole, jobContent, inputProgress):
    response = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemRole},
            {
                "role": "user",
                "content": "Here is the target of the project\n"
                + mainTarget
                + "\nHere is the current progress:\n"
                + inputProgress
                + "\n"
                + jobContent
                + "\n"
                + MESSAGE_FORMAT,
            },
        ],
    )
    return response.choices[0].message.content


# 執行員工工作 (V2)
def employeeWork_V2(mainTarget, systemRole, jobContent, inputProgress):
    response = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": systemRole},
            {
                "role": "user",
                "content": "Here is the main target of the project\n"
                + mainTarget
                + "\nHere is the last member's progress for you to refer:\n"
                + inputProgress
                + "\nHere is the job that you need to do:\n"
                + jobContent
                + "\n"
                + MESSAGE_FORMAT_V2,
            },
        ],
    )
    aiResponse = response.choices[0].message.content
    program_pool = testEnforcer.extract_section_content(inputProgress, "Program pool")
    job_output = testEnforcer.extract_section_content(aiResponse, "Current job output")
    combined_output = combineOutputs(program_pool, job_output)
    return testEnforcer.insert_section(aiResponse, "Program pool", combined_output)


# 合併輸出
def combineOutputs(pool, output):
    response = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Help me combine the content of two strings..."},
            {
                "role": "user",
                "content": "Combine the following two strings:\n" + pool + "\n" + output,
            },
        ],
    )
    return response.choices[0].message.content


# # 整理程式碼池
# def tidyUpProgramPool(mainTarget, programPool):
#     response = client_model_1.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are responsible for tidying up the program pool."},
#             {
#                 "role": "user",
#                 "content": "Here is the main target of the project:\n"
#                 + mainTarget
#                 + "\nHere is the program pool:\n"
#                 + programPool,
#             },
#         ],
#     )
#     return response.choices[0].message.content


# # 測試案例
# def test_employeeWork_V2_multilayer():
#     current_progress = '''
# Main problem:
# Develop a program that calculates the factorial of a given number using recursion.
# Current job:
# Current job output:
# Program pool:
# '''
#     layers = [
#         {
#             "mainTarget": "Define the factorial function.",
#             "systemRole": "Engineer.",
#             "jobContent": "Write basic factorial.",
#         },
#         {
#             "mainTarget": "Add error handling.",
#             "systemRole": "Engineer.",
#             "jobContent": "Ensure input is non-negative integer.",
#         },
#         {
#             "mainTarget": "Write test cases.",
#             "systemRole": "Engineer.",
#             "jobContent": "Write unit tests.",
#         },
#         {
#             "mainTarget": "Optimize test cases.",
#             "systemRole": "Engineer.",
#             "jobContent": "Test edge cases.",
#         },
#         {
#             "mainTarget": "Review code.",
#             "systemRole": "Senior Engineer.",
#             "jobContent": "Improve clarity and maintainability.",
#         },
#     ]

#     for layer in layers:
#         current_progress = employeeWork_V2(
#             layer["mainTarget"], layer["systemRole"], layer["jobContent"], current_progress
#         )

#     return current_progress


# # 主程式測試
# final_pool = testEnforcer.extract_section_content(test_employeeWork_V2_multilayer(), "Program pool")
# final_out = tidyUpProgramPool(
#     "Develop a program that calculates the factorial of a given number using recursion", final_pool
# )

# print(final_out)


import re


def is_valid_bullet_list_format(self, input_string):
    # 定義正則表達式模式
    bullet_list_pattern = r"""
        ^(?:                             # 開始匹配
            No\sissues$                  # 第一種情況: "No issues"
            |                           # 或
            (?:                         # 啟動多行模式
                Problem\s\d+:           # 匹配 Problem + 數字 + 冒號
                \s*\(.*?\)              # 匹配括號內的內容（允許空白或任意內容）
                \s*                     # 允許任意空白
            )+                          # 至少一組問題
        )$                              # 確保整個字符串都符合
    """

    # 使用正則表達式檢查格式
    return bool(re.match(bullet_list_pattern, input_string.strip(), re.VERBOSE | re.MULTILINE))


false_test_cases = [
    "Problem 1:\nProblem 2:",
    "Problem 1:\n(......)\nProblem 2:\n(......)\nExtra content here!",
    "Problem1:\n(......)\nProblem 2:\n(......)",
    "Problem 1:\n(......\nProblem 2:\n(......)",
    "Problem 1\n(......)\nProblem 2:\n(......)",
    "No issues\nProblem 1:\n(......)",
    "Problem 1:\n\nProblem 2:\n(......)",
]

# 測試 False 案例
for idx, case in enumerate(false_test_cases, 1):
    print(f"False Test Case {idx}: {case.strip()} => {is_valid_bullet_list_format(None, case)}")
