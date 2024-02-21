# traning.py
from openai import OpenAI

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()
    
api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)

# upLoad OK
client.files.create(
  file=open("usefulData.jsonl", "rb"),
  purpose="fine-tune"
)

print(client.files.list(extra_query=id))