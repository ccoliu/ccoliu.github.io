from openai import OpenAI
from trainingClass import TrainingTool
import time
import threading
from formattingToJsonl import StringToJsonl

fineTuneTools = TrainingTool()
test = StringToJsonl()


def check_condition():
    if fineTuneTools.getLatestJobStatus() == "succeeded":
        return True
    elif fineTuneTools.getLatestJobStatus() == "failed":
        return "Failed"
    else:
        return False


def check_status_periodically(timeout=600):
    start_time = time.time()
    while True:
        if check_condition() == True:
            print("The model has been finished")

            return fineTuneTools.getLatestJobStatus()
        elif check_condition() == "Failed":
            print("The model has been failed")
            break
        elif (time.time() - start_time) > timeout:
            print("Over time limit training failed")
            break
        else:
            time.sleep(300)  # wait for 5 minutes to check.


""" # 創建一個線程來週期性檢查條件
thread = threading.Thread(target=check_status_periodically)
thread.start()

a = fineTuneTools.getLatestFineTuneModel()
print(a) """
file_path = 'example.txt'

# 初始化两个列表来存储问题和答案
questions = []
answers = []

# 用来临时存储当前问题或答案的内容
current_content = ""
is_question = False

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # 检查是否为问题的开始
        if line.startswith('Q:'):
            # 如果之前已经有正在读取的内容，且是问题，则保存
            if is_question and current_content:
                questions.append(current_content.strip())
                current_content = ""  # 重置内容变量
            is_question = True  # 标记当前为问题
            current_content += line[2:]  # 去掉 'Q:'，然后追加内容
        # 检查是否为答案的开始
        elif line.startswith('A:'):
            # 如果之前有正在读取的问题内容，则保存该问题
            if is_question and current_content:
                questions.append(current_content.strip())
                current_content = ""  # 重置内容变量
            is_question = False  # 标记当前为答案
            current_content += line[2:]  # 去掉 'A:'，然后追加内容
        else:
            # 继续追加到当前内容
            current_content += line

# fineTuneTools.deleteAllModels()
# client.models.delete("ft:gpt-3.5-turbo-0613:personal::8uchyi8e")  # will delete successfully
