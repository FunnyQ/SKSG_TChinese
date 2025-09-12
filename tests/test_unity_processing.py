import pytest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from pathlib import Path

# 導入需要測試的模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sk_cht


class TestFontProcessing:
    """測試字型處理功能"""

    def setup_method(self):
        """設置測試環境"""
        self.temp_dir = tempfile.mkdtemp()
        self.font_source_folder = os.path.join(self.temp_dir, "CHT", "Font")
        os.makedirs(self.font_source_folder, exist_ok=True)

    def teardown_method(self):
        """清理測試環境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_process_font_正常字型(self):
        """測試正常字型的處理"""
        # 建立測試用 JSON 檔案
        font_data = {
            "m_fontInfo": {
                "Name": "chinese_body",
                "PointSize": 36.0,
                "Scale": 1.0
            },
            "m_glyphInfoList": [
                {
                    "index": 65,
                    "x": 0,
                    "y": 0,
                    "width": 24,
                    "height": 32
                }
            ]
        }

        json_path = os.path.join(self.font_source_folder, "chinese_body.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(font_data, f)

        # 建立模擬的 Unity 物件
        mock_data = MagicMock()
        mock_data.m_Name = "chinese_body"

        mock_obj_reader = MagicMock()
        mock_obj_reader.read.return_value = mock_data
        mock_obj_reader.read_typetree.return_value = {
            "m_fontInfo": {"Name": "old_name"},
            "m_glyphInfoList": []
        }

        with patch('sk_cht.FONT_SOURCE_FOLDER', self.font_source_folder):
            sk_cht.process_font(mock_obj_reader)

            # 驗證 typetree 被更新
            mock_obj_reader.save_typetree.assert_called_once()

            # 取得保存的參數
            saved_args = mock_obj_reader.save_typetree.call_args[0]
            saved_tree = saved_args[0]

            assert saved_tree["m_fontInfo"] == font_data["m_fontInfo"]
            assert saved_tree["m_glyphInfoList"] == font_data["m_glyphInfoList"]

    def test_process_font_特殊命名處理(self):
        """測試特殊命名字型的處理 (do_not_use_chinese_body_bold)"""
        # 建立 chinese_body_bold.json 檔案
        font_data = {"m_fontInfo": {"Name": "chinese_body_bold"}}
        json_path = os.path.join(self.font_source_folder, "chinese_body_bold.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(font_data, f)

        mock_data = MagicMock()
        mock_data.m_Name = "do_not_use_chinese_body_bold"

        mock_obj_reader = MagicMock()
        mock_obj_reader.read.return_value = mock_data
        mock_obj_reader.read_typetree.return_value = {}

        with patch('sk_cht.FONT_SOURCE_FOLDER', self.font_source_folder):
            sk_cht.process_font(mock_obj_reader)

            mock_obj_reader.save_typetree.assert_called_once()

    def test_process_font_檔案不存在(self):
        """測試字型 JSON 檔案不存在的情況"""
        mock_data = MagicMock()
        mock_data.m_Name = "nonexistent_font"

        mock_obj_reader = MagicMock()
        mock_obj_reader.read.return_value = mock_data

        with patch('sk_cht.FONT_SOURCE_FOLDER', self.font_source_folder):
            # 不應該拋出異常，而是默默跳過
            sk_cht.process_font(mock_obj_reader)

            # save_typetree 不應該被呼叫
            mock_obj_reader.save_typetree.assert_not_called()


class TestMaterialProcessing:
    """測試材質處理功能"""

    def test_process_material_更新紋理尺寸(self):
        """測試材質紋理尺寸更新"""
        # 建立模擬的材質 typetree
        initial_tree = {
            "m_Name": "test_material",
            "m_SavedProperties": {
                "m_Floats": [
                    ["_TextureHeight", 2048.0],
                    ["_TextureWidth", 2048.0],
                    ["_OtherProperty", 1.0]
                ]
            }
        }

        mock_obj_reader = MagicMock()
        mock_obj_reader.read_typetree.return_value = initial_tree.copy()

        sk_cht.process_material(mock_obj_reader)

        # 驗證 typetree 被保存
        mock_obj_reader.save_typetree.assert_called_once()

        # 檢查更新的內容
        saved_args = mock_obj_reader.save_typetree.call_args[0]
        updated_tree = saved_args[0]

        # 檢查浮點數屬性是否正確更新
        floats = dict(updated_tree["m_SavedProperties"]["m_Floats"])
        assert floats["_TextureHeight"] == 4096.0
        assert floats["_TextureWidth"] == 4096.0
        assert floats["_OtherProperty"] == 1.0  # 其他屬性不變

    def test_process_material_添加缺失屬性(self):
        """測試材質缺失屬性的添加"""
        # 建立缺少尺寸屬性的材質
        initial_tree = {
            "m_Name": "incomplete_material",
            "m_SavedProperties": {
                "m_Floats": [
                    ["_SomeOtherProperty", 0.5]
                ]
            }
        }

        mock_obj_reader = MagicMock()
        mock_obj_reader.read_typetree.return_value = initial_tree.copy()

        sk_cht.process_material(mock_obj_reader)

        saved_args = mock_obj_reader.save_typetree.call_args[0]
        updated_tree = saved_args[0]

        # 檢查屬性被添加
        floats = dict(updated_tree["m_SavedProperties"]["m_Floats"])
        assert "_TextureHeight" in floats
        assert "_TextureWidth" in floats
        assert floats["_TextureHeight"] == 4096.0
        assert floats["_TextureWidth"] == 4096.0

    def test_process_material_結構異常(self):
        """測試材質結構異常的處理"""
        # 建立異常結構的材質
        abnormal_tree = {
            "m_Name": "abnormal_material"
            # 缺少 m_SavedProperties
        }

        mock_obj_reader = MagicMock()
        mock_obj_reader.read_typetree.return_value = abnormal_tree

        # 應該不拋出異常，而是跳過處理
        sk_cht.process_material(mock_obj_reader)

        # save_typetree 不應該被呼叫
        mock_obj_reader.save_typetree.assert_not_called()


class TestTextureProcessing:
    """測試紋理處理功能"""

    def setup_method(self):
        """設置測試環境"""
        self.temp_dir = tempfile.mkdtemp()
        self.png_source_folder = os.path.join(self.temp_dir, "CHT", "Png")
        os.makedirs(self.png_source_folder, exist_ok=True)

    def teardown_method(self):
        """清理測試環境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('sk_cht.Image.open')
    def test_process_embedded_texture_成功(self, mock_image_open):
        """測試內嵌紋理處理成功案例"""
        # 建立測試圖片檔案
        test_png = os.path.join(self.png_source_folder, "chinese_body_Atlas.png")
        Path(test_png).write_bytes(b"fake png data")

        # 模擬 PIL Image
        mock_img = MagicMock()
        mock_img.width = 512
        mock_img.height = 512
        mock_image_open.return_value.__enter__.return_value = mock_img

        # 模擬 Unity 紋理數據
        mock_data = MagicMock()
        mock_data.m_Name = "chinese_body Atlas"

        with patch('sk_cht.PNG_SOURCE_FOLDER', self.png_source_folder):
            sk_cht.process_embedded_texture(mock_data)

            # 驗證圖片被設置
            assert mock_data.image == mock_img
            assert mock_data.m_Width == 512
            assert mock_data.m_Height == 512
            mock_data.save.assert_called_once()

    def test_process_embedded_texture_檔案不存在(self):
        """測試內嵌紋理源文件不存在"""
        mock_data = MagicMock()
        mock_data.m_Name = "nonexistent_texture"

        with patch('sk_cht.PNG_SOURCE_FOLDER', self.png_source_folder):
            # 不應該拋出異常
            sk_cht.process_embedded_texture(mock_data)

            # save 不應該被呼叫
            mock_data.save.assert_not_called()


