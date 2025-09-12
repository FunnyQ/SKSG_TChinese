"""
Unity 資產處理器基礎類別
"""
import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PIL import Image

from ..config import FONT_SOURCE_FOLDER, PNG_SOURCE_FOLDER, TEXT_SOURCE_FOLDER
from ..utils import sanitize_filename


class BaseAssetProcessor(ABC):
    """資產處理器基礎類別"""

    @abstractmethod
    def process(self, obj: Any) -> bool:
        """
        處理資產物件

        Args:
            obj: Unity 資產物件

        Returns:
            bool: 是否成功處理
        """
        pass


class FontProcessor(BaseAssetProcessor):
    """字型處理器"""

    def __init__(self):
        """初始化字型處理器"""
        self.font_source_folder = FONT_SOURCE_FOLDER

    def process(self, obj_reader: Any) -> bool:
        """
        處理字型資產

        Args:
            obj_reader: Unity 物件讀取器

        Returns:
            bool: 是否成功處理
        """
        try:
            data = obj_reader.read()
            asset_name = data.m_Name

            # 處理特殊命名
            source_asset_name = "chinese_body_bold" if asset_name == "do_not_use_chinese_body_bold" else asset_name
            source_json_path = os.path.join(self.font_source_folder, f"{source_asset_name}.json")

            if not os.path.exists(source_json_path):
                print(f"  - [警告] 找不到字型源檔案: {source_json_path}")
                return False

            # 讀取原始 typetree
            original_tree = obj_reader.read_typetree()

            # 讀取源 JSON 資料
            with open(source_json_path, "r", encoding="utf-8") as f:
                source_dict = json.load(f)

            # 完全替換字型資料
            if "m_fontInfo" in source_dict:
                original_tree["m_fontInfo"] = source_dict["m_fontInfo"]
            if "m_glyphInfoList" in source_dict:
                original_tree["m_glyphInfoList"] = source_dict["m_glyphInfoList"]

            # 保存修改
            obj_reader.save_typetree(original_tree)
            print(f"  - [字型] 已從 JSON 完整替換 '{asset_name}' 的數據")

            return True

        except Exception as e:
            print(f"  - [警告] 處理字型 '{getattr(data, 'm_Name', '未知')}' 時出錯: {e}")
            return False


class MaterialProcessor(BaseAssetProcessor):
    """材質處理器"""

    def process(self, obj_reader: Any) -> bool:
        """
        處理材質資產

        Args:
            obj_reader: Unity 物件讀取器

        Returns:
            bool: 是否成功處理
        """
        try:
            tree = obj_reader.read_typetree()
            asset_name = tree.get("m_Name", "未知材質")

            if "m_SavedProperties" not in tree or "m_Floats" not in tree["m_SavedProperties"]:
                print(f"  - [警告] 材質 '{asset_name}' 結構不符合預期，跳過修改。")
                return False

            # 創建新的浮點數屬性列表
            new_floats = []
            height_modified = False
            width_modified = False

            # 遍歷並更新屬性
            for key, value in tree["m_SavedProperties"]["m_Floats"]:
                if key == "_TextureHeight":
                    new_floats.append([key, 4096.0])
                    height_modified = True
                elif key == "_TextureWidth":
                    new_floats.append([key, 4096.0])
                    width_modified = True
                else:
                    new_floats.append([key, value])

            # 添加缺失的屬性
            if not height_modified:
                new_floats.append(["_TextureHeight", 4096.0])
                print(f"    - [資訊] 在 '{asset_name}' 中添加了 _TextureHeight")
            if not width_modified:
                new_floats.append(["_TextureWidth", 4096.0])
                print(f"    - [資訊] 在 '{asset_name}' 中添加了 _TextureWidth")

            # 更新材質屬性
            tree["m_SavedProperties"]["m_Floats"] = new_floats

            # 保存修改
            obj_reader.save_typetree(tree)
            print(f"  - [材質] 已直接修改 '{asset_name}' 的紋理尺寸屬性")

            return True

        except Exception as e:
            print(f"  - [警告] 處理材質時出錯: {e}")
            return False


