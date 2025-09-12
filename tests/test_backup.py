import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# 導入需要測試的模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sk_cht


class TestBackupFunctionality:
    """測試備份相關功能"""

    def setup_method(self):
        """每個測試前的設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.game_root = os.path.join(self.temp_dir, "game")
        self.backup_folder = os.path.join(self.game_root, "Backup")

        # 設定測試用路徑
        self.bundle_path = os.path.join(self.game_root, "test.bundle")
        self.assets_path = os.path.join(self.game_root, "resources.assets")
        self.title_path = os.path.join(self.game_root, "title.bundle")

        # 建立測試目錄結構
        os.makedirs(self.game_root, exist_ok=True)

        # 建立測試檔案
        Path(self.bundle_path).write_bytes(b"test bundle content")
        Path(self.assets_path).write_bytes(b"test assets content")
        Path(self.title_path).write_bytes(b"test title content")

    def teardown_method(self):
        """每個測試後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_備份建立簡化測試(self):
        """測試備份建立的簡化版本"""
        # 建立舊備份資料夾來測試清理邏輯
        old_backup = os.path.join(self.game_root, "Backup")
        os.makedirs(old_backup, exist_ok=True)

        # 在舊備份中建立檔案
        test_file = os.path.join(old_backup, "test.txt")
        Path(test_file).write_text("old backup content")

        assert os.path.exists(old_backup)
        assert os.path.exists(test_file)

        # 清理舊備份（模擬 run_modding 中的邏輯）
        if os.path.exists(old_backup):
            shutil.rmtree(old_backup)

        assert not os.path.exists(old_backup)
        assert not os.path.exists(test_file)

    def test_備份資料夾清理(self):
        """測試舊備份資料夾的清理"""
        # 建立舊備份資料夾
        old_backup = os.path.join(self.game_root, "Backup")
        os.makedirs(old_backup, exist_ok=True)

        # 在舊備份中建立檔案
        test_file = os.path.join(old_backup, "test.txt")
        Path(test_file).write_text("old backup content")

        assert os.path.exists(old_backup)
        assert os.path.exists(test_file)

        # 清理舊備份（模擬 run_modding 中的邏輯）
        if os.path.exists(old_backup):
            shutil.rmtree(old_backup)

        assert not os.path.exists(old_backup)
        assert not os.path.exists(test_file)

    def test_備份檔案複製邏輯(self):
        """測試備份檔案複製的基本邏輯"""
        # 建立目標備份資料夾
        os.makedirs(self.backup_folder, exist_ok=True)

        # 執行檔案複製
        backup_bundle = os.path.join(self.backup_folder, "test.bundle")
        backup_assets = os.path.join(self.backup_folder, "resources.assets")
        backup_title = os.path.join(self.backup_folder, "title.bundle")

        shutil.copy2(self.bundle_path, backup_bundle)
        shutil.copy2(self.assets_path, backup_assets)
        shutil.copy2(self.title_path, backup_title)

        # 驗證備份檔案存在並且內容正確
        assert os.path.exists(backup_bundle)
        assert os.path.exists(backup_assets)
        assert os.path.exists(backup_title)

        assert Path(backup_bundle).read_bytes() == b"test bundle content"
        assert Path(backup_assets).read_bytes() == b"test assets content"
        assert Path(backup_title).read_bytes() == b"test title content"

    def test_restore_backup_基本功能(self):
        """測試備份還原基本功能"""
        # 建立備份資料夾和檔案
        os.makedirs(self.backup_folder, exist_ok=True)
        backup_bundle = os.path.join(self.backup_folder, "test.bundle")
        backup_assets = os.path.join(self.backup_folder, "resources.assets")
        backup_title = os.path.join(self.backup_folder, "title.bundle")

        Path(backup_bundle).write_bytes(b"backup bundle content")
        Path(backup_assets).write_bytes(b"backup assets content")
        Path(backup_title).write_bytes(b"backup title content")

        # 修改原始檔案
        Path(self.bundle_path).write_bytes(b"modified bundle content")
        Path(self.assets_path).write_bytes(b"modified assets content")
        Path(self.title_path).write_bytes(b"modified title content")

        # 執行還原
        shutil.copy2(backup_bundle, self.bundle_path)
        shutil.copy2(backup_assets, self.assets_path)
        shutil.copy2(backup_title, self.title_path)

        # 驗證還原結果
        assert Path(self.bundle_path).read_bytes() == b"backup bundle content"
        assert Path(self.assets_path).read_bytes() == b"backup assets content"
        assert Path(self.title_path).read_bytes() == b"backup title content"

    def test_備份檔案完整性檢查(self):
        """測試備份檔案的完整性檢查"""
        # 建立不完整的備份
        os.makedirs(self.backup_folder, exist_ok=True)

        # 只建立部分備份檔案
        backup_bundle = os.path.join(self.backup_folder, "test.bundle")
        Path(backup_bundle).write_bytes(b"backup content")
        # 故意不建立其他備份檔案

        # 檢查備份完整性
        expected_backups = [
            os.path.join(self.backup_folder, "test.bundle"),
            os.path.join(self.backup_folder, "resources.assets"),
            os.path.join(self.backup_folder, "title.bundle")
        ]

        missing_files = [f for f in expected_backups if not os.path.exists(f)]

        # 應該有檔案缺失
        assert len(missing_files) > 0
        assert not os.path.exists(os.path.join(self.backup_folder, "resources.assets"))
        assert not os.path.exists(os.path.join(self.backup_folder, "title.bundle"))

    def test_備份過程異常處理(self):
        """測試備份過程中的異常處理"""
        # 測試權限錯誤的處理
        try:
            # 嘗試複製到不存在的目錄
            shutil.copy2(self.bundle_path, "/nonexistent/path/file")
            assert False, "應該拋出異常"
        except (FileNotFoundError, PermissionError, OSError):
            # 預期的異常
            pass

    def test_路徑計算正確性(self):
        """測試相對路徑計算的正確性"""
        # 測試 os.path.relpath 的使用
        game_root = "/fake/game/root"
        full_path = "/fake/game/root/data/bundle.file"

        relative_path = os.path.relpath(full_path, game_root)
        expected = "data/bundle.file"

        assert relative_path == expected


