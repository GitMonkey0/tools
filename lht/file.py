import json

def open_json(file, encoding="utf8"):
    with open(file, "r", encoding=encoding) as f:
        data = json.load(f)
    return data

def open_jsonl(file, encoding="utf8"):
    data = []
    with open(file, "r", encoding=encoding) as f:
        for line in f:
            _data = json.loads(line)
            data.append(_data)
    return data

def open_txt(file, encoding="utf8"):
    with open(file, "r", encoding=encoding) as f:
        data = f.readlines()
        data = [_data.strip() for _data in data]
    return data

def save_json(data, file, encoding="utf8"):
    with open(file, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved data to {file}!")

def save_jsonl(data, file, encoding="utf8"):
    with open(file, "w", encoding=encoding) as f:
        for _data in data:
            f.write(json.dumps(_data, ensure_ascii=False) + '\n')
        print(f"Saved data to {file}!")

def save_txt(data, file, encoding="utf8"):
    with open(file, "w", encoding=encoding) as f:
        for _data in data:
            f.write(_data + '\n')
        print(f"Saved data to {file}!")