class TextureProcessor(BaseAssetProcessor):
    """紋理處理器"""

    def __init__(self):
        """初始化紋理處理器"""
        self.png_source_folder = PNG_SOURCE_FOLDER

    def process_embedded_texture(self, data: Any) -> bool:
        """
        處理內嵌紋理

        Args:
            data: 紋理數據物件

        Returns:
            bool: 是否成功處理
        """
        try:
            asset_name = data.m_Name
            source_asset_name = "chinese_body_bold Atlas" if asset_name == "do_not_use_chinese_body_bold Atlas" else asset_name
            safe_name = sanitize_filename(source_asset_name)
            source_png_path = os.path.join(self.png_source_folder, f"{safe_name}.png")

            if not os.path.exists(source_png_path):
                print(f"  - [警告] 找不到紋理源檔案: {source_png_path}")
                return False

            with Image.open(source_png_path) as img:
                data.image = img
                data.m_Width = img.width
                data.m_Height = img.height
                data.save()
                print(f"  - [紋理] 已成功替換 (內嵌模式) '{asset_name}'")

            return True

        except Exception as e:
            print(f"  - [警告] 處理內嵌紋理 '{data.m_Name}' 時出錯: {e}")
            return False

    def process(self, obj: Any) -> bool:
        """處理紋理物件（通用介面）"""
        return self.process_embedded_texture(obj)


class TextAssetProcessor(BaseAssetProcessor):
    """文字資產處理器"""

    # 目標文字資產列表
    TEXT_TARGET_ASSETS = {
        "ZH_Achievements", "ZH_AutoSaveNames", "ZH_Belltown", "ZH_Bonebottom", "ZH_Caravan",
        "ZH_City", "ZH_Coral", "ZH_Crawl", "ZH_Credits List", "ZH_Deprecated", "ZH_Dust",
        "ZH_Enclave", "ZH_Error", "ZH_Fast Travel", "ZH_Forge", "ZH_General", "ZH_Greymoor",
        "ZH_Inspect", "ZH_Journal", "ZH_Lore", "ZH_MainMenu", "ZH_Map Zones", "ZH_Peak",
        "ZH_Pilgrims", "ZH_Prompts", "ZH_Quests", "ZH_Shellwood", "ZH_Shop", "ZH_Song",
        "ZH_Titles", "ZH_Tools", "ZH_UI", "ZH_Under", "ZH_Wanderers", "ZH_Weave", "ZH_Wilds"
    }

    def __init__(self):
        """初始化文字資產處理器"""
        self.text_source_folder = TEXT_SOURCE_FOLDER

    def process(self, data: Any) -> bool:
        """
        處理文字資產

        Args:
            data: 文字資產數據物件

        Returns:
            bool: 是否成功處理
        """
        try:
            if not data or not hasattr(data, 'm_Name'):
                return False

            asset_name = data.m_Name
            if asset_name not in self.TEXT_TARGET_ASSETS:
                return False

            source_txt_path = os.path.join(self.text_source_folder, f"{asset_name}.txt")
            if not os.path.exists(source_txt_path):
                print(f"  - [警告] 找不到文字源檔案: {source_txt_path}")
                return False

            with open(source_txt_path, "rb") as f:
                local_bytes = f.read()

            data.m_Script = local_bytes.decode("utf-8", "surrogateescape")
            data.save()
            print(f"  - [文字] 已成功替換 '{asset_name}'")

            return True

        except Exception as e:
            print(f"  - [警告] 處理文字資產時出錯: {e}")
            return False


class AssetProcessorFactory:
    """資產處理器工廠"""

    @staticmethod
    def create_font_processor() -> FontProcessor:
        """創建字型處理器"""
        return FontProcessor()

    @staticmethod
    def create_material_processor() -> MaterialProcessor:
        """創建材質處理器"""
        return MaterialProcessor()

    @staticmethod
    def create_texture_processor() -> TextureProcessor:
        """創建紋理處理器"""
        return TextureProcessor()

    @staticmethod
    def create_text_asset_processor() -> TextAssetProcessor:
        """創建文字資產處理器"""
        return TextAssetProcessor()
