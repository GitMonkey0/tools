import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='AI Model Changer')
    parser.add_argument('model_name')
    
    args = parser.parse_args()
    
    # 获取脚本绝对路径
    script_path = Path(__file__).parent / "scripts/deploy.sh"
    
    # 执行shell脚本并传递参数
    subprocess.run(["sh", str(script_path), args.model_name], check=True)

if __name__ == "__main__":
    main()