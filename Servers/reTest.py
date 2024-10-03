import re
import os  # System imports
import sys
import configparser  # For reading the config file (ini file)
from flask import Flask, request, jsonify, redirect, Response  # For Flask server
from flask_cors import CORS  # For Flask server
from openai import OpenAI  # OpenAI API
import os
import time
import threading
import random
import ssl  # Local https key

# Self-defined imports
from dataBase import dataBaseTools


def is_valid_worksheet_format(input_string):
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


# Function to get the file path after packaging
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Read API keys from key file using resource_path function
key_file_path = resource_path("key.txt")
with open(key_file_path, "r") as file:
    keys = file.readlines()

api_key_model_1 = keys[0].strip()
api_key_model_2 = keys[1].strip()
api_key_model_3 = keys[2].strip()

# Assign API keys to different models should use for the dived job.
client_model_1 = OpenAI(api_key=api_key_model_1)  # Gpt-3.5-turbo-A
client_model_2 = OpenAI(api_key=api_key_model_2)  # Gpt-3.5-turbo-B
client_model_3 = OpenAI(api_key=api_key_model_3)  # Fine-Tuning-Model

# Define some output format below.
WORKSHEET_FORMAT = '''Worksheet
Main problem: (understand what the user want to do and put it here)
(How many members are needed is up to you, since this is a one-way transfer, the roles cannot involve roles that require interactive communication. Each role will complete their work and then hand it off to the next person to continue. The smallest unit of task division is a function, meaning each person must be responsible for at least one function. Whether a person will need to handle more 
Member message: Help me ......
Member message: Help me ......
Member message: Help me ......
(... up to you, and don't list the index of the member)
(The last two messages are fixed and cannot be changed)
Member message: Help me Test the program to see if it reach the main problem, if not, fix it and return the new code.
Member message: Help me combine all the finished tasked and adjust the variable name to make sure the program runs correctly, and make sure to solved the errors.
(Don't add any extra information, and don't change the format)
'''
BOSS = "You are a software company boss that is skilled at divided the work into different parts and assign them to different people, and you are really good at managing the team and make sure the project is finished with high quality and meet the main target."


# Use to creating the worksheet for the team to solve the problem.
def createWorkSheet(request, language):
    workSheet = client_model_1.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": BOSS,
            },
            {
                "role": "user",
                "content": "Please strictly follow the format below to create a worksheet for the team to solve the problem.\n"
                + WORKSHEET_FORMAT
                + "How many members are needed to complete this project, as well as the messages of each member, is up to you, It is **required** that the output strictly follows the above format, and any deviations are unacceptable."
                + "The main target (request) is:\n"
                + request
                + "\n"
                + "Please make sure all the team members is using the language: "
                + language
                + "\n",
            },
        ],
    )

    return workSheet.choices[0].message.content


def strictlyFollowFormat(inputFunction, *args, **kwargs):
    flag = False  # 設定一個標誌，用來判斷是否已經通過格式檢查
    timesCount = 0  # 計數器，用來記錄嘗試次數
    while not flag:  # 當格式尚未通過檢查時，持續迴圈
        result = inputFunction(*args, **kwargs)  # 呼叫傳入的函數並取得結果
        # 檢查格式是否有效
        if is_valid_worksheet_format(result):
            flag = True  # 若格式有效，將標誌設為 True 結束迴圈
        else:
            timesCount += 1  # 格式無效時，計數器加1
            if timesCount > 8:  # 若嘗試次數超過8次，強制結束迴圈
                flag = True

    return result  # 返回最終結果（無論格式是否有效）


print(
    strictlyFollowFormat(
        createWorkSheet, "Create a program that can calculate the sum of two numbers.", "C++"
    )
)
