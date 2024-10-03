# ---------------------------------------------------
# Author:Daniel Hsiao (Github: https://github.com/whps970083)
# Date: 2024/10/04
# Version: <V10.0.0.0>
# Description: This is a format enforcer tool that can be used to enforce the format of the output of the GPT-3 model.
# ---------------------------------------------------

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
            print("You may use the enforcer tools now!")
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
