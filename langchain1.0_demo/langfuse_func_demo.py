# env:langgraph_env
import os
from dotenv import load_dotenv
load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY= os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST= os.getenv("LANGFUSE_HOST")

from langfuse import observe,Langfuse

langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST
)

@observe(name="func3")
def my_function(input_data):
    # 您的业务逻辑
    result = f"处理了：{input_data}"
    return result

@observe(name="func4")
def main():
    result = my_function("测试数据")
    print(result)

main()