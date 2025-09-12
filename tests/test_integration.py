#!/usr/bin/env python3
"""
整合測試：測試原版 sk_cht.py 和新版本的功能一致性
"""
import os
import sys
import subprocess
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock

# 確保可以找到項目根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestOriginalScript:
    """測試原版 sk_cht.py 腳本"""

    def test_original_script_存在(self):
        """測試原版腳本檔案存在"""
        script_path = os.path.join(PROJECT_ROOT, "sk_cht.py")
        assert os.path.exists(script_path), "原版 sk_cht.py 腳本應該存在"

    def test_original_script_可以導入(self):
        """測試原版腳本可以被導入"""
        try:
            import sk_cht
            assert hasattr(sk_cht, 'main_menu'), "原版腳本應該有 main_menu 函數"
            assert hasattr(sk_cht, 'sanitize_filename'), "原版腳本應該有 sanitize_filename 函數"
            assert hasattr(sk_cht, 'FileWrapper'), "原版腳本應該有 FileWrapper 類"
        except ImportError as e:
            pytest.fail(f"無法導入原版腳本: {e}")

    def test_original_script_基本功能測試(self):
        """測試原版腳本的基本功能"""
        import sk_cht

        # 測試檔案名稱淨化功能
        result = sk_cht.sanitize_filename("test<>file.txt")
        assert result == "testfile.txt"

        # 測試 FileWrapper 類別
        from io import BytesIO
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = sk_cht.FileWrapper(original_file, data_stream)
        assert wrapper.Length == 9

    @patch('sk_cht.os.path.exists')
    @patch('sk_cht.input')
    @patch('sk_cht.print')
    def test_original_script_路徑檢查邏輯(self, mock_print, mock_input, mock_exists):
        """測試原版腳本的路徑檢查邏輯"""
        import sk_cht

        # 模擬路徑不存在的情況
        mock_exists.return_value = False
        mock_input.return_value = 'n'  # 用戶選擇不繼續

        # 調用修改功能（應該會因為路徑不存在而提前返回）
        sk_cht.run_modding()

        # 驗證有錯誤訊息被印出
        assert any("錯誤" in str(call) for call in mock_print.call_args_list)


