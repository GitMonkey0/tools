from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
from typing import Optional, Dict, List
from .parse import extract_dict, extract_list

class VLLMGenerator:
    def __init__(
        self,
        model_name: str,
        max_model_len: int = 10000,
        gpu_memory_utilization: float = 0.9,
        tensor_parallel_size: int = 1,
        enable_lora: bool = False
    ):
        """
        Initialize the VLLMGenerator with the specified model and configurations.

        :param model_name: Name of the model to load.
        :param max_model_len: Maximum length of the model's context.
        :param gpu_memory_utilization: Fraction of GPU memory to utilize.
        :param tensor_parallel_size: Number of GPUs to use for tensor parallelism.
        :param enable_lora: Whether to enable LoRA support.
        """
        self.llm = LLM(
            model=model_name,
            max_model_len=max_model_len,
            gpu_memory_utilization=gpu_memory_utilization,
            tensor_parallel_size=tensor_parallel_size,
            enable_lora=enable_lora
        )

    def _create_prompts(self, inputs: List[str], system_prompt: str) -> List[str]:
        """
        Create chat prompts for each input using the system prompt.

        :param inputs: List of input prompts.
        :param system_prompt: System prompt to prepend to each input.
        :return: List of formatted prompts.
        """
        tokenizer = self.llm.get_tokenizer()
        prompts = []
        for data in inputs:
            message = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data}
            ]
            prompt = tokenizer.apply_chat_template(
                message,
                tokenize=False,
                add_generation_prompt=True
            )
            prompts.append(prompt)
        return prompts

    def _generate_initial_responses(self, prompts: List[str], temperature: float, max_tokens: int, top_p: float, lora_path: Optional[str]) -> List[str]:
        """
        Generate initial responses for the provided prompts.

        :param prompts: List of formatted prompts.
        :param temperature: Temperature parameter for sampling.
        :param max_tokens: Maximum number of tokens to generate.
        :param top_p: Top-p parameter for sampling.
        :param lora_path: Path to the LoRA adapter (optional).
        :return: List of generated response texts.
        """
        outputs = self.llm.generate(
            prompts=prompts,
            sampling_params=SamplingParams(
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            ),
            lora_request=LoRARequest("adapter", 1, lora_path) if lora_path is not None else None
        )
        return [output.outputs[0].text for output in outputs]

    def _validate_responses(self, responses: List[str], ensure_returned: Optional[str]) -> List[int]:
        """
        Validate the generated responses based on the `ensure_returned` parameter.

        :param responses: List of generated response texts.
        :param ensure_returned: Specify validation type ("list" or "dict"). If None, no validation is performed.
        :return: List of indices that need retrying.
        """
        if ensure_returned is None:
            return []

        validation_func = extract_dict if ensure_returned == "dict" else extract_list if ensure_returned == "list" else None
        if validation_func is None:
            return []

        # Identify indices that do not meet the validation criteria
        return [i for i, response in enumerate(responses) if not validation_func(response)]

    def _retry_failed_responses(
            self,
            inputs: List[str],
            system_prompt: str,
            failed_indices: List[int],
            temperature: float,
            max_tokens: int,
            top_p: float,
            lora_path: Optional[str]
    ) -> List[str]:
        retry_inputs = [inputs[i] for i in failed_indices]
        retry_prompts = self._create_prompts(retry_inputs, system_prompt)
        retry_outputs = self._generate_initial_responses(retry_prompts, temperature, max_tokens, top_p, lora_path)

        return [retry_outputs[failed_indices.index(i)] if i in failed_indices else "" for i in range(len(inputs))]

    def generate(
        self,
        inputs: List[str],
        system_prompt: str = "You are a helpful assistant.",
        ensure_returned: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: int = 10000,
        top_p: float = 0.95,
        lora_path: Optional[str] = None
    ) -> List[str]:
        """
        Parallelly generate responses for multiple inputs, supporting validation with `ensure_returned`.

        :param inputs: List of input prompts.
        :param system_prompt: System prompt to prepend to each input.
        :param ensure_returned: Specify validation type ("list" or "dict"). If None, no validation is performed.
        :param temperature: Temperature parameter for sampling.
        :param max_tokens: Maximum number of tokens to generate.
        :param top_p: Top-p parameter for sampling.
        :param lora_path: Path to the LoRA adapter (optional).
        :return: List of generated response texts.
        """
        # Step 1: Create prompts
        prompts = self._create_prompts(inputs, system_prompt)

        # Step 2: Generate initial responses
        results = self._generate_initial_responses(prompts, temperature, max_tokens, top_p, lora_path)

        # Step 3: Validate responses and determine retries
        if ensure_returned is not None:
            to_retry = self._validate_responses(results, ensure_returned)
            while to_retry:
                # Step 4: Retry failed responses
                retry_results = self._retry_failed_responses(
                    inputs=inputs,
                    system_prompt=system_prompt,
                    failed_indices=to_retry,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    lora_path=lora_path
                )

                # Step 5: Update results and determine new retries
                new_to_retry = []
                for idx in to_retry:
                    if ensure_returned == "dict":
                        validation_func = extract_dict
                    elif ensure_returned == "list":
                        validation_func = extract_list
                    else:
                        validation_func = None

                    if validation_func is not None and validation_func(retry_results[idx]):
                        results[idx] = retry_results[idx]
                    else:
                        results[idx] = ""  # Mark as invalid for further retries
                        new_to_retry.append(idx)

                to_retry = new_to_retry

        return results