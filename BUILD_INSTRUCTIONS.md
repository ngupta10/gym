# Building Windows .exe from Gym Management System

**⚠️ IMPORTANT: PyInstaller must run on Windows. You cannot build a Windows .exe on Mac or Linux.**

If you're on Mac/Linux, see `BUILD_ON_WINDOWS.md` for options (GitHub Actions, Windows VM, etc.).

This guide explains how to convert the Python application into a standalone Windows .exe file **on a Windows PC**.

## Prerequisites

1. **Windows PC** (Windows 7 or later) - **MUST build on Windows**
2. **Python 3.8 or higher** installed
3. **All dependencies installed** (run `pip install -r requirements.txt`)

## Method 1: Using the Build Script (Recommended)

1. Open Command Prompt or PowerShell in the project directory
2. Run the build script:
   ```batch
   build_exe.bat
   ```
3. Wait for the build to complete (this may take several minutes)
4. Find your .exe file in the `dist` folder: `dist\GymManagementSystem.exe`

## Method 2: Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build using the spec file:
   ```bash
   pyinstaller build_exe.spec --clean
   ```

3. Or build with a simple command:
   ```bash
   pyinstaller --name="GymManagementSystem" --windowed --onefile --add-data "icon;icon" main.py
   ```

## Build Options

### One-File vs One-Folder

- **One-File** (current spec): Creates a single .exe file that extracts to a temp folder when run
  - Pros: Single file to distribute
  - Cons: Slower startup, larger file size

- **One-Folder**: Creates a folder with .exe and dependencies
  - Pros: Faster startup, smaller individual files
  - Cons: Multiple files to distribute

To change to one-folder, modify `build_exe.spec` and change the `EXE` section to use `COLLECT` instead.

### Console Window

The current build hides the console window. To show it (for debugging), change `console=False` to `console=True` in `build_exe.spec`.

## Distribution

When distributing the .exe:

1. **Test on a clean Windows machine** (without Python installed) to ensure all dependencies are bundled
2. **Include the icon folder** if icons don't appear correctly
3. **Create a README** with:
   - System requirements
   - Installation instructions
   - How to use the application
   - Troubleshooting tips

## Troubleshooting

### "Failed to execute script" error
- Try building with `console=True` to see error messages
- Check that all dependencies are installed before building
- Ensure all data files (icons) are included

### Large file size
- This is normal for PyInstaller builds (includes Python interpreter)
- Consider using `--one-folder` instead of `--onefile` to reduce size
- Use UPX compression (already enabled in spec file)

### Missing icons/images
- Ensure the `icon` folder is included in the build
- Check the `datas` section in `build_exe.spec`
- Verify paths use relative references

### WhatsApp functionality issues
- Ensure Chrome/Edge browser is installed on target machine
- WhatsApp Web must be accessible
- Some antivirus software may block pyautogui automation

## File Structure After Build

```
gym/
├── build/              # Build files (can be deleted)
├── dist/              # Distribution folder
│   └── GymManagementSystem.exe  # Your executable
├── build_exe.spec     # PyInstaller spec file
└── ...                # Source files
```

## Notes

- The first run of the .exe may be slower as it extracts files
- Antivirus software may flag PyInstaller executables (false positive)
- The database file (`gym_management.db`) will be created in the same directory as the .exe when first run

