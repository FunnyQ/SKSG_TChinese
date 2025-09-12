#!/usr/bin/env python3
"""
新版本啟動腳本 - 使用重構後的模組架構
"""
import sys
import os

# 確保可以找到 src 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
