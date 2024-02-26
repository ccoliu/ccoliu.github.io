import json

# 假设你的文本文件名为 example.txt
file_path = 'example.txt'

# 使用 with 语句打开文件，确保文件正确关闭
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# file_content 变量现在包含了文件的全部内容，包括换行符等特殊字符
print(file_content)


class StringToJsonl:
    def __init__(self):
        print("you may format now")

    def formatToJSONL(self, question, content):
        jsonl_data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a coding-style master good at formatting codes into same coding style.",
                },
                {"role": "user", "content": "Give me a perfect coding style example."},
                {"role": "assistant", "content": "Taiwan."},
            ]
        }
        # put things in data stream
        jsonl_data["messages"][-2]["content"] = question
        jsonl_data["messages"][-1]["content"] = content

        jsonl_string = json.dumps(jsonl_data)

        # Keep Writing Data to JSONL
        with open('fineTuneData.jsonl', 'a') as file:
            file.write(jsonl_string + '\n')
            print("Write success")
