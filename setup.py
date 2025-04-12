from setuptools import setup, find_packages
import os

# 动态获取项目根目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

setup(
    name="my_package",
    version="1.0",
    packages=find_packages(),
    # 包含非Python文件（如Shell脚本）
    include_package_data=True,
    package_data={
        "my_package": ["my_package/scripts/*.sh"],  # 打包 scripts 目录下的所有 .sh 文件
    },
    # 注册命令行工具
    entry_points={
        "console_scripts": [
            "change_model=my_package.change_model:main",  # 通过Python调用Shell脚本
        ],
    },
)