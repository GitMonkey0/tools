from flask import Flask, request, jsonify
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from parse import extract_dict_from_text, extract_list_from_text

app = Flask(__name__)

# 原始初始化代码（完全一致）
model_name = "/data/lht/ckpt/Qwen2.5-32B-Instruct-AWQ"
llm = LLM(
    model=model_name,
    max_model_len=10000,
    gpu_memory_utilization=0.8, 
    tensor_parallel_size=4
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 原始classify函数（一字不改）
def classify(prompts, task_desc="判断以下句子的有害性.", labels=["有害", "无害"], 
             mode="long", temperature=0.8, max_tokens=10000, top_p=0.95):
    if mode == "long":
        system_prompt = f"You are a helpful assistant. {task_desc} 备选标签:{labels}，请一步步分析，最终输出一个形如" + "{'result': '分类结果'}的字典作为最终答案。"
    elif mode == "short":
        system_prompt = f"You are a helpful assistant. {task_desc} 备选标签:{labels}，请仅直接输出一个形如" + "{'result': '分类结果'}的字典作为最终答案。"
    
    results = generate(prompts, system_prompt, temperature, max_tokens)
    
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

# 原始generate函数（一字不改）
def generate(prompts, system_prompt="You are a helpful assistant.", 
             temperature=0.8, max_tokens=10000, top_p=0.95):
    texts = []
    for prompt in prompts:
        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        texts.append(tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True
        ))
    
    outputs = llm.generate(
        prompts=texts,
        sampling_params=SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
    )
    return [output.outputs[0].text for output in outputs]

# 仅添加最简Flask路由
@app.route('/classify', methods=['POST'])
def api_classify():
    data = request.json
    results = classify(
        prompts=data['prompts'],
        task_desc=data.get('task_desc'),
        labels=data.get('labels'),
        mode=data.get('mode', 'long'),
        temperature=float(data.get('temperature', 0.8)),
        max_tokens=int(data.get('max_tokens', 10000))
    )
    return jsonify({"results": results})

@app.route('/generate', methods=['POST'])
def api_generate():
    data = request.json
    results = generate(
        prompts=data['prompts'],
        system_prompt=data.get('system_prompt', 'You are a helpful assistant.'),
        temperature=float(data.get('temperature', 0.8)),
        max_tokens=int(data.get('max_tokens', 10000))
    )
    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)