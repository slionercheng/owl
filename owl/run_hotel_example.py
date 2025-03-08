from dotenv import load_dotenv
load_dotenv()

from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig

from typing import List, Dict
from loguru import logger

from utils import OwlRolePlaying, run_society
import os

# 导入我们的酒店工具包
from camel.toolkits import *

# 定义酒店搜索工具
# 定义可用的工具
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch content from a URL, supporting various formats like JSON, YAML, and plain text",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch content from"
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method to use (GET or POST)",
                        "enum": ["GET", "POST"]
                    },
                    "data": {
                        "type": "object",
                        "description": "Data to send in the request body (for POST requests)"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Additional headers to send with the request"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def construct_society(question: str) -> OwlRolePlaying:
    r"""Construct the society based on the question."""

    user_role_name = "user"
    assistant_role_name = "assistant"
    
    user_model = ModelFactory.create(
        model_platform=ModelPlatformType.AZURE,
        model_type=ModelType.GPT_4O,
        model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(), # [Optional] the config for model
    )

    assistant_model = ModelFactory.create(
        model_platform=ModelPlatformType.AZURE,
        model_type=ModelType.GPT_4O,
        model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(), # [Optional] the config for model
    )
    
    # 创建酒店模型并直接传递工具参数
    hotel_model = ModelFactory.create(
        model_platform=ModelPlatformType.AZURE,
        model_type=ModelType.GPT_4O,
        model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        tools=AVAILABLE_TOOLS  # 直接传递工具参数
    )

    # 创建工具列表，只包含酒店工具包
    tools_list = [
        *HotelToolkit(model=hotel_model).get_tools(),
    ]

    user_agent_kwargs = dict(model=user_model)
    assistant_agent_kwargs = dict(model=assistant_model, tools=tools_list)
    
    task_kwargs = {
        'task_prompt': question,
        'with_task_specify': False,
    }

    society = OwlRolePlaying(
        **task_kwargs,
        user_role_name=user_role_name,
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name=assistant_role_name,
        assistant_agent_kwargs=assistant_agent_kwargs,
    )
    
    return society


# 示例问题
question = "我需要预订杭州的一个酒店：2025年3月9日，1天的酒店，经纬度（120.026208, 30.279212）。请一步步处理：第一步，你自己选择一个不错的酒店，第二步，帮我选择一个房间。最后告诉我你选择的详细信息"

society = construct_society(question)
answer, chat_history, token_count = run_society(society)

logger.success(f"Answer: {answer}")