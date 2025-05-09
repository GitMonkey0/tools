from typing import List
from langchain_openai import ChatOpenAI
from .batch import run


class AI:
    def __init__(
            self,
            api_key: str = "9183dJxR3OrJvmz4oBFTJ7Y3@1641",
            base_url: str = "http://v2.open.venus.oa.com/llmproxy",
            model: str = "qwen2.5-7b-instruct",
            max_workers: int = 100
    ):
        self.client = ChatOpenAI(model=model, base_url=base_url, api_key=api_key)
        self.max_workers = max_workers
        self.api_key_choices = ["9183dJxR3OrJvmz4oBFTJ7Y3@1641", "sk-darryjdkfny2ji6l"]
        self.base_url_choices = ["http://v2.open.venus.oa.com/llmproxy", "https://cloud.infini-ai.com/maas/v1/"]

    def _request(self, messages: List[dict], thinking_enable: bool = False) -> str:
        """单个请求处理（会被run函数自动重试）"""
        response = self.client.invoke(
            input=messages,
            extra_body={"thinking_enabled": thinking_enable}
        )
        return response.content

    def batch_process(
            self,
            inputs: List[str],
            system_prompt: str = "You are a helpful assistant.",
            thinking_enable: bool = False,
            max_workers: int = None
    ) -> List[str]:
        """批量处理入口"""
        params_list = [{
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_str}
            ],
            "thinking_enable": thinking_enable
        } for input_str in inputs]

        workers = max_workers if max_workers is not None else self.max_workers
        return run(self._request, params_list, max_workers=workers)