# traning.py
from openai import OpenAI
# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

client = keys[2].strip()

client.files.create(
  file=open("data.jsonl", "rb"),
  purpose="fine-tune"
)
client.fine_tuning.jobs.create(
  training_file="data.jsonl", 
  model="gpt-3.5-turbo"
)


# List 10 fine-tuning jobs
client.fine_tuning.jobs.list(limit=10)

# Retrieve the state of a fine-tune
client.fine_tuning.jobs.retrieve("ftjob-abc123")

# Cancel a job
client.fine_tuning.jobs.cancel("ftjob-abc123")

# List up to 10 events from a fine-tuning job
client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-abc123", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
client.models.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")

# 使用訓練好的模型進行預測
response = OpenAI.Completion.create(
    #model=trained_model_id,  # 使用訓練後的模型 ID
    #prompt="這裡輸入你的提示文字",
    #max_tokens=50
)