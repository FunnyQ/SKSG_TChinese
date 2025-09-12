"""
Unity Bundle 處理器 - 統合所有 Unity 資產的處理
"""
import os
import shutil
from typing import List, Dict, Any, Optional
from PIL import Image
from io import BytesIO

import UnityPy
import UnityPy.config
from UnityPy.files import BundleFile, SerializedFile
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.export import Texture2DConverter

from ..config import UNITY_VERSION, TEMP_WORKSPACE_FOLDER, PNG_SOURCE_FOLDER
from ..utils import FileWrapper, sanitize_filename
from .asset_processor import AssetProcessorFactory


class BundleHandler:
    """Bundle 處理器"""

    def __init__(self, bundle_path: str, text_assets_path: str, title_bundle_path: str):
        """
        初始化 Bundle 處理器

        Args:
            bundle_path: Bundle 檔案路徑
            text_assets_path: 文字資產檔案路徑
            title_bundle_path: 標題 Bundle 檔案路徑
        """
        self.bundle_path = bundle_path
        self.text_assets_path = text_assets_path
        self.title_bundle_path = title_bundle_path

        # Unity 環境
        self.bundle_env: Optional[Any] = None
        self.text_env: Optional[Any] = None
        self.title_env: Optional[Any] = None

        # 資產處理器
        self.font_processor = AssetProcessorFactory.create_font_processor()
        self.material_processor = AssetProcessorFactory.create_material_processor()
        self.texture_processor = AssetProcessorFactory.create_texture_processor()
        self.text_processor = AssetProcessorFactory.create_text_asset_processor()

        # 暫存工作資料夾
        self.temp_workspace = TEMP_WORKSPACE_FOLDER

    def _initialize_unity_environment(self) -> bool:
        """
        初始化 Unity 環境

        Returns:
            bool: 是否成功初始化
        """
        try:
            # 清理並建立暫存資料夾
            if os.path.exists(self.temp_workspace):
                shutil.rmtree(self.temp_workspace)
            os.makedirs(self.temp_workspace, exist_ok=True)

            # 設定 Unity 版本
            if UNITY_VERSION:
                UnityPy.config.FALLBACK_UNITY_VERSION = UNITY_VERSION

            # 建立 TypeTree 生成器
            generator = TypeTreeGenerator(UNITY_VERSION)
            generator.load_local_game(os.getcwd())

            # 載入 Unity 環境
            self.bundle_env = UnityPy.load(self.bundle_path)
            self.bundle_env.typetree_generator = generator

            self.text_env = UnityPy.load(self.text_assets_path)

            self.title_env = UnityPy.load(self.title_bundle_path)
            self.title_env.typetree_generator = generator

            print("[資訊] Unity 環境初始化完成")
            return True

        except Exception as e:
            print(f"[錯誤] Unity 環境初始化失敗: {e}")
            return False

    def _find_all_objects(self, container: Any) -> List[Any]:
        """
        遞歸查找所有 Unity 物件

        Args:
            container: Unity 容器

        Returns:
            List[Any]: 所有找到的物件
        """
        all_objects = []

        if hasattr(container, 'files') and container.files is not None:
            for asset_file in list(container.files.values()):
                if isinstance(asset_file, SerializedFile):
                    all_objects.extend(asset_file.objects.values())
                elif isinstance(asset_file, BundleFile):
                    all_objects.extend(self._find_all_objects(asset_file))

        return all_objects

    def _process_title_bundle(self) -> bool:
        """
        處理標題 Bundle

        Returns:
            bool: 是否成功處理
        """
        try:
            print("[資訊] 開始處理 Title Bundle...")
            TARGET_ASSET_NAME = "sactx-0-1024x1024-BC7-Title-228dda81"
            SOURCE_PNG_NAME = "logo.png"
            source_png_path = os.path.join(PNG_SOURCE_FOLDER, SOURCE_PNG_NAME)

            if not os.path.exists(source_png_path):
                print(f"  - [警告] 找不到源文件 '{SOURCE_PNG_NAME}'，跳過 Title Logo 替換。")
                return True

            for obj in self.title_env.objects:
                if obj.type.name == "Texture2D":
                    data = obj.read()
                    if hasattr(data, "m_Name") and data.m_Name == TARGET_ASSET_NAME:
                        print(f"  - [紋理] 找到目標 Title Logo: '{data.m_Name}'")

                        if not (data.m_StreamData and data.m_StreamData.path):
                            print("  - [警告] Title Logo 不是 .resS 格式，暫不支援此種替換。")
                            break

                        with Image.open(source_png_path) as img:
                            image_binary, new_format = Texture2DConverter.image_to_texture2d(
                                img, data.m_TextureFormat, data.assets_file.target_platform
                            )

                        resS_path = os.path.basename(data.m_StreamData.path)
                        bundle_file = data.assets_file.parent
                        resS_file = bundle_file.files[resS_path]
                        new_ress_stream = BytesIO(image_binary)
                        wrapper = FileWrapper(resS_file, new_ress_stream)
                        bundle_file.files[resS_path] = wrapper

                        print(f"    - [資訊] 已為 '{resS_path}' 創建新的數據流。")

                        # 更新元數據
                        data.m_StreamData.offset = 0
                        data.m_StreamData.size = len(image_binary)
                        data.m_Width = img.width
                        data.m_Height = img.height
                        data.m_TextureFormat = new_format
                        data.m_CompleteImageSize = len(image_binary)

                        if hasattr(data, 'image_data'):
                            data.image_data = b""

                        data.save()
                        print(f"    - [紋理] 已成功更新 '{data.m_Name}' 的元數據。")
                        break

            return True

        except Exception as e:
            print(f"  - [嚴重警告] 處理 Title Logo 時發生錯誤: {e}")
            return False

    def _process_ress_texture_group(self, texture_group: List[Any]) -> bool:
        """
        處理 .resS 紋理組

        Args:
            texture_group: 共享同一個 .resS 檔案的紋理列表

        Returns:
            bool: 是否成功處理
        """
        if not texture_group:
            return True

        try:
            first_texture = texture_group[0]
            resS_path = os.path.basename(first_texture.m_StreamData.path)
            bundle_file = first_texture.assets_file.parent
            print(f"  - [紋理組] 開始處理共享 '{resS_path}' 的 {len(texture_group)} 個紋理...")

            new_datas = []
            for tex_data in texture_group:
                asset_name = tex_data.m_Name
                source_asset_name = "chinese_body_bold Atlas" if asset_name == "do_not_use_chinese_body_bold Atlas" else asset_name
                safe_name = sanitize_filename(source_asset_name)
                source_png_path = os.path.join(PNG_SOURCE_FOLDER, f"{safe_name}.png")

                if os.path.exists(source_png_path):
                    with Image.open(source_png_path) as img:
                        image_binary, new_format = Texture2DConverter.image_to_texture2d(
                            img, tex_data.m_TextureFormat, tex_data.assets_file.target_platform
                        )
                        new_datas.append({
                            "original_obj": tex_data,
                            "image_binary": image_binary,
                            "new_format": new_format,
                            "img": img.copy()
                        })

            if not new_datas:
                print(f"    - [資訊] 沒有找到要替換的紋理文件")
                return True

            # 重建 .resS 檔案
            new_ress_stream = BytesIO()
            current_offset = 0

            for data_dict in new_datas:
                data_dict["new_offset"] = current_offset
                new_ress_stream.write(data_dict["image_binary"])
                current_offset += len(data_dict["image_binary"])

            resS_file = bundle_file.files[resS_path]
            original_obj = resS_file._original if isinstance(resS_file, FileWrapper) else resS_file
            wrapper = FileWrapper(original_obj, new_ress_stream)
            bundle_file.files[resS_path] = wrapper
            print(f"    - [資訊] 已成功重建 '{resS_path}'，新總大小: {current_offset} bytes")

            # 更新所有紋理的元數據
            for data_dict in new_datas:
                tex_data = data_dict["original_obj"]
                img = data_dict["img"]
                tex_data.m_StreamData.offset = data_dict["new_offset"]
                tex_data.m_StreamData.size = len(data_dict["image_binary"])
                tex_data.m_Width = img.width
                tex_data.m_Height = img.height
                tex_data.m_TextureFormat = data_dict["new_format"]
                tex_data.m_CompleteImageSize = len(data_dict["image_binary"])

                if hasattr(tex_data, 'image_data'):
                    tex_data.image_data = b""

                tex_data.save()
                print(f"    - [紋理] 已更新 '{tex_data.m_Name}' 元數據 (新 offset: {data_dict['new_offset']})")

            return True

        except Exception as e:
            print(f"  - [嚴重警告] 處理紋理組 '{resS_path}' 時發生錯誤: {e}")
            return False

    def _process_bundle_assets(self) -> bool:
        """
        處理 Bundle 中的資產

        Returns:
            bool: 是否成功處理
        """
        try:
            print("[資訊] 正在分析與分類所有資源...")
            all_objects = self._find_all_objects(self.bundle_env)

            # 分類資產
            materials_to_process = []
            fonts_to_process = []
            textures_by_ress: Dict[str, List[Any]] = {}
            embedded_textures = []

            for obj in all_objects:
                try:
                    if obj.type.name in ["MonoBehaviour", "Material", "Texture2D"]:
                        data = obj.read()
                        if not (hasattr(data, 'm_Name') and data.m_Name):
                            continue

                        asset_name = data.m_Name

                        if (obj.type.name == "MonoBehaviour" and
                            asset_name in ["chinese_body", "chinese_body_bold", "do_not_use_chinese_body_bold"]):
                            fonts_to_process.append(data)

                        elif (obj.type.name == "Material" and
                              asset_name in ["simsun_tmpro Material", "chinese_body_bold Material", "do_not_use_chinese_body_bold Material"]):
                            materials_to_process.append(data)

                        elif (obj.type.name == "Texture2D" and
                              asset_name in ["chinese_body Atlas", "chinese_body_bold Atlas", "do_not_use_chinese_body_bold Atlas"]):
                            if data.m_StreamData and data.m_StreamData.path:
                                resS_path = os.path.basename(data.m_StreamData.path)
                                if resS_path not in textures_by_ress:
                                    textures_by_ress[resS_path] = []
                                textures_by_ress[resS_path].append(data)
                            else:
                                embedded_textures.append(data)

                except Exception as e:
                    print(f"  - [警告] 預處理資源時出錯: {e}")
                    continue

            print("[資訊] 分類完成，開始按依賴順序應用修改...")

            # 按依賴順序處理資產
            success = True

            # 1. 處理紋理組
            for resS_path, texture_group in textures_by_ress.items():
                texture_group.sort(key=lambda x: int(x.m_StreamData.offset))
                if not self._process_ress_texture_group(texture_group):
                    success = False

            # 2. 處理內嵌紋理
            for tex_data in embedded_textures:
                if not self.texture_processor.process_embedded_texture(tex_data):
                    success = False

            # 3. 處理字型
            for font_data in fonts_to_process:
                if not self.font_processor.process(font_data.object_reader):
                    success = False

            # 4. 處理材質
            for mat_data in materials_to_process:
                if not self.material_processor.process(mat_data.object_reader):
                    success = False

            return success

        except Exception as e:
            print(f"[錯誤] 處理 Bundle 資產時發生錯誤: {e}")
            return False

    def _process_text_assets(self) -> bool:
        """
        處理文字資產

        Returns:
            bool: 是否成功處理
        """
        try:
            print("[資訊] 開始處理文字資產...")
            success_count = 0

            for obj in self.text_env.objects:
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    if self.text_processor.process(data):
                        success_count += 1

            print(f"[資訊] 文字資產處理完成，成功處理 {success_count} 個資產")
            return True

        except Exception as e:
            print(f"[錯誤] 處理文字資產時發生錯誤: {e}")
            return False

    def process_all_assets(self) -> bool:
        """
        處理所有資產

        Returns:
            bool: 是否成功處理所有資產
        """
        if not self._initialize_unity_environment():
            return False

        success = True

        # 處理 Bundle 資產
        if not self._process_bundle_assets():
            success = False

        # 處理文字資產
        if not self._process_text_assets():
            success = False

        # 處理標題 Bundle
        if not self._process_title_bundle():
            success = False

        return success

    def save_modified_files(self) -> bool:
        """
        保存修改後的檔案到暫存區

        Returns:
            bool: 是否成功保存
        """
        try:
            modified_bundle_path = os.path.join(self.temp_workspace, os.path.basename(self.bundle_path))
            modified_text_assets_path = os.path.join(self.temp_workspace, os.path.basename(self.text_assets_path))
            modified_title_bundle_path = os.path.join(self.temp_workspace, os.path.basename(self.title_bundle_path))

            # 保存修改後的檔案
            with open(modified_bundle_path, "wb") as f:
                f.write(self.bundle_env.file.save())

            with open(modified_text_assets_path, "wb") as f:
                f.write(self.text_env.file.save())

            with open(modified_title_bundle_path, "wb") as f:
                f.write(self.title_env.file.save())

            print("[資訊] 檔案保存完成")
            return True

        except Exception as e:
            print(f"[錯誤] 保存檔案時發生錯誤: {e}")
            return False

    def replace_game_files(self) -> bool:
        """
        用修改後的檔案覆蓋遊戲檔案

        Returns:
            bool: 是否成功覆蓋
        """
        try:
            modified_bundle_path = os.path.join(self.temp_workspace, os.path.basename(self.bundle_path))
            modified_text_assets_path = os.path.join(self.temp_workspace, os.path.basename(self.text_assets_path))
            modified_title_bundle_path = os.path.join(self.temp_workspace, os.path.basename(self.title_bundle_path))

            # 覆蓋原始檔案
            shutil.move(modified_bundle_path, self.bundle_path)
            shutil.move(modified_text_assets_path, self.text_assets_path)
            shutil.move(modified_title_bundle_path, self.title_bundle_path)

            print("[資訊] 檔案覆蓋完成")
            return True

        except Exception as e:
            print(f"[錯誤] 覆蓋檔案時發生錯誤: {e}")
            return False
        finally:
            # 清理暫存資料夾
            if os.path.exists(self.temp_workspace):
                shutil.rmtree(self.temp_workspace)
