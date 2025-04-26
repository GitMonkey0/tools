import json

def open_json(file):
    with open(file, "r", encoding="utf8") as f:
        data = json.load(f)
    return data

def open_jsonl(file):
    data = []
    with open(file, "r", encoding="utf8") as f:
        for line in f:
            _data = json.loads(f)
            data.append(_data)
    return data

def open_txt(file):
    with open(file, "r", encoding="utf8") as f:
        data = f.readlines()
    return data

def save_json(data, file):
    with open(file, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved data to {file}!")

def save_jsonl(data, file):
    with open(file, "w", encoding="utf8") as f:
        for _data in data:
            f.write(json.dumps(_data, ensure_ascii=False) + '\n')
        print(f"Saved data to {file}!")

def save_txt(data, file):
    with open(file, "w", encoding="utf8") as f:
        for _data in data:
            f.write(_data + '\n')
        print(f"Saved data to {file}!")