"""
使用者介面模組 - 處理主選單和使用者互動
"""
import os
import sys
import time
from typing import Callable, Dict, Any

from ..platform_detector import PlatformDetector


class MenuSystem:
    """選單系統"""

    def __init__(self):
        """初始化選單系統"""
        self.platform_name = PlatformDetector.get_current_platform()
        self.game_root = os.getcwd()

        # 選單選項對應的處理函數
        self.menu_handlers: Dict[str, Callable] = {}

    def register_handler(self, option: str, handler: Callable) -> None:
        """
        註冊選單選項處理器

        Args:
            option: 選項編號
            handler: 處理函數
        """
        self.menu_handlers[option] = handler

    def display_header(self) -> None:
        """顯示選單標題"""
        print("=" * 60)
        print("== 絲綢之歌繁體中文化工具 v1.1 ==")
        print("=" * 60)
        print(f"作業系統: {self.platform_name}")
        print(f"遊戲目錄: {self.game_root}")

    def display_menu_options(self) -> None:
        """顯示選單選項"""
        print("\n請選擇要執行的操作：\n")
        print("  1. 進行繁體中文化")
        print("  2. 還原備份")
        print("  3. 關於")
        print("  4. 退出\n")

    def get_user_choice(self) -> str:
        """
        獲取使用者選擇

        Returns:
            str: 使用者輸入的選項
        """
        return input("請輸入選項 [1-4]: ").strip()

    def clear_screen(self) -> None:
        """清理螢幕"""
        if sys.platform == 'win32':
            os.system('cls')

    def wait_for_enter(self) -> None:
        """等待使用者按 Enter 鍵"""
        input("\n按下 Enter 鍵返回主選單...")

    def show_unsupported_platform_error(self) -> None:
        """顯示不支援平台的錯誤訊息"""
        print(f"\n[錯誤] 不支援的作業系統 ({sys.platform})。")
        input("\n按下 Enter 鍵退出...")

    def show_about(self) -> None:
        """顯示關於資訊"""
        print("\n" + "=" * 60)
        print("== 關於此工具 ==")
        print("\n本工具全程使用AI完成。")
        print("\n核心: Python")
        print("  - 資源庫: UnityPy")
        print("  - 自動化腳本: Gemini大神")
        print("\n不提供技術支援。")
        print("=" * 60)

    def run_main_loop(self) -> None:
        """
        執行主選單迴圈
        """
        while True:
            self.clear_screen()
            self.display_header()

            # 檢查平台支援
            if not PlatformDetector.is_supported_platform():
                self.show_unsupported_platform_error()
                return

            self.display_menu_options()
            choice = self.get_user_choice()

            if choice == '4':
                print("程式即將退出。")
                time.sleep(1)
                break
            elif choice == '3':
                self.show_about()
            elif choice in self.menu_handlers:
                # 執行對應的處理函數
                self.menu_handlers[choice]()
            else:
                print("\n無效的指令，請重新輸入。")
                time.sleep(1)
                continue

            if choice != '4':  # 不是退出選項才等待
                self.wait_for_enter()


def create_menu_system() -> MenuSystem:
    """
    創建選單系統實例

    Returns:
        MenuSystem: 選單系統實例
    """
    return MenuSystem()
