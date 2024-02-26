from openai import OpenAI
from trainingClass import TrainingTool

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)

t = TrainingTool()

# Input some question to test
temp = '''Give me the header format'''

completion = client.chat.completions.create(
    # get the latest model we trained
    model=t.getLatestFineTuneModel(),
    messages=[
        {
            "role": "system",
            "content": "You are a coding-style master good at formatting codes into one specific coding style.",
        },
        {"role": "user", "content": temp},
    ],
)

print(completion.choices[0].message)
