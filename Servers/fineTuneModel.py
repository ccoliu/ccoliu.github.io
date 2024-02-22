from openai import OpenAI

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()
    
api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)
completion = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-0613:personal::8uchyi8e",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of Paris?"}
  ]
)

print(completion.choices[0].message)