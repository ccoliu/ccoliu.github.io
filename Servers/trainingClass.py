from openai import OpenAI


class TrainingTool:
    # Get key during initailzation
    def __init__(self):
        with open("key.txt", "r") as file:
            keys = file.readlines()
        api_key_model_3 = keys[2].strip()
        self.client = OpenAI(api_key=api_key_model_3)

    # input file name and will return fileID
    def upLoadFile(self, fileName):
        # Upload the file and receive the response
        response = self.client.files.create(file=open(fileName, "rb"), purpose="fine-tune")

        # Extract the file ID from the response
        file_id = response.id

        # Print the file ID for later use in fine-tuning
        print(f"File ID: {file_id}")

        # Write the file ID to a text file
        with open("fileNames.txt", "w") as file:
            file.write(file_id)

        return file_id

    # get latest file id from file
    def getFileId(self):
        with open('fileNames.txt', 'r') as file:
            keys = file.readlines()

        file_id = keys[0].strip()

        return file_id

    # input file ID and will start traning and retrun fine tune ID and will print out current status
    def fineTune(self, fileID):
        # Create a fine tuninig job
        response = self.client.fine_tuning.jobs.create(training_file=fileID, model="gpt-3.5-turbo")
        # Get fine tuing job ID
        fineTuneID = response.id
        # Get current job info
        jobInfo = self.client.fine_tuning.jobs.retrieve(fineTuneID)

        # Write in status into file
        with open("moldesNames.txt", "w") as file:
            file.write(jobInfo.status)

        return fineTuneID

    # This function will delete all the files at the cloud in OpenAI since we will change files periodically.
    def deleteAllFiles(self):
        response = self.client.files.list()
        for response in response.data:
            self.client.files.delete(response.id)

    # This function will print out all fine tune jobs' id and model name
    def getFineTuneList(self):
        response = self.client.fine_tuning.jobs.list()
        for fine_tune in response.data:
            print(f"Fine-tune ID: {fine_tune.id}, Model: {fine_tune.fine_tuned_model}")

    def getLatestFineTuneModel(self):
        response = self.client.fine_tuning.jobs.list()
        for fine_tune in response.data:
            with open("moldesNames.txt", "w") as file:
                file.write(fine_tune.fine_tuned_model)
            print(f"Model: {fine_tune.fine_tuned_model}")
            return fine_tune.fine_tuned_model

    def getLatestJobId(self):
        response = self.client.fine_tuning.jobs.list()
        for fine_tune in response.data:
            print(f"Fine-tune ID: {fine_tune.id}")
            return fine_tune.id

    def getLatestJobStatus(self):
        response = self.client.fine_tuning.jobs.retrieve(self.getLatestJobId())
        return response.status

    def deleteAllModels(self):
        response = self.client.fine_tuning.jobs.list()
        for fine_tune in response.data:
            print(f"Model: {fine_tune.fine_tuned_model}")
            self.client.models.delete(fine_tune.fine_tuned_model)

    def deleteAllModelsExceptLatest(self):
        response = self.client.fine_tuning.jobs.list()
        models = response.data

        if len(models) > 1:
            for fine_tune in models[1:]:
                print(f"Deleting model: {fine_tune.fine_tuned_model}")
                self.client.models.delete(fine_tune.fine_tuned_model)
            print("Finished deleting all models except the latest one.")
        else:
            print("No models to delete or only one model exists.")
