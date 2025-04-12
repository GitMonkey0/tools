首先，在tools目录下执行:
pip install -e .

随后，在任意目录下执行：
change_model Qwen2.5-7B
你可以选择其他模型，对应关系如：
["Qwen2.5-7B"]="Qwen2.5-7B-Instruct"
["Qwen2.5-32B"]="Qwen2.5-32B-Instruct-AWQ"
["Qwen2.5-72B"]="Qwen2.5-72B-Instruct-AWQ"

如需切换其他模型，在任意目录下执行以下命令，例如：
change_model [your_model_name]

到此为止，vLLM服务就部署好了。

下一步，在任意python文件中导入：
from my_package import *

于是你可以使用以下函数：
def generate(prompts, system_prompt="You are a helpful assistant.", 
             temperature=0.8, max_tokens=10000, top_p=0.95):
输入字符串列表，输出你部署的服务的结果，是和输入一一对应的字符串列表。

def classify(prompts, task_desc="判断以下句子的有害性.", labels=["有害", "无害"], 
             mode="long", temperature=0.8, max_tokens=10000, top_p=0.95):
文本分类，mode是调整长推理和短推理，需在准确性和耗时之间权衡。

def extract_dict_from_text(text):
    """
    从文本中提取字典结构

    参数:
        text (str): 包含字典的大模型输出文本

    返回:
        dict: 提取到的字典，如果提取失败则返回None
    """

def extract_list_from_text(text):
    """
    从文本中提取列表结构

    参数:
        text (str): 包含列表的大模型输出文本

    返回:
        list: 提取到的列表，如果提取失败则返回None
    """

以及：
def open_json(file):

def open_jsonl(file):

def open_txt(file):

def save_json(data, file):

def save_jsonl(data, file):

def save_txt(data, file):