import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# 導入需要測試的模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPlatformDetection:
    """測試平台偵測邏輯"""

    def setup_method(self):
        """每個測試方法前執行的設置"""
        # 清除已設置的全域變數，確保測試獨立性
        import sk_cht
        sk_cht.PLATFORM_NAME = "未知"
        sk_cht.BUNDLE_FILE_PATH = None
        sk_cht.TEXT_ASSETS_FILE_PATH = None
        sk_cht.TITLE_BUNDLE_PATH = None

    @patch('sk_cht.sys.platform', 'win32')
    @patch('sk_cht.os.getcwd')
    def test_windows_平台路徑設定(self, mock_getcwd):
        """測試 Windows 平台的路徑設定"""
        mock_getcwd.return_value = '/fake/game/root'

        # 重新導入模組以觸發平台檢測邏輯
        import importlib
        import sk_cht
        importlib.reload(sk_cht)

        assert sk_cht.PLATFORM_NAME == "Windows"
        assert "Hollow Knight Silksong_Data" in sk_cht.SILKSONG_DATA_PATH
        assert "StandaloneWindows64" in sk_cht.STREAMING_ASSETS_PLATFORM_PATH
        assert sk_cht.BUNDLE_FILE_PATH.endswith("fonts_assets_chinese.bundle")
        assert sk_cht.TEXT_ASSETS_FILE_PATH.endswith("resources.assets")
        assert sk_cht.TITLE_BUNDLE_PATH.endswith("title.spriteatlas.bundle")

    @patch('sk_cht.sys.platform', 'darwin')
    @patch('sk_cht.os.getcwd')
    def test_macos_平台路徑設定(self, mock_getcwd):
        """測試 macOS 平台的路徑設定"""
        mock_getcwd.return_value = '/fake/game/root'

        # 重新導入模組以觸發平台檢測邏輯
        import importlib
        import sk_cht
        importlib.reload(sk_cht)

        assert sk_cht.PLATFORM_NAME == "macOS"
        assert "Hollow Knight Silksong.app" in sk_cht.SILKSONG_DATA_PATH
        assert "Contents/Resources/Data" in sk_cht.SILKSONG_DATA_PATH
        assert "StandaloneOSX" in sk_cht.STREAMING_ASSETS_PLATFORM_PATH
        assert sk_cht.BUNDLE_FILE_PATH.endswith("fonts_assets_chinese.bundle")

    @patch('sk_cht.sys.platform', 'linux')
    @patch('sk_cht.os.getcwd')
    def test_linux_平台路徑設定(self, mock_getcwd):
        """測試 Linux 平台的路徑設定"""
        mock_getcwd.return_value = '/fake/game/root'

        # 重新導入模組以觸發平台檢測邏輯
        import importlib
        import sk_cht
        importlib.reload(sk_cht)

        assert sk_cht.PLATFORM_NAME == "Linux"
        assert "Hollow Knight Silksong_Data" in sk_cht.SILKSONG_DATA_PATH
        assert "StandaloneLinux64" in sk_cht.STREAMING_ASSETS_PLATFORM_PATH
        assert sk_cht.BUNDLE_FILE_PATH.endswith("fonts_assets_chinese.bundle")

    @patch('sk_cht.sys.platform', 'unknown_platform')
    @patch('sk_cht.os.getcwd')
    def test_未知平台處理(self, mock_getcwd):
        """測試未知平台的處理"""
        mock_getcwd.return_value = '/fake/game/root'

        # 重新導入模組以觸發平台檢測邏輯
        import importlib
        import sk_cht
        importlib.reload(sk_cht)

        # 未知平台時，變數應該保持預設值
        assert sk_cht.PLATFORM_NAME == "未知"
        assert sk_cht.BUNDLE_FILE_PATH is None
        assert sk_cht.TEXT_ASSETS_FILE_PATH is None
        assert sk_cht.TITLE_BUNDLE_PATH is None

    def test_常數設定正確性(self):
        """測試常數設定的正確性"""
        import sk_cht

        # 檢查 Unity 版本
        assert sk_cht.UNITY_VERSION == "6000.0.50f1"

        # 檢查資料夾路徑包含 CHT
        assert sk_cht.CHT_FOLDER_PATH.endswith("CHT")
        assert sk_cht.FONT_SOURCE_FOLDER.endswith(os.path.join("CHT", "Font"))
        assert sk_cht.PNG_SOURCE_FOLDER.endswith(os.path.join("CHT", "Png"))
        assert sk_cht.TEXT_SOURCE_FOLDER.endswith(os.path.join("CHT", "Text"))

        # 檢查備份與暫存資料夾
        assert sk_cht.BACKUP_FOLDER.endswith("Backup")
        assert sk_cht.TEMP_WORKSPACE_FOLDER.endswith("temp_workspace")


class TestGamePathValidation:
    """測試遊戲路徑驗證邏輯"""

    @patch('sk_cht.os.path.exists')
    def test_路徑檢查邏輯(self, mock_exists):
        """測試路徑存在性檢查邏輯"""
        import sk_cht

        # 設定哪些路徑存在
        def exists_side_effect(path):
            # 只有特定路徑存在
            return path.endswith(('CHT', 'fonts_assets_chinese.bundle', 'resources.assets'))

        mock_exists.side_effect = exists_side_effect

        # 模擬 run_modding 中的路徑檢查邏輯
        paths_to_check = [
            sk_cht.BUNDLE_FILE_PATH,
            sk_cht.TEXT_ASSETS_FILE_PATH,
            sk_cht.TITLE_BUNDLE_PATH,
            sk_cht.CHT_FOLDER_PATH
        ]

        # 由於某些路徑可能是 None（未知平台），需要過濾
        valid_paths = [path for path in paths_to_check if path is not None]

        if valid_paths:
            # 檢查路徑存在性
            results = [mock_exists(path) for path in valid_paths]

            # CHT 路徑應該存在
            cht_result = mock_exists(sk_cht.CHT_FOLDER_PATH)
            assert cht_result is True
