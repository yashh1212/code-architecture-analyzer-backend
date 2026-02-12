from zhipuai import ZhipuAI
client = ZhipuAI(api_key="d83b942d65914c27a51a696ff97d89c6.39gAWb4ZAg3IS9yO")
response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[
        {"role": "user", "content": "As a marketing expert, please create an attractive slogan for my product"},
        {"role": "assistant", "content": "Sure, to create an attractive slogan, please tell me some information about your product"},
        {"role": "user", "content": "ZhipuAI Open Platform"},
        {"role": "assistant", "content": "Ignite the future, ZhipuAI paints the infinite, making innovation within reach!"},
        {"role": "user", "content": "Create a more precise and attractive slogan"}
    ],
)
print(response)