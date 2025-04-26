import json
from typing import Optional, Dict, List

def extract_dict(s: str) -> Optional[Dict]:
    """
    遍历字符串，提取第一个合法的 JSON 对象（用 {} 包裹的部分）。
    如果找到则返回解析后的 dict，否则返回 None。
    """
    stack = []
    start = -1

    for i, char in enumerate(s):
        if char == '{':
            if not stack:
                start = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    json_str = s[start:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

    return None

def extract_list(s: str) -> Optional[List]:
    """
    遍历字符串，提取第一个合法的 JSON 数组（用 [] 包裹的部分）。
    如果找到则返回解析后的 list，否则返回 None。
    """
    stack = []
    start = -1

    for i, char in enumerate(s):
        if char == '[':
            if not stack:
                start = i
            stack.append(char)
        elif char == ']':
            if stack:
                stack.pop()
                if not stack:
                    json_str = s[start:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass

    return None
