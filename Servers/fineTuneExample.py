from openai import OpenAI
from trainingClass import TrainingTool
import time
import threading
from fileFormatt import StringToJsonl
from dataBase import dataBaseTools
from bson import ObjectId

fineTuneTools = TrainingTool()
jsonTool = StringToJsonl()

dbT = dataBaseTools()


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


# fileID = fineTuneTools.upLoadFile('Misc/fact.jsonl')

# fineTuneTools.fineTune(fileID)

# Build a thread periodically check if the fine tune is succeeded.
""" thread = threading.Thread(target=check_status_periodically)
thread.start() """

# read comment file into jsonl // can successfully read the file into fact.jsonl
# jsonTool.read_file("Misc/comment.txt", "factDescription")


# nested query format example {'messages.role': "system1" , 'messages.content': "Give me a perfect coding style example."}

id = '65feda0d1127e8ff3e0c8d7b'
idFilter = {'_id': ObjectId(id)}


keyWord = "fib"


# The data base is named fineTune
# This collection that record both mode and use for searching is named codoctopus

# dbT.readDBToFile("fineTune", "codoctopus", "Misc/fineTuneDataTest.jsonl")

# dbT.communitySearch("fineTune", "codoctopus", keyWord)
dbT.createCollection("fineTune", "similarityCheck")
