# env:langgraph_env
import os
from dotenv import load_dotenv
load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY= os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST= os.getenv("LANGFUSE_HOST")

from langfuse.langchain import CallbackHandler
handler = CallbackHandler()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL= os.getenv("DEEPSEEK_BASE_URL")
MODEL_NAME= os.getenv("DEEPSEEK_MODEL_NAME")

# 初始化模型
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

model = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL_NAME, # OpenRouter 支持的模型名称
        temperature=0.0,
        max_tokens=4096,
    )

'''
# ====================================================
# 使用模型
response = model.invoke("解释大航海时代？")
print(response.content)
# ====================================================
'''

# 导入自定义工具
import sys
# Windows 终端编码支持
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# 添加 tools 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from weather import get_weather
from calculator import calculator
from web_search import web_search

# 创建一个简单的 Agent
agent = create_agent(
    model=model,
    tools=[get_weather, calculator, web_search],
    system_prompt="""你是一个友好的助手。
        特点：
        - 回答简洁明了
        - 使用工具前先说明
        - 结果用表格或列表清晰展示""",
    )

print("\n测试：自定义行为的 Agent")
response = agent.invoke({
    "messages": [{"role": "user", "content": "如果北京天气晴朗就去计算 100 加 40 的结果再乘以 3 等于多少？"}]
    },
    config={
        "callbacks": [handler],
        "run_name": "weather-calculator-agent",  # 设置 trace 名称
        "metadata": {
            "langfuse_user_id": "Jay",
            "langfuse_session_id": "session_123",
            "langfuse_tags": ["agent", "weather"]
        }
    }
)

print(f"\nAgent 回复：{response['messages'][-1].content}")