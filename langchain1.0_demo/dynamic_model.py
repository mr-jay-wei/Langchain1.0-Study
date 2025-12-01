# env:langgraph_env
import os
from dotenv import load_dotenv
load_dotenv()
# ===================================================
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY= os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST= os.getenv("LANGFUSE_HOST")

from langfuse.langchain import CallbackHandler
handler = CallbackHandler()
# ===================================================
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL= os.getenv("DEEPSEEK_BASE_URL")
MODEL_NAME= os.getenv("DEEPSEEK_MODEL_NAME")

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

basic_model = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL_NAME,
        temperature=0.0,
        max_tokens=4096,
    )
advanced_model = ChatOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL_NAME,
        max_tokens=4096,
    )
# ===================================================
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
# ===================================================
# 【关键修改 1】为了验证，我们在中间件里加入打印语句
@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])
    
    # 打印日志，观察 message_count 的变化和模型的选择
    print(f"\n[Middleware Log] Current message count: {message_count}")

    if message_count > 4:
        print("[Middleware Log] Threshold reached! Using 'advanced_model'.")
        model = advanced_model
    else:
        print(f"[Middleware Log] Using 'basic_model'.")
        model = basic_model

    request.model = model
    return handler(request)

agent = create_agent(
    model=basic_model,  # Default model
    tools=[get_weather, calculator, web_search],
    middleware=[dynamic_model_selection],
    system_prompt="""你是一个友好的助手。
        特点：
        - 回答简洁明了
        - 使用工具前先说明
        - 结果用表格或列表清晰展示""",
)

# ===================================================
# 【关键修改 2】手动维护一个对话历史列表
conversation_history = []

# 定义一个辅助函数来简化调用过程
def chat(user_input):
    print(f"👤 User: {user_input}")
    
    # 将用户的新消息添加到历史中
    conversation_history.append(HumanMessage(content=user_input))
    
    # 调用 agent 时，传入完整的对话历史
    response = agent.invoke(
        {"messages": conversation_history},
        config={
            "callbacks": [handler],
            "run_name": "dynamic_demo_conversation",
            "metadata": {
                "langfuse_user_id": "Jay",
                "langfuse_session_id": "session_123",
                "langfuse_tags": ["agent"]
            }
        }
    )
    
    # 从返回结果中获取 AI 的回复
    ai_response = response["messages"][-1]
    
    # 将 AI 的回复也添加到历史中，为下一轮对话做准备
    conversation_history.append(ai_response)
    
    print(f"🤖 AI: {ai_response.content}")
    print("-----")

# 现在，我们来进行一场连续的对话
chat("解释大航海时代？")
chat("那个时代的主要国家有哪些？")
chat("请帮我计算一下 12345 * 6789 的结果。") # 到这里，历史长度为 1+1+1 = 3 (Human) + 2 (AI) = 5
chat("请帮我搜索一下最近的科技新闻。")
chat("请总结一下我们刚才的对话内容。")
# ===================================================