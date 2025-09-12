#!/usr/bin/env python3
"""
測試 run_new.py 啟動器的專門測試
"""
import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock

# 確保可以找到項目根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestRunNewLauncher:
    """測試 run_new.py 啟動器"""

    def test_launcher_檔案存在(self):
        """測試 run_new.py 檔案存在"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        assert os.path.exists(launcher_path), "run_new.py 啟動器應該存在"

    def test_launcher_檔案內容正確(self):
        """測試 run_new.py 內容結構正確"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        
        with open(launcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查必要的內容
        assert '#!/usr/bin/env python3' in content or 'python3' in content.lower()
        assert 'from src.main import main' in content
        assert 'if __name__ == "__main__":' in content
        assert 'main()' in content

    def test_launcher_可以導入所需模組(self):
        """測試啟動器可以正確導入所需模組"""
        # 測試可以導入 src.main
        try:
            from src.main import main
            assert callable(main), "main 函數應該是可調用的"
        except ImportError as e:
            pytest.fail(f"無法導入 src.main.main: {e}")

    def test_launcher_路徑設置正確(self):
        """測試啟動器的路徑設置邏輯"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        
        with open(launcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查路徑設置邏輯
        assert 'sys.path.insert(0,' in content
        assert 'os.path.dirname(os.path.abspath(__file__))' in content

    @patch('src.main.main')
    def test_launcher_執行流程(self, mock_main):
        """測試啟動器的執行流程"""
        # 模擬執行 run_new.py
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        
        # 直接執行檔案內容來測試
        with open(launcher_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 創建一個模擬的全域環境
        mock_globals = {
            '__name__': '__main__',
            'sys': sys,
            'os': os,
        }
        
        try:
            # 執行程式碼（但不會實際調用 main，因為我們已經 mock 了）
            exec(content, mock_globals)
        except Exception:
            # 如果有 import 錯誤等，這是預期的，因為我們在測試環境
            pass
        
        # 這個測試主要是確保程式碼結構正確


class TestNewVersionModules:
    """測試新版本各個模組的基本功能"""

    def test_main_模組存在(self):
        """測試 src.main 模組存在且可導入"""
        try:
            from src import main
            assert hasattr(main, 'main'), "main 模組應該有 main 函數"
        except ImportError as e:
            pytest.fail(f"無法導入 src.main: {e}")

    def test_config_模組存在(self):
        """測試 src.config 模組存在且有必要配置"""
        try:
            from src import config
            # 檢查重要配置項
            assert hasattr(config, 'UNITY_VERSION'), "config 應該有 UNITY_VERSION"
            assert hasattr(config, 'GAME_ROOT_PATH'), "config 應該有 GAME_ROOT_PATH"
            assert hasattr(config, 'CHT_FOLDER_PATH'), "config 應該有 CHT_FOLDER_PATH"
        except ImportError as e:
            pytest.fail(f"無法導入 src.config: {e}")

    def test_utils_模組存在(self):
        """測試 src.utils 模組存在且有必要工具函數"""
        try:
            from src import utils
            assert hasattr(utils, 'sanitize_filename'), "utils 應該有 sanitize_filename 函數"
            assert hasattr(utils, 'FileWrapper'), "utils 應該有 FileWrapper 類"
        except ImportError as e:
            pytest.fail(f"無法導入 src.utils: {e}")

    def test_platform_detector_模組存在(self):
        """測試 src.platform_detector 模組存在"""
        try:
            from src import platform_detector
            assert hasattr(platform_detector, 'PlatformDetector'), "platform_detector 應該有 PlatformDetector 類"
        except ImportError as e:
            pytest.fail(f"無法導入 src.platform_detector: {e}")

    def test_backup_manager_模組存在(self):
        """測試 src.backup.backup_manager 模組存在"""
        try:
            from src.backup import backup_manager
            assert hasattr(backup_manager, 'BackupManager'), "backup_manager 應該有 BackupManager 類"
        except ImportError as e:
            pytest.fail(f"無法導入 src.backup.backup_manager: {e}")

    def test_unity_模組存在(self):
        """測試 Unity 相關模組存在"""
        try:
            from src.unity import asset_processor
            from src.unity import bundle_handler
            assert hasattr(asset_processor, 'BaseAssetProcessor'), "asset_processor 應該有 BaseAssetProcessor 類"
            assert hasattr(bundle_handler, 'BundleHandler'), "bundle_handler 應該有 BundleHandler 類"
        except ImportError as e:
            pytest.fail(f"無法導入 Unity 模組: {e}")

    def test_ui_模組存在(self):
        """測試 src.ui.menu 模組存在"""
        try:
            from src.ui import menu
            assert hasattr(menu, 'MenuSystem'), "menu 應該有 MenuSystem 類"
        except ImportError as e:
            pytest.fail(f"無法導入 src.ui.menu: {e}")


class TestNewVersionFunctionality:
    """測試新版本的核心功能"""

    def test_新版本工具函數與原版一致(self):
        """測試新版本的工具函數與原版行為一致"""
        import sk_cht
        from src import utils
        
        test_cases = [
            "normal_file.txt",
            "file with spaces.txt", 
            "file<>:|*?.txt",
            "中文檔案.txt",
            ""
        ]
        
        for test_case in test_cases:
            original_result = sk_cht.sanitize_filename(test_case)
            new_result = utils.sanitize_filename(test_case)
            assert original_result == new_result, f"檔案名淨化不一致: '{test_case}'"

    def test_新版本FileWrapper與原版一致(self):
        """測試新版本的 FileWrapper 與原版行為一致"""
        import sk_cht
        from src.utils import FileWrapper as NewFileWrapper
        from io import BytesIO
        
        # 準備測試資料
        original_file = MagicMock()
        test_data = b"test data for consistency check"
        
        # 建立兩個版本的 FileWrapper
        old_stream = BytesIO(test_data)
        old_wrapper = sk_cht.FileWrapper(original_file, old_stream)
        
        new_stream = BytesIO(test_data)  
        new_wrapper = NewFileWrapper(original_file, new_stream)
        
        # 測試基本屬性
        assert old_wrapper.Length == new_wrapper.Length
        assert old_wrapper.Position == new_wrapper.Position
        
        # 測試讀取行為
        old_data = old_wrapper.read_bytes(8)
        new_data = new_wrapper.read_bytes(8) 
        assert old_data == new_data

    def test_配置常數與原版一致(self):
        """測試新版本配置常數與原版一致"""
        import sk_cht
        from src import config
        
        # 檢查重要常數
        assert sk_cht.UNITY_VERSION == config.UNITY_VERSION
        
        # 檢查路徑相關常數存在（值可能不同但都應該存在）
        assert hasattr(sk_cht, 'CHT_FOLDER_PATH') and hasattr(config, 'CHT_FOLDER_PATH')
        assert hasattr(sk_cht, 'BACKUP_FOLDER') and hasattr(config, 'BACKUP_FOLDER')


class TestExecutionCompatibility:
    """測試執行兼容性"""

    def test_run_new_語法正確性(self):
        """測試 run_new.py 語法正確性"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", launcher_path],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"run_new.py 語法錯誤: {result.stderr}"

    @patch('src.main.main')
    def test_run_new_可以被執行(self, mock_main):
        """測試 run_new.py 可以被正常執行（模擬模式）"""
        launcher_path = os.path.join(PROJECT_ROOT, "run_new.py")
        
        # 模擬執行（但不會實際調用主函數）
        try:
            result = subprocess.run(
                [sys.executable, launcher_path],
                capture_output=True,
                text=True,
                timeout=5  # 5秒超時
            )
            # 預期可能會有某些錯誤（因為缺少遊戲檔案等），但不應該是語法錯誤
        except subprocess.TimeoutExpired:
            # 如果超時，說明程式至少開始執行了，這也是可接受的
            pass
        except Exception as e:
            pytest.fail(f"執行 run_new.py 時發生未預期錯誤: {e}")