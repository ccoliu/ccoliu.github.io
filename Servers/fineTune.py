from openai import OpenAI

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)


fine_tunes = client.fine_tuning.jobs.list()

# 遍歷任務列表，打印每個任務的模型 ID
for fine_tune in fine_tunes.data:
    print(f"Fine-tune ID: {fine_tune.id}, Model: {fine_tune.fine_tuned_model}")

client.models.delete("ft:gpt-3.5-turbo-0613:personal::8uchyi8e")  # will delete successfully
