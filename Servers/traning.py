from openai import OpenAI

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()
    
api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)
flag = True
# Upload the file and receive the response
response = client.files.create(
  file=open("usefulData.jsonl", "rb"),
  purpose="fine-tune"
)

# Extract the file ID from the response
file_id = response.id  # 修改此處

# Print the file ID for later use in fine-tuning
print(f"File ID: {file_id}")

# Write the file ID to a text file
with open('trainingFileId.txt', 'w') as file:
    file.write(file_id)
