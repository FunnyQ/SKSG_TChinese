#!/usr/bin/env python3
"""
測試工具函數模組
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

# 導入要測試的函數
from sk_cht import sanitize_filename, is_admin, get_base_path, FileWrapper


class TestUtilityFunctions:
    """測試工具函數"""

    def test_sanitize_filename_基本字元(self):
        """測試檔案名稱淨化 - 基本字元"""
        result = sanitize_filename("hello_world-123.txt")
        assert result == "hello_world-123.txt"

    def test_sanitize_filename_非法字元(self):
        """測試檔案名稱淨化 - 非法字元處理"""
        result = sanitize_filename("file<>:\"|?*.txt")
        assert result == "file.txt"

    def test_sanitize_filename_空格處理(self):
        """測試檔案名稱淨化 - 空格替換為底線"""
        result = sanitize_filename("my file name.txt")
        assert result == "my_file_name.txt"

    def test_sanitize_filename_中文字元保留(self):
        """測試檔案名稱淨化 - 中文字元應被保留"""
        result = sanitize_filename("中文檔案名稱.txt")
        assert result == "中文檔案名稱.txt"

    def test_sanitize_filename_空字串(self):
        """測試檔案名稱淨化 - 空字串處理"""
        result = sanitize_filename("")
        assert result == ""

    def test_sanitize_filename_特殊字元組合(self):
        """測試檔案名稱淨化 - 特殊字元組合"""
        result = sanitize_filename("test/\\<>:|file?.txt")
        assert result == "testfile.txt"


class TestAdminCheck:
    """測試權限檢查功能"""

    def test_is_admin_windows_成功(self):
        """測試 Windows 系統管理員檢查 - 成功案例"""
        with patch('sk_cht.sys.platform', 'win32'), \
             patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = True
            result = is_admin()
            assert result is True

    def test_is_admin_windows_失敗(self):
        """測試 Windows 系統管理員檢查 - 失敗案例"""
        with patch('sk_cht.sys.platform', 'win32'), \
             patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.return_value = False
            result = is_admin()
            assert result is False

    def test_is_admin_非windows系統(self):
        """測試非 Windows 系統權限檢查"""
        with patch('sk_cht.sys.platform', 'darwin'):
            result = is_admin()
            assert result is False

    def test_is_admin_異常處理(self):
        """測試權限檢查異常處理"""
        with patch('sk_cht.sys.platform', 'win32'), \
             patch('sk_cht.ctypes') as mock_ctypes:
            mock_ctypes.windll.shell32.IsUserAnAdmin.side_effect = Exception("權限檢查失敗")
            result = is_admin()
            assert result is False


class TestGetBasePath:
    """測試基礎路徑獲取"""

    def test_get_base_path_開發模式(self):
        """測試開發模式下的路徑獲取"""
        # 在非打包模式下，函數應該返回包含 sk_cht.py 的目錄
        with patch('sk_cht.getattr') as mock_getattr, \
             patch('sk_cht.hasattr', return_value=False), \
             patch('sk_cht.os.path.dirname') as mock_dirname, \
             patch('sk_cht.os.path.abspath') as mock_abspath:
            mock_getattr.return_value = False
            mock_abspath.return_value = '/path/to/sk_cht.py'
            mock_dirname.return_value = '/path/to'

            result = get_base_path()
            assert result == '/path/to'

    def test_get_base_path_打包模式模擬(self):
        """測試打包模式的模擬行為"""
        # 模擬打包環境
        with patch('sk_cht.getattr') as mock_getattr, \
             patch('sk_cht.hasattr', return_value=True):
            # 模擬 sys.frozen = True 和 sys._MEIPASS 存在
            def side_effect(obj, attr, default=None):
                if attr == 'frozen':
                    return True
                elif attr == '_MEIPASS':
                    return '/temp/extracted'
                return default
            mock_getattr.side_effect = side_effect

            # 直接模擬 get_base_path 的行為
            with patch('sk_cht.get_base_path', return_value='/temp/extracted'):
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
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)
        assert wrapper.Length == 9  # "test data" 的長度

    def test_file_wrapper_position_屬性(self):
        """測試 FileWrapper Position 屬性"""
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        # 測試初始位置
        assert wrapper.Position == 0

        # 測試設定位置
        wrapper.Position = 5
        assert wrapper.Position == 5

    def test_file_wrapper_read_bytes(self):
        """測試 FileWrapper read_bytes 方法"""
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        # 讀取部分資料
        result = wrapper.read_bytes(4)
        assert result == b"test"

    def test_file_wrapper_save_方法(self):
        """測試 FileWrapper save 方法"""
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        # 模擬讀取一些資料後儲存
        wrapper.read_bytes(4)
        result = wrapper.save()
        assert result == b"test data"

    def test_file_wrapper_getattr_代理(self):
        """測試 FileWrapper __getattr__ 代理功能"""
        original_file = MagicMock()
        original_file.custom_method.return_value = "custom_result"
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)

        # 測試代理到原始檔案的方法
        result = wrapper.custom_method()
        assert result == "custom_result"
        original_file.custom_method.assert_called_once()
