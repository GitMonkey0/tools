import requests
from transformers import AutoTokenizer
import json
import ast
import re
import time
from .parse import extract_dict_from_text, extract_list_from_text

# 使用模块级变量实现单例模式
_model_id = None
_tokenizer = None

def get_model_info():
    global _model_id, _tokenizer
    
    if _model_id is None or _tokenizer is None:
        response = requests.get("http://localhost:8000/v1/models")
        _model_id = response.json()["data"][0]["id"]
        _tokenizer = AutoTokenizer.from_pretrained(_model_id)
    
    return _model_id, _tokenizer

def classify(prompts, task_desc="判断以下句子的有害性.", labels=["有害", "无害"], mode="long", temperature=0.8, max_tokens=4096):
    if mode == "long":
        system_prompt = f"You are a helpful assistant. {task_desc} 备选标签:{labels}，请一步步分析，最终输出一个形如" + "{'result': '分类结果'}的字典作为最终答案。"
    elif mode == "short":
        system_prompt = f"You are a helpful assistant. {task_desc} 备选标签:{labels}，请仅直接输出一个形如" + "{'result': '分类结果'}的字典作为最终答案。"
    
    results = generate(prompts=prompts, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens)
    
    classification_results = []
    for result in results:
        try:
            extracted_dict = extract_dict_from_text(result)
            if extracted_dict:
                output = extracted_dict.get("result", "解析失败")
                classification_results.append(output)
        except Exception as e:
            print(f"Error parsing result: {e}")
            classification_results.append('解析失败')
    
    return classification_results
    
def generate(prompts, system_prompt="You are a helpful assistant.", temperature=0.8, max_tokens=4096):
    model_id, tokenizer = get_model_info()  # 获取已初始化的模型信息
    
    texts = []
    for prompt in prompts:
        message = [
            {
                "role": "system",
                "content": system_prompt
            },
            {"role": "user", "content": prompt}
        ]
    
        text = tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True
        )
        texts.append(text)
        
    response = requests.post(
        "http://localhost:8000/v1/completions",
        json={
            "model": model_id,
            "prompt": texts,  
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        headers={"Content-Type": "application/json"}
    )
    
    return [choice["text"] for choice in response.json()["choices"]]
    

# if __name__ == "__main__":
#     prompts = ["什么是机器学习？", "深度学习的应用场景有哪些？", "大模型的核心技术是什么？"] * 1000
#     targets = ["否", "否", "是"] * 1000
    
#     # 测试long模式
#     start_long = time.time()
#     results_long = classify(prompts, "以下内容是关于大模型的吗？", ["是", "否"], "long")
#     time_long = time.time() - start_long
    
#     # 测试short模式（会复用已初始化的model_id和tokenizer）
#     start_short = time.time()
#     results_short = classify(prompts, "以下内容是关于大模型的吗？",", "否"], "short")
#     time_short = time.time() - start_short
    
#     # 计算准确率
#     acc_long = sum(1 for r, t in zip(results_long, targets) if r == t) / len(targets)
#     acc_short = sum(1 for r, t in zip(results_short, targets) if r == t) / len(targets)
    
#     print(f"长文本模式(long)耗时: {time_long:.3f}秒, 准确率: {acc_long:.2%}")
#     print(f"短文本模式(short)耗时: {time_short:.3f}秒, 准确率: {acc_short:.2%}")
#     print(f"准确率差异: {abs(acc_long - acc_short):.2%} (长文本模式更准确)")