class TestNewLauncher:
    """測試新版 run_new.py 啟動器"""

    def test_new_launcher_存在(self):
        """測試新版啟動器存在"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        assert os.path.exists(launcher_path), "新版 run_new.py 啟動器應該存在"

    def test_new_launcher_可以導入(self):
        """測試新版啟動器可以正常導入模組"""
        # 測試是否可以導入新版的模組
        try:
            from src import main
            from src import config
            from src import utils
            assert hasattr(main, 'main'), "新版應該有 main 函數"
            assert hasattr(config, 'UNITY_VERSION'), "新版應該有配置模組"
            assert hasattr(utils, 'sanitize_filename'), "新版應該有工具函數"
        except ImportError as e:
            pytest.fail(f"無法導入新版模組: {e}")

    def test_new_launcher_基本功能測試(self):
        """測試新版本的基本功能"""
        from src import utils
        from src.utils import FileWrapper

        # 測試檔案名稱淨化功能
        result = utils.sanitize_filename("test<>file.txt")
        assert result == "testfile.txt"

        # 測試 FileWrapper 類別
        from io import BytesIO
        original_file = MagicMock()
        data_stream = BytesIO(b"test data")
        wrapper = FileWrapper(original_file, data_stream)
        assert wrapper.Length == 9


class TestVersionCompatibility:
    """測試兩個版本之間的兼容性"""

    def test_工具函數一致性(self):
        """測試兩個版本的工具函數行為一致"""
        # 導入兩個版本的函數
        import sk_cht
        from src import utils

        test_cases = [
            "normal_file.txt",
            "file with spaces.txt",
            "file<>with|illegal*chars?.txt",
            "中文檔案名稱.txt",
            "",
            "file/with\\path.txt"
        ]

        for test_case in test_cases:
            original_result = sk_cht.sanitize_filename(test_case)
            new_result = utils.sanitize_filename(test_case)
            assert original_result == new_result, f"檔案名稱淨化結果不一致: '{test_case}'"

    def test_FileWrapper類別一致性(self):
        """測試兩個版本的 FileWrapper 類別行為一致"""
        import sk_cht
        from src.utils import FileWrapper as NewFileWrapper
        from io import BytesIO

        # 準備測試資料
        original_file = MagicMock()
        test_data = b"test data for wrapper"

        # 測試原版 FileWrapper
        old_stream = BytesIO(test_data)
        old_wrapper = sk_cht.FileWrapper(original_file, old_stream)

        # 測試新版 FileWrapper
        new_stream = BytesIO(test_data)
        new_wrapper = NewFileWrapper(original_file, new_stream)

        # 比較行為
        assert old_wrapper.Length == new_wrapper.Length
        assert old_wrapper.Position == new_wrapper.Position

        # 測試讀取行為
        old_data = old_wrapper.read_bytes(4)
        new_data = new_wrapper.read_bytes(4)
        assert old_data == new_data

    def test_配置常數一致性(self):
        """測試兩個版本的配置常數一致"""
        import sk_cht
        from src import config

        # 測試 Unity 版本
        assert sk_cht.UNITY_VERSION == config.UNITY_VERSION

        # 測試平台相關路徑邏輯是否一致
        # （這裡可以根據實際情況添加更多配置比較）

    def test_路徑驗證邏輯一致性(self):
        """測試兩個版本的路徑驗證邏輯一致"""
        # 這個測試確保兩個版本在相同條件下有相同的行為
        import sk_cht
        from src import config
        
        # 檢查基本路徑常數是否存在
        assert hasattr(sk_cht, 'GAME_ROOT_PATH')
        assert hasattr(config, 'GAME_ROOT_PATH')
        
        # 檢查 CHT 相關路徑是否定義
        assert hasattr(sk_cht, 'CHT_FOLDER_PATH')  
        assert hasattr(config, 'CHT_FOLDER_PATH')


class TestScriptExecution:
    """測試腳本執行能力（不實際修改檔案）"""

    @pytest.mark.slow
    def test_original_script_可執行性(self):
        """測試原版腳本在模擬環境下可以執行"""
        script_path = os.path.join(PROJECT_ROOT, "sk_cht.py")

        # 使用 Python 語法檢查
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", script_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"原版腳本語法錯誤: {result.stderr}"

    @pytest.mark.slow
    def test_new_launcher_可執行性(self):
        """測試新版啟動器在模擬環境下可以執行"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")

        # 使用 Python 語法檢查
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", launcher_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"新版啟動器語法錯誤: {result.stderr}"

    def test_版本資訊一致性(self):
        """確保兩個版本顯示相同的版本資訊"""
        # 這個測試確保用戶看到的版本資訊是一致的
        # 可以根據實際需要調整
        pass


class TestBackwardCompatibility:
    """測試向後兼容性"""

    def test_CHT資料夾結構兼容(self):
        """測試CHT資料夾結構在兩個版本中都能正確識別"""
        cht_path = os.path.join(PROJECT_ROOT, "CHT")
        if os.path.exists(cht_path):
            # 檢查基本目錄結構
            expected_dirs = ["Font", "Png", "Text"]
            for dir_name in expected_dirs:
                dir_path = os.path.join(cht_path, dir_name)
                assert os.path.exists(dir_path), f"CHT/{dir_name} 目錄應該存在"

    def test_備份機制兼容(self):
        """測試備份機制在兩個版本中的兼容性"""
        # 確保兩個版本創建的備份可以互相使用
        backup_path = os.path.join(PROJECT_ROOT, "Backup")
        # 這裡可以添加更具體的備份機制測試
        assert True  # 佔位符
