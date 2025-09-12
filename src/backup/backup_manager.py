"""
備份管理模組 - 負責遊戲檔案的備份與還原
"""
import os
import shutil
from typing import List, Optional
from ..config import BACKUP_FOLDER, GAME_ROOT_PATH
from ..platform_detector import PlatformDetector


class BackupManager:
    """備份管理器"""

    def __init__(self):
        """初始化備份管理器"""
        self.backup_folder = BACKUP_FOLDER
        self.game_root = GAME_ROOT_PATH

        try:
            self.bundle_path, self.assets_path, self.title_path = PlatformDetector.get_game_paths()
        except RuntimeError:
            # 平台不支援時設為 None
            self.bundle_path = None
            self.assets_path = None
            self.title_path = None

    def get_backup_paths(self) -> List[tuple[str, str]]:
        """
        獲取需要備份的檔案路徑對應關係

        Returns:
            List[tuple]: [(source_path, backup_path), ...]
        """
        if not all([self.bundle_path, self.assets_path, self.title_path]):
            return []

        backup_pairs = [
            (self.bundle_path, os.path.join(
                self.backup_folder,
                os.path.relpath(self.bundle_path, self.game_root)
            )),
            (self.assets_path, os.path.join(
                self.backup_folder,
                os.path.relpath(self.assets_path, self.game_root)
            )),
            (self.title_path, os.path.join(
                self.backup_folder,
                os.path.relpath(self.title_path, self.game_root)
            ))
        ]

        return backup_pairs

    def cleanup_old_backup(self) -> bool:
        """
        清理舊的備份資料夾

        Returns:
            bool: 是否成功清理
        """
        try:
            if os.path.exists(self.backup_folder):
                print("\n[步驟] 偵測到舊的備份資料夾，正在移除...")
                shutil.rmtree(self.backup_folder)
                print("舊備份已移除。")
            return True
        except Exception as e:
            print(f"[警告] 清理舊備份時發生錯誤: {e}")
            return False

    def create_backup(self) -> bool:
        """
        建立新的備份

        Returns:
            bool: 是否成功建立備份
        """
        try:
            print("\n[步驟] 正在建立新的原始檔案備份...")

            backup_pairs = self.get_backup_paths()
            if not backup_pairs:
                print("[錯誤] 無法獲取備份路徑，可能平台不受支援。")
                return False

            # 建立備份目錄結構
            for source_path, backup_path in backup_pairs:
                backup_dir = os.path.dirname(backup_path)
                os.makedirs(backup_dir, exist_ok=True)

                # 檢查源檔案是否存在
                if not os.path.exists(source_path):
                    print(f"[警告] 源檔案不存在: {source_path}")
                    continue

                # 複製檔案
                shutil.copy2(source_path, backup_path)

            print("新備份已建立至 'Backup' 資料夾。")
            return True

        except Exception as e:
            print(f"[錯誤] 建立備份時發生錯誤: {e}")
            return False

    def restore_backup(self) -> bool:
        """
        從備份還原檔案

        Returns:
            bool: 是否成功還原
        """
        try:
            if not os.path.exists(self.backup_folder):
                print("[錯誤] 找不到 'Backup' 資料夾，無法還原。")
                return False

            backup_pairs = self.get_backup_paths()
            if not backup_pairs:
                print("[錯誤] 無法獲取備份路徑，可能平台不受支援。")
                return False

            # 檢查備份完整性
            missing_backups = []
            for source_path, backup_path in backup_pairs:
                if not os.path.exists(backup_path):
                    missing_backups.append(backup_path)

            if missing_backups:
                print("[錯誤] 備份資料夾中檔案不完整，無法還原。")
                for missing in missing_backups:
                    print(f"  缺失: {missing}")
                return False

            # 執行還原
            print("正在從 'Backup' 資料夾還原原始檔案...")
            for source_path, backup_path in backup_pairs:
                shutil.copy2(backup_path, source_path)

            print("\n== 檔案已成功還原！==")
            return True

        except Exception as e:
            print(f"[錯誤] 還原過程中發生錯誤: {e}")
            return False

    def validate_backup(self) -> bool:
        """
        驗證備份的完整性

        Returns:
            bool: 備份是否完整
        """
        if not os.path.exists(self.backup_folder):
            return False

        backup_pairs = self.get_backup_paths()
        if not backup_pairs:
            return False

        for _, backup_path in backup_pairs:
            if not os.path.exists(backup_path):
                return False

        return True
