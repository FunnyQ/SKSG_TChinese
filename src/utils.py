"""
工具函數模組 - 包含各種輔助函數和類別
"""
import os
import sys
import ctypes
from io import BytesIO
from typing import Any


def sanitize_filename(name: str) -> str:
    """清理檔名，移除非法字元"""
    return "".join(c for c in name if c.isalnum() or c in " .-_()").replace(" ", "_")


def is_admin() -> bool:
    """檢查是否具有管理員權限（僅限 Windows）"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin() -> None:
    """以管理員權限重新執行程式（僅限 Windows）"""
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


class FileWrapper:
    """
    檔案包裝器，用於在 Unity 資產處理中包裝新的資料流

    這個類別允許我們創建一個新的資料流來替換原始檔案的內容，
    同時保持對原始檔案物件的引用以進行其他操作。
    """

    def __init__(self, original_file: Any, new_data_stream: BytesIO) -> None:
        """
        初始化檔案包裝器

        Args:
            original_file: 原始檔案物件
            new_data_stream: 新的資料流
        """
        self._original = original_file
        self._stream = new_data_stream

    @property
    def Length(self) -> int:
        """獲取資料流長度"""
        return len(self._stream.getbuffer())

    @property
    def Position(self) -> int:
        """獲取當前讀取位置"""
        return self._stream.tell()

    @Position.setter
    def Position(self, value: int) -> None:
        """設置讀取位置"""
        self._stream.seek(value)

    def read_bytes(self, length: int) -> bytes:
        """讀取指定長度的位元組"""
        return self._stream.read(length)

    def save(self) -> bytes:
        """
        保存資料並重置位置到開頭

        Returns:
            完整的資料內容
        """
        self.Position = 0
        return self._stream.read()

    def __getattr__(self, name: str) -> Any:
        """代理其他屬性到原始檔案物件"""
        return getattr(self._original, name)