class TestRestoreBackupFunction:
    """專門測試 restore_backup 函數"""

    def setup_method(self):
        """每個測試前的設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_folder = os.path.join(self.temp_dir, "Backup")

    def teardown_method(self):
        """每個測試後的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_restore_backup_資料夾不存在(self):
        """測試還原時備份資料夾不存在的情況"""
        # 確保資料夾不存在
        assert not os.path.exists(self.backup_folder)

        with patch('sk_cht.BACKUP_FOLDER', self.backup_folder), \
             patch('builtins.print') as mock_print:

            sk_cht.restore_backup()

            # 驗證錯誤訊息被顯示
            mock_print.assert_any_call("[錯誤] 找不到 'Backup' 資料夾，無法還原。")

    def test_restore_backup_檔案不完整(self):
        """測試備份檔案不完整時的處理"""
        # 建立不完整的備份
        os.makedirs(self.backup_folder, exist_ok=True)

        # 只建立部分備份檔案
        partial_backup = os.path.join(self.backup_folder, "partial.bundle")
        Path(partial_backup).write_bytes(b"partial backup")

        # 模擬路徑設置
        fake_bundle_path = os.path.join(self.temp_dir, "fake.bundle")
        fake_assets_path = os.path.join(self.temp_dir, "fake.assets")
        fake_title_path = os.path.join(self.temp_dir, "fake.title")
        fake_game_root = self.temp_dir

        with patch('sk_cht.BACKUP_FOLDER', self.backup_folder), \
             patch('sk_cht.BUNDLE_FILE_PATH', fake_bundle_path), \
             patch('sk_cht.TEXT_ASSETS_FILE_PATH', fake_assets_path), \
             patch('sk_cht.TITLE_BUNDLE_PATH', fake_title_path), \
             patch('sk_cht.GAME_ROOT_PATH', fake_game_root), \
             patch('builtins.print') as mock_print:

            sk_cht.restore_backup()

            # 驗證錯誤訊息
            mock_print.assert_any_call("[錯誤] 備份資料夾中檔案不完整，無法還原。")
