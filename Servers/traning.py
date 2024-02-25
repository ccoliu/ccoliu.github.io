from openai import OpenAI


# Read API keys from key file and use only one for all fine tuning jobs.
with open("key.txt", "r") as file:
    keys = file.readlines()

api_key_model_3 = keys[2].strip()

client = OpenAI(api_key=api_key_model_3)


# input file name and will return fileID
def upLoadFile(fileName):
    # Upload the file and receive the response
    response = client.files.create(file=open(fileName, "rb"), purpose="fine-tune")

    # Extract the file ID from the response
    file_id = response.id

    # Print the file ID for later use in fine-tuning
    print(f"File ID: {file_id}")

    # Write the file ID to a text file
    with open("fileNames.txt", "w") as file:
        file.write(file_id)

    return file_id


def getFileID():
    with open('fileNames.txt', 'r') as file:
        keys = file.readlines()

    file_id = keys[0].strip()

    return file_id


# input file ID and will start traning and retrun fine tune ID and will print out current status
def fineTune(fileID):
    # Create a fine tuninig job
    response = client.fine_tuning.jobs.create(training_file=fileID, model="gpt-3.5-turbo")
    # Get fine tuing job ID
    fineTuneID = response.id
    # Get current job info
    jobInfo = client.fine_tuning.jobs.retrieve(fineTuneID)
    # Get current job status
    jobStatus = jobInfo.status

    # Write in status into file
    with open("moldesNames.txt", "w") as file:
        file.write(jobStatus)

    client.fine_tuning.jobs.cancel(fineTuneID)

    return fineTuneID


# This function will delete all the files at the cloud in OpenAI since we will change files periodically.
def deleteAllFiles():
    response = client.files.list()
    for response in response.data:
        client.files.delete(response.id)


# This function will print out all fine tune jobs' id and model name
def getFineTuneList():
    fine_tunes = client.fine_tuning.jobs.list()
    for fine_tune in fine_tunes.data:
        print(f"Fine-tune ID: {fine_tune.id}, Model: {fine_tune.fine_tuned_model}")


def getLatestFineTuneModel():
    fine_tunes = client.fine_tuning.jobs.list()
    for fine_tune in fine_tunes.data:
        print(f"Model: {fine_tune.fine_tuned_model}")
        break


def getLatestJobId():
    fine_tunes = client.fine_tuning.jobs.list()
    for fine_tune in fine_tunes.data:
        print(f"Fine-tune ID: {fine_tune.id}")
        return fine_tune.id


response = client.fine_tuning.jobs.retrieve(getLatestJobId())

print(response.status)
""" fileID = upLoadFile("usefulData.jsonl")
fileTuneID = fineTune(fileID)

print(fileTuneID)
"""
