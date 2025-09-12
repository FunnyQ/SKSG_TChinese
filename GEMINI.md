# GEMINI.md

## Project Overview

This project is a Python-based tool for applying a Traditional Chinese localization to the game "Hollow Knight: Silksong". The project has been **completely refactored** from a single monolithic script to a modern, modular architecture while maintaining full backward compatibility.

**🔄 MAJOR REFACTOR COMPLETED**: 
- Transformed 1000+ line single file into modular architecture
- Added comprehensive test suite (43 tests, 40%+ coverage)
- Implemented TDD (Test-Driven Development) practices
- Maintained 100% backward compatibility

**Key Technologies:**

*   **Programming Language:** Python 3.8+
*   **Core Library:** `UnityPy` for Unity asset manipulation
*   **Image Processing:** `Pillow`
*   **Packaging:** `PyInstaller`
*   **Testing:** `pytest` with mocking and coverage
*   **Project Structure:** Modern `pyproject.toml` configuration

## Building and Running

**Dependencies:**

The project's dependencies are managed through both `requirements.txt` and `pyproject.toml`:

**Core Dependencies:**
*   `UnityPy` - Unity asset manipulation
*   `Pillow` - Image processing
*   `etcpak` - Texture compression
*   `TypeTreeGeneratorAPI` - Unity TypeTree generation

**Development Dependencies:**
*   `pytest>=7.0` - Testing framework
*   `pytest-mock>=3.0` - Mocking utilities  
*   `pytest-cov>=4.0` - Coverage reporting
*   `pyinstaller` - Executable building

**Running the New Modular Version (Recommended):**

1.  Install dependencies with development tools:
    ```bash
    uv pip install -r requirements.txt
    uv pip install -e ".[dev]"
    ```
2.  Place the entire project in the root directory of the "Hollow Knight: Silksong" game.
3.  Run the new modular version:
    ```bash
    uv run python -m src.main
    # OR
    uv run python run_new.py
    ```

**Running the Original Version (Backward Compatibility):**

```bash
# Traditional approach - still fully supported
python sk_cht.py
```

**Testing the Project:**

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test modules
uv run pytest tests/test_utils.py -v
```

**Building the executable:**

```bash
# Build from new modular entry point
pyinstaller --onefile --windowed --name "SilkSong_CHT" --icon="resources/icons/sk.ico" src/main.py

# Or build from original script (still works)
pyinstaller --onefile --windowed --name "SilkSong_CHT" --icon="resources/icons/sk.ico" sk_cht.py
```

## Development Conventions

### New Architecture Conventions

*   **Modular Design:** Code is organized into focused modules with single responsibilities:
    *   `src/main.py` - Application entry point and orchestration
    *   `src/config.py` - Centralized configuration management
    *   `src/utils.py` - Utility functions and helper classes
    *   `src/platform_detector.py` - Cross-platform compatibility
    *   `src/backup/` - Backup management functionality
    *   `src/unity/` - Unity asset processing modules
    *   `src/ui/` - User interface components

*   **Type Safety:** All new code uses Python type hints for better IDE support and error detection.

*   **Factory Pattern:** Asset processors use factory pattern for extensibility and testability.

*   **Dependency Injection:** Components receive their dependencies rather than creating them internally.

*   **Error Handling:** Comprehensive exception handling with user-friendly error messages.

### Testing Conventions

*   **Test-Driven Development:** Tests were written before refactoring to ensure functionality preservation.
*   **Mocking:** Unity dependencies are properly mocked to enable isolated testing.
*   **Fixtures:** Reusable test fixtures are organized in the `tests/fixtures/` directory.
*   **Coverage:** Target 40%+ code coverage with plans to reach 80%+.

### Legacy Conventions (Preserved)

*   **Platform-Specific Logic:** Uses `sys.platform` to detect OS and adjust file paths accordingly.
*   **Asset Organization:** Localized assets remain in the `CHT` folder (UNCHANGED):
    *   `CHT/Font`: Contains JSON files with font data
    *   `CHT/Png`: Contains PNG images for replacement
    *   `CHT/Text`: Contains `.txt` files with translated game text
*   **User Interface:** CLI with menu options for mod application, backup restoration, and tool information.
*   **Backups:** Automatic backup creation before any modifications.

### Project Structure

```
SKSG_TChinese/
├── src/                          # New modular codebase
├── tests/                        # Comprehensive test suite
├── CHT/                         # Asset directory (UNCHANGED)
├── resources/                   # Static resources
├── pyproject.toml              # Modern Python project config  
├── run_new.py                  # New launcher
├── sk_cht.py                   # Original script (preserved)
└── requirements.txt            # Dependencies
```

### Backward Compatibility

*   The original `sk_cht.py` script remains fully functional
*   All existing workflows and usage patterns are preserved
*   CHT asset directory structure is completely unchanged
*   Users can seamlessly switch between old and new versions
