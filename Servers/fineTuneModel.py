from openai import OpenAI
from trainingClass import TrainingTool

# Read API keys from key file.
with open('key.txt', 'r') as file:
    keys = file.readlines()

api_key_model_3 = keys[2].strip()
client = OpenAI(api_key=api_key_model_3)

t = TrainingTool()

temp = '''
const double pi = 3.1415926535;
enum key{
	up,
	down,
	left,
	right
};
enum common_color{
    red,
    green,
    blue
};'''
completion = client.chat.completions.create(
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
