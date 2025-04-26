from setuptools import setup, find_packages
import os

# 动态获取项目根目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

setup(
    name="a",
    version="1.0",
    packages=find_packages()
)