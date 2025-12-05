# Troubleshooting .exe Not Opening

If your .exe file is not opening on Windows, follow these steps:

## Step 1: Build Debug Version (See Error Messages)

1. Build the debug version which shows console output:
   ```batch
   pyinstaller build_exe_debug.spec --clean
   ```

2. Run `dist\GymManagementSystem_DEBUG.exe`
   - A console window will appear showing any error messages
   - This will help identify the exact problem

## Step 2: Common Issues and Fixes

### Issue: "Failed to execute script main"
**Cause**: Missing dependencies or import errors

**Solution**:
- Check the console output for specific error messages
- Ensure all dependencies are installed before building:
  ```batch
  pip install -r requirements.txt
  pip install pyinstaller
  ```

### Issue: "ModuleNotFoundError" or Import Errors
**Cause**: PyInstaller didn't bundle all required modules

**Solution**:
- Add missing modules to `hiddenimports` in `build_exe.spec`
- Rebuild with: `pyinstaller build_exe.spec --clean`

### Issue: Application Crashes Immediately
**Cause**: Path resolution issues or missing data files

**Solution**:
- The code has been updated to use `resource_path()` helper function
- Ensure `icon` folder is included in the build (already in spec file)
- Rebuild the application

### Issue: Antivirus Blocks the .exe
**Cause**: False positive from antivirus software

**Solution**:
- Add exception in antivirus settings
- Or use one-folder build instead of one-file

## Step 3: Test Build Process

1. **Clean previous builds**:
   ```batch
   rmdir /s /q build dist
   ```

2. **Rebuild with debug version**:
   ```batch
   pyinstaller build_exe_debug.spec --clean
   ```

3. **Test the debug .exe**:
   - Run `dist\GymManagementSystem_DEBUG.exe`
   - Check console for errors
   - Note any error messages

## Step 4: Alternative - One-Folder Build

If one-file build continues to fail, try one-folder build:

1. Create `build_exe_folder.spec`:
   ```python
   # Copy from build_exe.spec but change EXE section to:
   exe = EXE(
       pyz,
       a.scripts,
       [],
       exclude_binaries=True,
       name='GymManagementSystem',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       console=False,
   )
   
   coll = COLLECT(
       exe,
       a.binaries,
       a.zipfiles,
       a.datas,
       strip=False,
       upx=True,
       upx_exclude=[],
       name='GymManagementSystem',
   )
   ```

2. Build:
   ```batch
   pyinstaller build_exe_folder.spec --clean
   ```

3. Distribute the entire `dist\GymManagementSystem` folder

## Step 5: Check Windows Event Viewer

If the .exe still doesn't open:

1. Open Windows Event Viewer
2. Go to Windows Logs > Application
3. Look for errors related to your .exe
4. This will show detailed error information

## Step 6: Manual Testing

Test on the build machine first:

1. Build the .exe
2. Test it on the same machine where you built it
3. If it works there but not on another machine:
   - Missing Visual C++ Redistributable
   - Different Windows version
   - Missing system dependencies

## Required System Files

The target Windows machine may need:
- **Visual C++ Redistributable** (usually already installed)
- **Windows 7 or later**
- **Chrome/Edge browser** (for WhatsApp functionality)

## Getting Help

If issues persist, provide:
1. Error message from debug console
2. Windows version
3. Whether it works on build machine
4. Event Viewer error details

