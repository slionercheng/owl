# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
import os
from typing import Any, Dict, List, Optional, Union

from openai import AzureOpenAI, Stream

from camel.configs import OPENAI_API_PARAMS, ChatGPTConfig
from camel.messages import OpenAIMessage
from camel.models.base_model import BaseModelBackend
from camel.types import (
    ChatCompletion,
    ChatCompletionChunk,
    ModelType,
)
from camel.utils import BaseTokenCounter, OpenAITokenCounter, api_keys_required


class AzureOpenAIModel(BaseModelBackend):
    r"""Azure OpenAI API in a unified BaseModelBackend interface.

    Args:
        model_type (Union[ModelType, str]): Model for which a backend is
            created, one of GPT_* series.
        model_config_dict (Optional[Dict[str, Any]], optional): A dictionary
            that will be fed into:obj:`openai.ChatCompletion.create()`. If
            :obj:`None`, :obj:`ChatGPTConfig().as_dict()` will be used.
            (default: :obj:`None`)
        api_key (Optional[str], optional): The API key for authenticating with
            the OpenAI service. (default: :obj:`None`)
        url (Optional[str], optional): The url to the OpenAI service.
            (default: :obj:`None`)
        api_version (Optional[str], optional): The api version for the model.
            (default: :obj:`None`)
        azure_deployment_name (Optional[str], optional): The deployment name
            you chose when you deployed an azure model. (default: :obj:`None`)
        token_counter (Optional[BaseTokenCounter], optional): Token counter to
            use for the model. If not provided, :obj:`OpenAITokenCounter`
            will be used. (default: :obj:`None`)

    References:
        https://learn.microsoft.com/en-us/azure/ai-services/openai/
    """

    def __init__(
        self,
        model_type: Union[ModelType, str],
        model_config_dict: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        token_counter: Optional[BaseTokenCounter] = None,
        api_version: Optional[str] = None,
        azure_deployment_name: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if model_config_dict is None:
            model_config_dict = ChatGPTConfig().as_dict()
        api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        url = url or os.environ.get("AZURE_OPENAI_BASE_URL")
        super().__init__(
            model_type, model_config_dict, api_key, url, token_counter
        )

        self.api_version = api_version or os.environ.get("AZURE_API_VERSION")
        self.azure_deployment_name = azure_deployment_name or os.environ.get(
            "AZURE_DEPLOYMENT_NAME"
        )
        if self.api_version is None:
            raise ValueError(
                "Must provide either the `api_version` argument "
                "or `AZURE_API_VERSION` environment variable."
            )
        if self.azure_deployment_name is None:
            raise ValueError(
                "Must provide either the `azure_deployment_name` argument "
                "or `AZURE_DEPLOYMENT_NAME` environment variable."
            )
            
        # 存储工具定义
        self.tools = tools

        self._client = AzureOpenAI(
            azure_endpoint=str(self._url),
            azure_deployment=self.azure_deployment_name,
            api_version=self.api_version,
            api_key=self._api_key,
            timeout=60,
            max_retries=3,
        )

    @property
    def token_counter(self) -> BaseTokenCounter:
        r"""Initialize the token counter for the model backend.

        Returns:
            BaseTokenCounter: The token counter following the model's
                tokenization style.
        """
        if not self._token_counter:
            self._token_counter = OpenAITokenCounter(self.model_type)
        return self._token_counter

    @api_keys_required("AZURE_OPENAI_API_KEY", "AZURE_API_VERSION")
    def run(
        self,
        messages: List[OpenAIMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
        r"""Runs inference of Azure OpenAI chat completion.

        Args:
            messages (List[OpenAIMessage]): Message list with the chat history
                in OpenAI API format.

        Returns:
            Union[ChatCompletion, Stream[ChatCompletionChunk]]:
                `ChatCompletion` in the non-stream mode, or
                `Stream[ChatCompletionChunk]` in the stream mode.
        """
        # 准备API调用参数
        api_params = {
            "messages": messages,
            "model": self.azure_deployment_name,  # type:ignore[arg-type]
            **self.model_config_dict,
        }
        
        # 添加工具参数（如果有）
        tools_to_use = tools if tools is not None else self.tools
        if tools_to_use:
            api_params["tools"] = tools_to_use
            api_params["tool_choice"] = tool_choice or "auto"
        
        # 调用API
        response = self._client.chat.completions.create(**api_params)
        return response

    def check_model_config(self):
        r"""Check whether the model configuration contains any
        unexpected arguments to Azure OpenAI API.

        Raises:
            ValueError: If the model configuration dictionary contains any
                unexpected arguments to Azure OpenAI API.
        """
        # OPENAI_API_PARAMS 是一个集合，需要正确处理
        allowed_params = set(OPENAI_API_PARAMS)  # 创建一个副本
        allowed_params.update(["tools", "tool_choice"])  # 添加额外的参数
        
        for param in self.model_config_dict:
            if param not in allowed_params:
                raise ValueError(
                    f"Unexpected argument `{param}` is "
                    "input into Azure OpenAI model backend."
                )

    @property
    def stream(self) -> bool:
        r"""Returns whether the model is in stream mode,
            which sends partial results each time.
        Returns:
            bool: Whether the model is in stream mode.
        """
        return self.model_config_dict.get("stream", False)