class TestTextAssetProcessing:
    """測試文字資產處理功能"""

    def setup_method(self):
        """設置測試環境"""
        self.temp_dir = tempfile.mkdtemp()
        self.text_source_folder = os.path.join(self.temp_dir, "CHT", "Text")
        os.makedirs(self.text_source_folder, exist_ok=True)

    def teardown_method(self):
        """清理測試環境"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_process_text_assets_成功替換(self):
        """測試文字資產成功替換"""
        # 建立測試文字檔案
        test_content = "測試繁體中文內容"
        text_file = os.path.join(self.text_source_folder, "ZH_UI.txt")
        Path(text_file).write_text(test_content, encoding="utf-8")

        # 建立模擬 Unity 環境
        mock_data = MagicMock()
        mock_data.m_Name = "ZH_UI"

        mock_obj = MagicMock()
        mock_obj.type.name = "TextAsset"
        mock_obj.read.return_value = mock_data

        mock_env = MagicMock()
        mock_env.objects = [mock_obj]

        with patch('sk_cht.TEXT_SOURCE_FOLDER', self.text_source_folder):
            sk_cht.process_text_assets(mock_env)

            # 驗證文字內容被設置
            assert mock_data.m_Script == test_content
            mock_data.save.assert_called_once()

    def test_process_text_assets_不在目標列表(self):
        """測試不在目標列表中的文字資產"""
        mock_data = MagicMock()
        mock_data.m_Name = "NotInTargetList"

        mock_obj = MagicMock()
        mock_obj.type.name = "TextAsset"
        mock_obj.read.return_value = mock_data

        mock_env = MagicMock()
        mock_env.objects = [mock_obj]

        sk_cht.process_text_assets(mock_env)

        # save 不應該被呼叫
        mock_data.save.assert_not_called()


class TestFileWrapper:
    """測試 FileWrapper 在 Unity 處理中的使用"""

    def test_file_wrapper_在紋理處理中的使用(self):
        """測試 FileWrapper 在紋理處理中的使用情況"""
        # 建立原始檔案模擬
        original_file = MagicMock()
        original_file.some_property = "original_value"

        # 建立新數據流
        new_data = b"new texture data"
        new_stream = BytesIO(new_data)

        # 建立 FileWrapper
        wrapper = sk_cht.FileWrapper(original_file, new_stream)

        # 測試數據存取
        assert wrapper.Length == len(new_data)
        assert wrapper.Position == 0

        # 測試讀取
        read_data = wrapper.read_bytes(4)
        assert read_data == b"new "

        # 測試屬性代理
        assert wrapper.some_property == "original_value"

        # 測試保存
        saved_data = wrapper.save()
        assert saved_data == new_data
