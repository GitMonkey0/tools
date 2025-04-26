from langchain_openai import ChatOpenAI
from .task import run_concurrently
from typing import Optional, Callable, Iterable, Any, List, Dict
from .parse import extract_dict, extract_list


class WBZ:
    def __init__(self, model: str = "deepseek-v3", api_key: str = "sk-darryjdkfny2ji6l", base_url: str = "https://cloud.infini-ai.com/maas/v1/"):
        """
        初始化 WBZGenerator 类，加载指定的语言模型。

        :param model: 模型名称，默认为 "deepseek-v3"。
        :param api_key: API 密钥。
        :param base_url: 模型服务的基地址。
        """
        self.llm = ChatOpenAI(
            base_url=base_url,
            model=model,
            api_key=api_key
        )

    def _create_prompts(self, inputs: List[str], system_prompt: str) -> List[List[Dict[str, str]]]:
        """
        为每个输入创建提示词。

        :param inputs: 输入数据列表。
        :param system_prompt: 系统提示。
        :return: 包含角色和内容的提示词列表。
        """
        return [
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data}
            ]
            for data in inputs
        ]

    def _generate_tasks(self, prompts: List[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        """
        为每个提示词创建任务。

        :param prompts: 提示词列表。
        :return: 任务列表。
        """
        return [
            {
                'func': self.infer,
                'args': [prompt],  # 注意这里 args 是一个列表，包含 prompt
            }
            for prompt in prompts
        ]

    def infer(self, prompt: List[Dict[str, str]]) -> str:
        """
        调用 LLM 推理 API。

        :param prompt: 包含角色和内容的列表。
        :return: 推理结果的字符串。
        """
        ai_msg = self.llm.invoke(prompt)
        return ai_msg.content

    def generate(
        self,
        inputs: List[str],
        system_prompt: str = "You are a helpful assistant.",
        ensure_returned: Optional[str] = None,
        max_workers: int = 4,
        temperature: float = 0.8,
        max_tokens: int = 10000,
        top_p: float = 0.95
    ) -> List[str]:
        """
        并行生成多个输入的响应，支持验证和重试机制。

        :param inputs: 输入数据列表。
        :param system_prompt: 系统提示。
        :param ensure_returned: 指定验证类型 ("list" 或 "dict")。如果为 None，则不进行验证。
        :param max_workers: 最大并行工作数。
        :param temperature: 温度参数。
        :param max_tokens: 最大 token 数。
        :param top_p: Top-p 参数。
        :return: 响应文本列表。
        """
        # Step 1: 创建提示词
        prompts = self._create_prompts(inputs, system_prompt)

        # Step 2: 为每个提示词创建任务
        tasks = self._generate_tasks(prompts)

        # Step 3: 运行任务并行处理
        if ensure_returned == "dict":
            validation_func = extract_dict
        elif ensure_returned == "list":
            validation_func = extract_list
        else:
            validation_func = None

        results = run_concurrently(tasks, max_workers=max_workers, validation_func=validation_func)

        return results


# 示例使用
if __name__ == "__main__":
    # 初始化 WBZGenerator
    llm_generator = WBZ(model="deepseek-v3")

    # 输入数据
    inputs = [
        "Hello, how are you?",
        "What's the weather today?",
        "Tell me a joke.",
        "Explain quantum mechanics in simple terms.",
        "Translate 'Hello' to French.",
        "Write a short poem about the ocean.",
        "What is the capital of France?",
        "Can you summarize the plot of 'Pride and Prejudice'?"
    ]

    # 生成响应
    outputs = llm_generator.generate(
        inputs=inputs,
        system_prompt="You are a helpful assistant.",
        max_workers=4
    )

    # 打印结果
    for i, output in enumerate(outputs, 1):
        print(f"Input {i}: {inputs[i - 1]}")
        print(f"Output {i}: {output}\n")