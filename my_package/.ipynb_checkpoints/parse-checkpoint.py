import re
import json
import ast


def extract_dict_from_text(text):
    """
    从文本中提取字典结构

    参数:
        text (str): 包含字典的大模型输出文本

    返回:
        dict: 提取到的字典，如果提取失败则返回None
    """
    # 尝试直接解析为字典（适用于纯字典输出）
    try:
        # 处理可能存在的json字符串
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()

        # 尝试直接解析为字典
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # 如果直接解析失败，尝试在文本中查找字典模式
    pattern = r'\{[\s\S]*?\}'
    matches = re.findall(pattern, text)

    for match in matches:
        try:
            # 使用ast.literal_eval安全地评估字符串
            result = ast.literal_eval(match)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            continue

    # 如果以上方法都失败，尝试更宽松的解析
    try:
        # 去除可能的解释性前缀
        lines = text.split('\n')
        dict_lines = []
        in_dict = False

        for line in lines:
            if line.strip().startswith('{') or in_dict:
                in_dict = True
                dict_lines.append(line)
                if line.strip().endswith('}'):
                    break

        dict_str = '\n'.join(dict_lines)
        result = ast.literal_eval(dict_str)
        if isinstance(result, dict):
            return result
    except (ValueError, SyntaxError):
        pass

    return None


def extract_list_from_text(text):
    """
    从文本中提取列表结构

    参数:
        text (str): 包含列表的大模型输出文本

    返回:
        list: 提取到的列表，如果提取失败则返回None
    """
    # 尝试直接解析为列表（适用于纯列表输出）
    try:
        # 处理可能存在的json字符串
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()

        # 尝试直接解析为列表
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # 如果直接解析失败，尝试在文本中查找列表模式
    pattern = r'$$[\s\S]*?$$'
    matches = re.findall(pattern, text)

    for match in matches:
        try:
            # 使用ast.literal_eval安全地评估字符串
            result = ast.literal_eval(match)
            if isinstance(result, list):
                return result
        except (ValueError, SyntaxError):
            continue

    # 如果以上方法都失败，尝试更宽松的解析
    try:
        # 去除可能的解释性前缀
        lines = text.split('\n')
        list_lines = []
        in_list = False

        for line in lines:
            if line.strip().startswith('[') or in_list:
                in_list = True
                list_lines.append(line)
                if line.strip().endswith(']'):
                    break

        list_str = '\n'.join(list_lines)
        result = ast.literal_eval(list_str)
        if isinstance(result, list):
            return result
    except (ValueError, SyntaxError):
        pass

    return None