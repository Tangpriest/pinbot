import os
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("DASHSCOPE_API_KEY"))

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def need_camera_by_llm(question: str) -> bool:
    """
    通过大模型 function call 语义分析，判断是否需要调用摄像头。
    """
    functions = [
        {
            "name": "should_use_camera",
            "description": "你是一个智能机器人，摄像头就是的眼睛，你需要根据问题的输入，判断用户的问题是否需要调用摄像头（如需要识别图片、分析画面等），比如用户问你，我看起来如何，你就需要调用摄像头",
            "parameters": {
                "type": "object",
                "properties": {
                    "need_camera": {
                        "type": "boolean",
                        "description": "是否需要调用摄像头"
                    }
                },
                "required": ["need_camera"]
            }
        }
    ]

    messages = [
        {"role": "system", "content": "你是一个助手，请根据用户问题判断是否需要调用摄像头。"},
        {"role": "user", "content": question}
    ]

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        functions=functions,
        function_call={"name": "should_use_camera"},
        max_tokens=50,
    )

    # 解析 function call 结果
    try:
        function_call = completion.choices[0].message.function_call
        if function_call and hasattr(function_call, "arguments"):
            args = json.loads(function_call.arguments)
            return args.get("need_camera", False)
        else:
            # 没有 function_call，说明模型没触发函数，默认不需要摄像头
            return False
    except Exception as e:
        print("Function call 解析失败：", e)
        return False 