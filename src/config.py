"""
配置檔案 - 包含所有平台相關設定和路徑配置
"""
import os
import sys
from typing import Optional
from dataclasses import dataclass


@dataclass
class PlatformConfig:
    """平台配置資料類"""
    name: str
    silksong_data_path: str
    streaming_assets_platform_path: str
    bundle_file_path: str
    text_assets_file_path: str
    title_bundle_path: str


def get_base_path() -> str:
    """獲取基礎路徑"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_project_root() -> str:
    """獲取專案根目錄"""
    # 從 src/config.py 往上兩層到專案根目錄
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def detect_platform() -> Optional[PlatformConfig]:
    """偵測並設定平台相關路徑"""
    game_root_path = os.getcwd()

    if sys.platform == "win32":
        silksong_data_path = os.path.join(game_root_path, "Hollow Knight Silksong_Data")
        streaming_assets_platform_path = os.path.join(
            silksong_data_path, "StreamingAssets", "aa", "StandaloneWindows64"
        )

        return PlatformConfig(
            name="Windows",
            silksong_data_path=silksong_data_path,
            streaming_assets_platform_path=streaming_assets_platform_path,
            bundle_file_path=os.path.join(streaming_assets_platform_path, "fonts_assets_chinese.bundle"),
            text_assets_file_path=os.path.join(silksong_data_path, "resources.assets"),
            title_bundle_path=os.path.join(
                streaming_assets_platform_path, "atlases_assets_assets", "sprites", "_atlases", "title.spriteatlas.bundle"
            ),
        )

    elif sys.platform == "darwin":
        silksong_data_path = os.path.join(
            game_root_path, "Hollow Knight Silksong.app", "Contents", "Resources", "Data"
        )
        streaming_assets_platform_path = os.path.join(
            silksong_data_path, "StreamingAssets", "aa", "StandaloneOSX"
        )

        return PlatformConfig(
            name="macOS",
            silksong_data_path=silksong_data_path,
            streaming_assets_platform_path=streaming_assets_platform_path,
            bundle_file_path=os.path.join(streaming_assets_platform_path, "fonts_assets_chinese.bundle"),
            text_assets_file_path=os.path.join(silksong_data_path, "resources.assets"),
            title_bundle_path=os.path.join(
                streaming_assets_platform_path, "atlases_assets_assets", "sprites", "_atlases", "title.spriteatlas.bundle"
            ),
        )

    elif sys.platform.startswith("linux"):
        silksong_data_path = os.path.join(game_root_path, "Hollow Knight Silksong_Data")
        streaming_assets_platform_path = os.path.join(
            silksong_data_path, "StreamingAssets", "aa", "StandaloneLinux64"
        )

        return PlatformConfig(
            name="Linux",
            silksong_data_path=silksong_data_path,
            streaming_assets_platform_path=streaming_assets_platform_path,
            bundle_file_path=os.path.join(streaming_assets_platform_path, "fonts_assets_chinese.bundle"),
            text_assets_file_path=os.path.join(silksong_data_path, "resources.assets"),
            title_bundle_path=os.path.join(
                streaming_assets_platform_path, "atlases_assets_assets", "sprites", "_atlases", "title.spriteatlas.bundle"
            ),
        )

    return None


# 全域常數
UNITY_VERSION = "6000.0.50f1"

# 路徑相關
_project_root = get_project_root()
GAME_ROOT_PATH = os.getcwd()
BACKUP_FOLDER = os.path.join(GAME_ROOT_PATH, "Backup")
TEMP_WORKSPACE_FOLDER = os.path.join(GAME_ROOT_PATH, "temp_workspace")

# CHT 資源路徑（保持原有結構）
CHT_FOLDER_PATH = os.path.join(_project_root, "CHT")
FONT_SOURCE_FOLDER = os.path.join(CHT_FOLDER_PATH, "Font")
PNG_SOURCE_FOLDER = os.path.join(CHT_FOLDER_PATH, "Png")
TEXT_SOURCE_FOLDER = os.path.join(CHT_FOLDER_PATH, "Text")

# 資源路徑
RESOURCES_FOLDER = os.path.join(_project_root, "resources")
ICONS_FOLDER = os.path.join(RESOURCES_FOLDER, "icons")

# 偵測平台配置
PLATFORM_CONFIG = detect_platform()
PLATFORM_NAME = PLATFORM_CONFIG.name if PLATFORM_CONFIG else "未知"
