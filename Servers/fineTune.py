from openai import OpenAI

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()
    
api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)

with open('trainingFileId.txt', 'r') as file:
    keys = file.readlines()
    
file_id = keys[0].strip()

response = client.fine_tuning.jobs.create(
  training_file= file_id,
  model="gpt-3.5-turbo"
)