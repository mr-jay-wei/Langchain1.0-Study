# env:langgraph_env
# human_in_the_loop_demo.py
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

# ===== 1. Langfuse 监控（可选） =====
LANGFUSE_SECRET_KEY  = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY  = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST        = os.getenv("LANGFUSE_HOST")

from langfuse.langchain import CallbackHandler
handler = CallbackHandler()

# ===== 2. 模型 =====
API_KEY     = os.getenv("DEEPSEEK_API_KEY")
BASE_URL    = os.getenv("DEEPSEEK_BASE_URL")
MODEL_NAME  = os.getenv("DEEPSEEK_MODEL_NAME")

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
basic_model = ChatOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    model=MODEL_NAME,
    temperature=0.0,
    max_tokens=4096,
)

# ===== 3. 工具 =====
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b

@tool
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters."""
    if height_m <= 0 or weight_kg <= 0:
        raise ValueError("height_m and weight_kg must be greater than 0.")
    return weight_kg / (height_m ** 2)

# ===== 4. Human-in-the-loop 配置 =====
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

tool_agent = create_agent(
    model=basic_model,
    tools=[get_weather, add_numbers, calculate_bmi],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "get_weather": False,                                    # 直接执行
                "add_numbers": True,                                     # 可 approve/edit/reject
                "calculate_bmi": {"allowed_decisions": ["approve", "reject"]},
            },
            description_prefix="Tool execution pending approval",
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="You are a helpful assistant",
)

# ===== 5. 运行：第一次调用会中断，第二次 approve 继续 =====

THREAD_ID = str(uuid.uuid4())          # 固定线程，方便继续

# 5.1 第一次 invoke —— 触发 calculate_bmi 审批中断
initial_input = {
    "messages": [{
        "role": "user",
        "content": "我身高 180cm，体重 180 斤，我的 BMI 是多少？"
    }],
}
config = {
    "callbacks": [handler],
    "run_name": "dynamic_demo2",
    "metadata": {
        "langfuse_user_id": "Jay",
        "langfuse_session_id": "session_123",
        "langfuse_tags": ["Human-in-the-loop"]
    },
    "configurable": {"thread_id": THREAD_ID},
}

# 如果只想看中断效果，取消下面两行注释
interrupt_result = tool_agent.invoke(initial_input, config=config)

print(f"\n第一次调用结果（等待审批）：{interrupt_result}")

# ===== 6. 第二次调用：添加 approve 继续执行 =====
from langgraph.types import Command

# 构造 approve 命令
# 对于 calculate_bmi 工具，使用 approve 决定
resume_command = Command(
    resume={"decisions": [{"type": "approve"}]}
)

# 使用相同的 config（包含 thread_id）继续执行
continue_result = tool_agent.invoke(
    resume_command,  # 传入 Command 对象而不是初始输入
    config=config
)

print(f"\n第二次调用结果（已批准）：{continue_result}")

