from openai import OpenAI
from trainingClass import TrainingTool
import time
import threading
from formattingToJsonl import StringToJsonl

fineTuneTools = TrainingTool()
jsonTool = StringToJsonl()


def check_condition():
    if fineTuneTools.getLatestJobStatus() == "succeeded":
        return True
    elif fineTuneTools.getLatestJobStatus() == "failed":
        return "Failed"
    else:
        return False


def check_status_periodically(timeout=1800):
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
            time.sleep(600)  # wait for 5 minutes to check.


fileID = fineTuneTools.upLoadFile('Misc/fineTuneData.jsonl')

fineTuneTools.fineTune(fileID)

# 創建一個線程來週期性檢查條件
thread = threading.Thread(target=check_status_periodically)
thread.start()
