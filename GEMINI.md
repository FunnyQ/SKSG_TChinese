# GEMINI.md

## Project Overview

This project is a Python-based tool for applying a Traditional Chinese localization to the game "Hollow Knight: Silksong". The main script, `sk_cht.py`, utilizes the `UnityPy` library to modify the game's Unity asset bundles. It replaces specific text, fonts, and images with their Traditional Chinese equivalents, which are stored in the `CHT` directory. The tool is designed to be packaged into a standalone executable using `PyInstaller`.

**Key Technologies:**

*   **Programming Language:** Python
*   **Core Library:** `UnityPy` for Unity asset manipulation
*   **Image Processing:** `Pillow`
*   **Packaging:** `PyInstaller`

## Building and Running

**Dependencies:**

The project's dependencies are listed in `requirements.txt`:

*   `pyinstaller`
*   `UnityPy`
*   `Pillow`
*   `TypeTreeGeneratorAPI`

**Running the script directly:**

1.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Place the script in the root directory of the "Hollow Knight: Silksong" game.
3.  Run the script:
    ```bash
    python sk_cht.py
    ```

**Building the executable:**

The project is intended to be distributed as a standalone executable. You can build it using `PyInstaller`:

```bash
pyinstaller --onefile --windowed --name "SilkSong_CHT" --icon="sk.ico" sk_cht.py
```

## Development Conventions

*   **Platform-Specific Logic:** The script uses `sys.platform` to detect the operating system (Windows, macOS, Linux) and adjust file paths accordingly.
*   **Asset Organization:** Localized assets are organized into subdirectories within the `CHT` folder:
    *   `CHT/Font`: Contains JSON files with font data.
    *   `CHT/Png`: Contains PNG images for replacement.
    *   `CHT/Text`: Contains `.txt` files with translated game text.
*   **User Interface:** The script provides a simple command-line interface (CLI) with options to apply the mod, restore from backup, and view information about the tool.
*   **Backups:** The script automatically creates a backup of the original game files before making any modifications.
