"""
主程式入口 - 絲綢之歌繁體中文化工具
"""
import sys
import os
import traceback
from typing import Optional

# 添加 Unity 相關的修正補丁
print("[資訊] 應用 BC7 壓縮修正補丁...")
import UnityPy
from UnityPy.export import Texture2DConverter
from UnityPy.enums import TextureFormat
import etcpak

# BC7 壓縮修正補丁
original_compress_etcpak = Texture2DConverter.compress_etcpak

def patched_compress_etcpak(data: bytes, width: int, height: int, target_texture_format: TextureFormat) -> bytes:
    if target_texture_format == TextureFormat.BC7:
        params = etcpak.BC7CompressBlockParams()
        return etcpak.compress_bc7(data, width, height, params)
    else:
        return original_compress_etcpak(data, width, height, target_texture_format)

Texture2DConverter.compress_etcpak = patched_compress_etcpak
print("[資訊] 補丁應用成功。")

# 導入自定義模組
from .platform_detector import PlatformDetector
from .backup.backup_manager import BackupManager
from .ui.menu import create_menu_system
from .unity.bundle_handler import BundleHandler
from .utils import is_admin, run_as_admin
from .config import PLATFORM_CONFIG


class SilksongLocalizationTool:
    """絲綢之歌本地化工具主類"""

    def __init__(self):
        """初始化工具"""
        self.backup_manager = BackupManager()
        self.bundle_handler: Optional[BundleHandler] = None
        self.menu_system = create_menu_system()

        # 註冊選單處理器
        self.menu_system.register_handler('1', self.run_modding)
        self.menu_system.register_handler('2', self.restore_backup)

    def initialize_bundle_handler(self) -> bool:
        """
        初始化 Bundle 處理器

        Returns:
            bool: 是否成功初始化
        """
        try:
            if not PLATFORM_CONFIG:
                print("[錯誤] 不支援的平台")
                return False

            self.bundle_handler = BundleHandler(
                PLATFORM_CONFIG.bundle_file_path,
                PLATFORM_CONFIG.text_assets_file_path,
                PLATFORM_CONFIG.title_bundle_path
            )
            return True
        except Exception as e:
            print(f"[錯誤] 初始化 Bundle 處理器失敗: {e}")
            return False

    def validate_environment(self) -> bool:
        """
        驗證執行環境

        Returns:
            bool: 環境是否有效
        """
        if not PlatformDetector.is_supported_platform():
            print(f"[錯誤] 不支援的作業系統: {sys.platform}")
            return False

        # 檢查關鍵路徑
        try:
            bundle_path, assets_path, title_path = PlatformDetector.get_game_paths()
            paths_to_check = [bundle_path, assets_path, title_path]

            for path in paths_to_check:
                if not os.path.exists(path):
                    print(f"\n[錯誤] 關鍵路徑或檔案不存在: {path}")
                    print(f"請確保此程式位於遊戲根目錄下，且 {PlatformDetector.get_current_platform()} 版本的遊戲檔案完整。")
                    return False

        except RuntimeError as e:
            print(f"[錯誤] {e}")
            return False

        return True

    def run_modding(self) -> None:
        """執行中文化修改"""
        print("\n[開始執行修改流程]")

        # 驗證環境
        if not self.validate_environment():
            return

        # 確認使用者意圖
        print("\n[警告] 此操作將直接修改遊戲檔案。")
        confirm = input("您是否要繼續執行？ (輸入 'y' 確認): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            return

        try:
            # 初始化 Bundle 處理器
            if not self.initialize_bundle_handler():
                return

            # 清理舊備份並建立新備份
            if not self.backup_manager.cleanup_old_backup():
                print("[警告] 清理舊備份失敗，但繼續執行...")

            if not self.backup_manager.create_backup():
                print("[錯誤] 建立備份失敗，中止操作。")
                return

            # 執行資產處理
            print("\n[步驟 2/4] 正在載入資源並應用修改...")
            if not self.bundle_handler.process_all_assets():
                print("[錯誤] 資產處理失敗。")
                return

            print("資源修改完成。")

            # 保存修改後的檔案
            print("\n[步驟 3/4] 正在重新打包修改後的檔案...")
            if not self.bundle_handler.save_modified_files():
                print("[錯誤] 檔案保存失敗。")
                return

            print("打包完成。")

            # 覆蓋原始檔案
            print("\n[步驟 4/4] 正在用新檔案覆蓋遊戲檔案...")
            if not self.bundle_handler.replace_game_files():
                print("[錯誤] 檔案覆蓋失敗。")
                return

            print("覆蓋完成！")
            print("\n== 所有操作已成功完成！==")

        except Exception as e:
            print(f"\n[嚴重錯誤] 操作過程中發生錯誤: {e}")
            traceback.print_exc()

    def restore_backup(self) -> None:
        """還原備份"""
        print("\n[開始執行還原備份流程]")
        success = self.backup_manager.restore_backup()

        if not success:
            print("[錯誤] 還原失敗。")

    def run(self) -> None:
        """執行主程式"""
        # 檢查 Windows 管理員權限
        is_packaged = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

        if sys.platform == 'win32' and is_packaged and not is_admin():
            print("偵測到需要管理員權限，正在嘗試重新啟動...")
            run_as_admin()
            sys.exit(0)

        if sys.platform == 'win32' and not is_packaged and not is_admin():
            print("\n" + "=" * 60)
            print("== [開發者警告] ==")
            print("偵測到腳本未以管理員權限執行。")
            print("部分檔案操作 (如覆蓋遊戲檔案) 可能會失敗。")
            print("=" * 60 + "\n")

        # 啟動主選單
        self.menu_system.run_main_loop()


def main() -> None:
    """主程式入口點"""
    app = SilksongLocalizationTool()
    app.run()


if __name__ == "__main__":
    main()
