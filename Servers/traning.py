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
    response = client.fine_tuning.jobs.create(training_file=fileID, model="gpt-3.5-turbo")
    fineTuneID = response.id
    status = client.fine_tuning.jobs.retrieve(fineTuneID)
    print(status)
    client.fine_tuning.jobs.cancel(fineTuneID)
    return fineTuneID


fileID = upLoadFile("usefulData.jsonl")
fileTuneID = fineTune(fileID)

print(fileTuneID)
