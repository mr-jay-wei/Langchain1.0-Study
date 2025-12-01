# env:langgraph_env
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL= os.getenv("DEEPSEEK_BASE_URL")
MODEL_NAME= os.getenv("DEEPSEEK_MODEL_NAME")

# 从 Langfuse 导入 OpenAI（这是唯一需要改的地方）
from langfuse.openai import openai

# 使用 OpenAI 客户端（代码完全不变）
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

response = client.chat.completions.create(
    name="langfuse 对 openai 库的使用 demo", 
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "你是一个友好的助手"},
        {"role": "user", "content": "解释光电效应？"}
    ],
    metadata={
        "langfuse_session_id": "session_456",
        "langfuse_user_id": "Jay",
        "langfuse_tags": ["production", "chat-bot"],
        "custom_field": "additional metadata"  # 普通 metadata 字段也可以
    },
)

print(response.choices[0].message.content)