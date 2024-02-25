from openai import OpenAI
from trainingClass import TrainingTool

testClass = TrainingTool()

testClass.getFineTuneList()

# client.models.delete("ft:gpt-3.5-turbo-0613:personal::8uchyi8e")  # will delete successfully
