"""
平台偵測模組 - 負責偵測作業系統並設定對應的遊戲路徑
"""
import sys
from .config import PLATFORM_CONFIG, PlatformConfig


class PlatformDetector:
    """平台偵測器"""

    @staticmethod
    def get_current_platform() -> str:
        """獲取當前平台名稱"""
        return PLATFORM_CONFIG.name if PLATFORM_CONFIG else "未知"

    @staticmethod
    def get_platform_config() -> PlatformConfig:
        """
        獲取平台配置

        Returns:
            PlatformConfig: 平台配置物件

        Raises:
            RuntimeError: 如果平台不受支援
        """
        if PLATFORM_CONFIG is None:
            raise RuntimeError(f"不支援的作業系統: {sys.platform}")

        return PLATFORM_CONFIG

    @staticmethod
    def is_supported_platform() -> bool:
        """檢查當前平台是否受支援"""
        return PLATFORM_CONFIG is not None

    @staticmethod
    def get_game_paths() -> tuple[str, str, str]:
        """
        獲取遊戲相關路徑

        Returns:
            tuple: (bundle_file_path, text_assets_file_path, title_bundle_path)
        """
        config = PlatformDetector.get_platform_config()
        return (
            config.bundle_file_path,
            config.text_assets_file_path,
            config.title_bundle_path
        )
