import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# 從新的模組結構匯入函數
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    # 嘗試從新模組導入
    from src.utils import sanitize_filename, is_admin, FileWrapper
    from src.config import get_base_path
except ImportError:
    # 如果新模組不可用，回退到舊的 sk_cht
    from sk_cht import sanitize_filename, is_admin, get_base_path, FileWrapper
from io import BytesIO


class TestUtilityFunctions:
    """測試工具函數"""

    def test_sanitize_filename_基本字元(self):
        """測試檔名清理 - 保留允許的字元"""
        result = sanitize_filename("chinese_body.json")
        assert result == "chinese_body.json"

    def test_sanitize_filename_非法字元(self):
        """測試檔名清理 - 移除非法字元"""
        result = sanitize_filename("file<>:\"|?*.txt")
        assert result == "file.txt"

    def test_sanitize_filename_空格處理(self):
        """測試檔名清理 - 空格轉換為底線"""
        result = sanitize_filename("chinese body bold Atlas.png")
        assert result == "chinese_body_bold_Atlas.png"

    def test_sanitize_filename_中文字元保留(self):
        """測試檔名清理 - 中文字元實際行為"""
        result = sanitize_filename("中文檔名test.txt")
        # 檢查實際行為 - 中文字元是 isalnum() 所以會被保留
        assert result == "中文檔名test.txt"

    def test_sanitize_filename_空字串(self):
        """測試檔名清理 - 空字串輸入"""
        result = sanitize_filename("")
        assert result == ""

    def test_sanitize_filename_特殊字元組合(self):
        """測試檔名清理 - 複雜案例"""
        result = sanitize_filename("do_not_use_chinese_body_bold Atlas.png")
        assert result == "do_not_use_chinese_body_bold_Atlas.png"


class TestAdminCheck:
    """測試權限檢查功能"""

    def test_is_admin_windows_成功(self):
        """測試 Windows 系統管理員檢查 - 成功案例"""
        with patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = True
            result = is_admin()
            assert result is True

    def test_is_admin_windows_失敗(self):
        """測試 Windows 系統管理員檢查 - 失敗案例"""
        with patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = False
            result = is_admin()
            assert result is False

    def test_is_admin_異常處理(self):
        """測試權限檢查異常處理"""
        with patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.side_effect = Exception("權限檢查失敗")
            result = is_admin()
            assert result is False


class TestGetBasePath:
    """測試基礎路徑獲取"""

    def test_get_base_path_開發模式(self):
        """測試開發模式下的路徑獲取"""
        # 在非打包模式下，函數應該返回包含 sk_cht.py 的目錄
        result = get_base_path()
        assert os.path.exists(result)
        assert result.endswith('SKSG_TChinese')

    def test_get_base_path_打包模式模擬(self):
        """測試打包模式的模擬行為"""
        # 模擬打包環境
        mock_sys = MagicMock()
        mock_sys.frozen = True
        mock_sys._MEIPASS = '/temp/extracted'

        with patch('sk_cht.sys', mock_sys), \
             patch('sk_cht.getattr') as mock_getattr, \
             patch('sk_cht.hasattr', return_value=True):

            mock_getattr.side_effect = lambda obj, name, default: getattr(mock_sys, name, default)
            result = get_base_path()
            assert result == '/temp/extracted'


class TestFileWrapper:
    """測試 FileWrapper 類別"""

    def test_file_wrapper_初始化(self):
        """測試 FileWrapper 初始化"""
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        assert wrapper._original == original_file
        assert wrapper._stream == data_stream

    def test_file_wrapper_length_屬性(self):
        """測試 FileWrapper Length 屬性"""
        original_file = MagicMock()
        test_data = b"test data with some content"
        data_stream = BytesIO(test_data)
        wrapper = FileWrapper(original_file, data_stream)

        assert wrapper.Length == len(test_data)

    def test_file_wrapper_position_屬性(self):
        """測試 FileWrapper Position 屬性讀寫"""
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        # 測試初始位置
        assert wrapper.Position == 0

        # 測試設置位置
        wrapper.Position = 5
        assert wrapper.Position == 5
        assert data_stream.tell() == 5

    def test_file_wrapper_read_bytes(self):
        """測試 FileWrapper read_bytes 方法"""
        original_file = MagicMock()
        test_data = b"test data for reading"
        data_stream = BytesIO(test_data)
        wrapper = FileWrapper(original_file, data_stream)

        result = wrapper.read_bytes(4)
        assert result == b"test"
        assert wrapper.Position == 4

    def test_file_wrapper_save_方法(self):
        """測試 FileWrapper save 方法"""
        original_file = MagicMock()
        test_data = b"complete test data"
        data_stream = BytesIO(test_data)
        wrapper = FileWrapper(original_file, data_stream)

        # 移動到中間位置
        wrapper.Position = 8

        # 調用 save 應該返回完整數據並重置位置
        result = wrapper.save()
        assert result == test_data
        assert wrapper.Position == len(test_data)

    def test_file_wrapper_getattr_代理(self):
        """測試 FileWrapper __getattr__ 代理功能"""
        original_file = MagicMock()
        original_file.custom_method.return_value = "delegated result"
        data_stream = BytesIO(b"test")
        wrapper = FileWrapper(original_file, data_stream)

        # 應該代理到原始檔案對象
        result = wrapper.custom_method()
        assert result == "delegated result"
        original_file.custom_method.assert_called_once()
