vLLM 服务部署与使用指南
一、环境准备
在 tools 目录下，执行以下命令安装依赖：
bash
pip install -e.

二、模型部署
在任意目录下执行以下命令来选择要部署的模型：
bash
change_model Qwen2.5-7B

模型对应关系如下：
选择的模型名称	实际使用的模型
Qwen2.5-7B	Qwen2.5-7B-Instruct
Qwen2.5-32B	Qwen2.5-32B-Instruct-AWQ
Qwen2.5-72B	Qwen2.5-72B-Instruct-AWQ
若要切换其他模型，在任意目录下执行以下命令，将 [your_model_name] 替换为实际的模型名称：
bash
change_model [your_model_name]
至此，vLLM 服务部署完成。
三、使用方法
导入模块
在任意 Python 文件中，使用以下代码导入模块：
python
from my_package import *
函数使用说明
1. generate 函数
python
def generate(prompts, system_prompt="You are a helpful assistant.", temperature=0.8, max_tokens=10000, top_p=0.95):
    """
    输入字符串列表，输出你部署的服务的结果，是和输入一一对应的字符串列表。
    :param prompts: 字符串列表，输入的提示信息
    :param system_prompt: 系统提示信息，默认为 "You are a helpful assistant."
    :param temperature: 生成文本的温度参数，默认为 0.8
    :param max_tokens: 生成文本的最大标记数，默认为 10000
    :param top_p: 核采样参数，默认为 0.95
    :return: 字符串列表，与输入提示对应的生成结果
    """
示例代码：
python
prompts = ["请介绍一下 Python 语言", "推荐一些好看的电影"]
results = generate(prompts)
print(results)
2. classify 函数
python
def classify(prompts, task_desc="判断以下句子的有害性.", labels=["有害", "无害"], mode="long", temperature=0.8, max_tokens=10000, top_p=0.95):
    """
    文本分类，mode 是调整长推理和短推理，需在准确性和耗时之间权衡。
    :param prompts: 字符串列表，待分类的文本
    :param task_desc: 任务描述，默认为 "判断以下句子的有害性."
    :param labels: 分类标签列表，默认为 ["有害", "无害"]
    :param mode: 推理模式，"long" 或 "short"，默认为 "long"
    :param temperature: 生成文本的温度参数，默认为 0.8
    :param max_tokens: 生成文本的最大标记数，默认为 10000
    :param top_p: 核采样参数，默认为 0.95
    :return: 分类结果
    """
示例代码：
python
prompts = ["这是一段正常的文本", "这是可能有害的内容"]
classification_results = classify(prompts)
print(classification_results)
3. extract_dict_from_text 函数
python
def extract_dict_from_text(text):
    """
    从文本中提取字典结构
    :param text: str，包含字典的大模型输出文本
    :return: dict，提取到的字典，如果提取失败则返回 None
    """
示例代码：
python
text = '{"name": "John", "age": 30}'
extracted_dict = extract_dict_from_text(text)
print(extracted_dict)
4. extract_list_from_text 函数
python
def extract_list_from_text(text):
    """
    从文本中提取列表结构
    :param text: str，包含列表的大模型输出文本
    :return: list，提取到的列表，如果提取失败则返回 None
    """
示例代码：
python
text = "[1, 2, 3, 'apple', 'banana']"
extracted_list = extract_list_from_text(text)
print(extracted_list)
5. 文件操作函数
python
def open_json(file):
    """
    打开 JSON 文件
    :param file: 文件路径
    :return: 解析后的 JSON 数据
    """

def open_jsonl(file):
    """
    打开 JSONL 文件
    :param file: 文件路径
    :return: 包含 JSONL 数据的列表
    """

def open_txt(file):
    """
    打开 TXT 文件
    :param file: 文件路径
    :return: TXT 文件内容（字符串）
    """

def save_json(data, file):
    """
    保存数据为 JSON 文件
    :param data: 要保存的数据
    :param file: 保存的文件路径
    """

def save_jsonl(data, file):
    """
    保存数据为 JSONL 文件
    :param data: 要保存的数据列表
    :param file: 保存的文件路径
    """

def save_txt(data, file):
    """
    保存数据为 TXT 文件
    :param data: 要保存的字符串数据
    :param file: 保存的文件路径
    """