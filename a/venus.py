import os
from typing import Optional, Callable, Iterable, Any, List
from langchain import VenusLLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from .task import run_concurrently
from .parse import extract_dict, extract_list


class Venus:
    def __init__(self, model_name: str = 'belle-13b-2m',
                 secret_id: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 domain: str = "http://v2.open.venus.oa.com"):
        """
        初始化 Venus 类，加载指定的 VenusLLM 模型。

        :param model_name: 模型名称，默认为 'belle-13b-2m'。
        :param secret_id: API 密钥 ID，如果为 None 则从环境变量获取。
        :param secret_key: API 密钥，如果为 None 则从环境变量获取。
        :param domain: 模型服务的基地址。
        """
        self.secret_id = secret_id or os.environ.get("ENV_VENUS_OPENAPI_SECRET_ID")
        self.secret_key = secret_key or os.environ.get("ENV_VENUS_OPENAPI_SECRET_KEY")
        self.domain = domain
        self.model_name = model_name

        # 初始化对话链
        self.conversation_chain = self._build_conversation_chain()

    def _build_conversation_chain(self) -> ConversationChain:
        """
        构建 ConversationChain。

        :return: 初始化的 ConversationChain 实例。
        """
        llm = VenusLLM(
            venus_openapi_secret_id=self.secret_id,
            venus_openapi_secret_key=self.secret_key,
            venus_openapi_domain=self.domain,
            model_name=self.model_name
        )
        return ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationBufferMemory()
        )

    def _create_prompts(self, inputs: List[str]) -> List[str]:
        """
        为每个输入创建提示词。这里直接使用输入作为提示词。

        :param inputs: 输入数据列表。
        :return: 提示词列表。
        """
        return inputs

    def _generate_tasks(self, prompts: List[str]) -> List[Callable[[], Any]]:
        """
        为每个提示词创建任务。由于 ConversationChain 不支持直接并行调用，
        这里我们模拟任务生成，实际调用时需要串行处理。

        :param prompts: 提示词列表。
        :return: 任务列表，每个任务是一个无参函数。
        """
        # 注意：由于 ConversationChain 的状态性，无法真正并行处理
        # 这里返回的任务列表仅用于模拟，并行处理需要特殊处理
        return [lambda prompt=prompt: self._process_prompt(prompt) for prompt in prompts]

    def _process_prompt(self, prompt: str) -> str:
        """
        处理单个提示词，调用对话链。

        :param prompt: 输入提示词。
        :return: 对话链的响应。
        """
        # 重置内存以避免状态污染（仅用于演示，并不推荐在实际对话中使用）
        # 在真实场景中，ConversationChain 的内存是累积的
        self.conversation_chain.memory.clear()

        # 调用对话链
        response = self.conversation_chain(prompt)
        return response['response']

    def generate(
            self,
            inputs: List[str],
            ensure_returned: Optional[str] = None,
            max_workers: int = 4,
            temperature: float = 0.8,  # VenusLLM 可能不支持这些参数
            max_tokens: int = 10000,  # VenusLLM 可能不支持这些参数
            top_p: float = 0.95  # VenusLLM 可能不支持这些参数
    ) -> List[str]:
        """
        并行生成多个输入的响应。注意：由于 ConversationChain 的状态性，
        这里的并行处理是模拟的，实际调用时可能需要串行处理。

        :param inputs: 输入数据列表。
        :param ensure_returned: 指定验证类型 ("list" 或 "dict")。如果为 None，则不进行验证。
        :param max_workers: 最大并行工作数（仅用于模拟）。
        :param temperature: 温度参数（可能不支持）。
        :param max_tokens: 最大 token 数（可能不支持）。
        :param top_p: Top-p 参数（可能不支持）。
        :return: 响应文本列表。
        """
        # 注意：ConversationChain 的状态性使得真正的并行处理变得复杂
        # 这里我们模拟并行处理，但实际上需要串行调用

        # Step 1: 创建提示词
        prompts = self._create_prompts(inputs)

        # Step 2: 为每个提示词创建任务
        tasks = self._generate_tasks(prompts)

        # 由于 ConversationChain 的状态性问题，这里改为串行处理
        # 如果需要真正的并行处理，可能需要为每个输入创建独立的 ConversationChain 实例
        # 但这会消耗更多资源
        results = []
        for task in tasks:
            try:
                result = task()
                results.append(result)
            except Exception as e:
                print(f"Error processing prompt: {e}")
                results.append("Error occurred during processing")

        # 如果需要验证结果
        if ensure_returned == "dict":
            validation_func = extract_dict
        elif ensure_returned == "list":
            validation_func = extract_list
        else:
            validation_func = None

        if max_workers > 1:
            results = run_concurrently(tasks, max_workers=max_workers, validation_func=validation_func)
        else:
            results = [task() for task in tasks]

        return results


# 示例使用
if __name__ == "__main__":
    # 初始化 VenusWBZ
    # 注意：需要设置环境变量 ENV_VENUS_OPENAPI_SECRET_ID 和 ENV_VENUS_OPENAPI_SECRET_KEY
    # 或者直接传入 secret_id 和 secret_key
    llm_generator = Venus(
        model_name='belle-13b-2m',
        # secret_id="your_secret_id",  # 如果不使用环境变量
        # secret_key="your_secret_key"  # 如果不使用环境变量
    )

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
    # 注意：由于 ConversationChain 的状态性，并行处理可能不会按预期工作
    # 这里我们使用串行处理
    outputs = []
    for input_text in inputs:
        response = llm_generator.conversation_chain(input_text)
        outputs.append(response['response'])

    # 或者使用 generate 方法（但注意并行处理的问题）
    # outputs = llm_generator.generate(inputs, max_workers=1)  # 设置为1以避免并行问题

    # 打印结果
    for i, output in enumerate(outputs, 1):
        print(f"Input {i}: {inputs[i - 1]}")
        print(f"Output {i}: {output}\n")