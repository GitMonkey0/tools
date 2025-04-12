# vLLM 服务部署与使用指南

## 一、环境准备

在 `tools` 目录下，执行以下命令安装依赖：



```
pip install -e.
```

## 二、模型部署

在任意目录下执行以下命令来选择要部署的模型：



```
change\_model Qwen2.5-7B
```

模型对应关系如下：



| 选择的模型名称     | 实际使用的模型                  |
| ----------- | ------------------------ |
| Qwen2.5-7B  | Qwen2.5-7B-Instruct      |
| Qwen2.5-32B | Qwen2.5-32B-Instruct-AWQ |
| Qwen2.5-72B | Qwen2.5-72B-Instruct-AWQ |

若要切换其他模型，在任意目录下执行以下命令，将 `[your_model_name]` 替换为实际的模型名称：



```
change\_model \[your\_model\_name]
```

至此，vLLM 服务部署完成。

## 三、使用方法

### 导入模块

在任意 Python 文件中，使用以下代码导入模块：



```
from my\_package import \*
```

### 函数使用说明

**generate 函数**



```
def generate(prompts, system\_prompt="You are a helpful assistant.", temperature=0.8, max\_tokens=10000, top\_p=0.95):

&#x20;   """

&#x20;   输入字符串列表，输出你部署的服务的结果，是和输入一一对应的字符串列表。

&#x20;   :param prompts: 字符串列表，输入的提示信息

&#x20;   :param system\_prompt: 系统提示信息，默认为 "You are a helpful assistant."

&#x20;   :param temperature: 生成文本的温度参数，默认为 0.8

&#x20;   :param max\_tokens: 生成文本的最大标记数，默认为 10000

&#x20;   :param top\_p: 核采样参数，默认为 0.95

&#x20;   :return: 字符串列表，与输入提示对应的生成结果

&#x20;   """
```

示例代码：



```
prompts = \["请介绍一下 Python 语言", "推荐一些好看的电影"]

results = generate(prompts)

print(results)
```

**classify 函数**



```
def classify(prompts, task\_desc="判断以下句子的有害性.", labels=\["有害", "无害"], mode="long", temperature=0.8, max\_tokens=10000, top\_p=0.95):

&#x20;   """

&#x20;   文本分类，mode 是调整长推理和短推理，需在准确性和耗时之间权衡。

&#x20;   :param prompts: 字符串列表，待分类的文本

&#x20;   :param task\_desc: 任务描述，默认为 "判断以下句子的有害性."

&#x20;   :param labels: 分类标签列表，默认为 \["有害", "无害"]

&#x20;   :param mode: 推理模式，"long" 或 "short"，默认为 "long"

&#x20;   :param temperature: 生成文本的温度参数，默认为 0.8

&#x20;   :param max\_tokens: 生成文本的最大标记数，默认为 10000

&#x20;   :param top\_p: 核采样参数，默认为 0.95

&#x20;   :return: 分类结果

&#x20;   """
```

示例代码：



```
prompts = \["这是一段正常的文本", "这是可能有害的内容"]

classification\_results = classify(prompts)

print(classification\_results)
```

**extract\_dict\_from\_text 函数**



```
def extract\_dict\_from\_text(text):

&#x20;   """

&#x20;   从文本中提取字典结构

&#x20;   :param text: str，包含字典的大模型输出文本

&#x20;   :return: dict，提取到的字典，如果提取失败则返回 None

&#x20;   """
```

示例代码：



```
text = '{"name": "John", "age": 30}'

extracted\_dict = extract\_dict\_from\_text(text)

print(extracted\_dict)
```

**extract\_list\_from\_text 函数**



```
def extract\_list\_from\_text(text):

&#x20;   """

&#x20;   从文本中提取列表结构

&#x20;   :param text: str，包含列表的大模型输出文本

&#x20;   :return: list，提取到的列表，如果提取失败则返回 None

&#x20;   """
```

示例代码：



```
text = "\[1, 2, 3, 'apple', 'banana']"

extracted\_list = extract\_list\_from\_text(text)

print(extracted\_list)
```

**文件操作函数**



```
def open\_json(file):

&#x20;   """

&#x20;   打开 JSON 文件

&#x20;   :param file: 文件路径

&#x20;   :return: 解析后的 JSON 数据

&#x20;   """

def open\_jsonl(file):

&#x20;   """

&#x20;   打开 JSONL 文件

&#x20;   :param file: 文件路径

&#x20;   :return: 包含 JSONL 数据的列表

&#x20;   """

def open\_txt(file):

&#x20;   """

&#x20;   打开 TXT 文件

&#x20;   :param file: 文件路径

&#x20;   :return: TXT 文件内容（字符串）

&#x20;   """

def save\_json(data, file):

&#x20;   """

&#x20;   保存数据为 JSON 文件

&#x20;   :param data: 要保存的数据

&#x20;   :param file: 保存的文件路径

&#x20;   """

def save\_jsonl(data, file):

&#x20;   """

&#x20;   保存数据为 JSONL 文件

&#x20;   :param data: 要保存的数据列表

&#x20;   :param file: 保存的文件路径

&#x20;   """

def save\_txt(data, file):

&#x20;   """

&#x20;   保存数据为 TXT 文件

&#x20;   :param data: 要保存的字符串数据

&#x20;   :param file: 保存的文件路径

&#x20;   """
```