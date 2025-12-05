# Complete Windows Setup Guide - Step by Step

This guide will walk you through installing Git, getting the code, and building the .exe on Windows.

## Step 1: Install Git on Windows

### Option A: Download Git Installer (Recommended)

1. **Open your web browser** and go to: https://git-scm.com/download/win
2. **Download** the latest Git for Windows installer (it will auto-detect 64-bit or 32-bit)
3. **Run the installer** (Git-2.x.x-64-bit.exe)
4. **During installation:**
   - Click "Next" through the license
   - Choose installation location (default is fine)
   - Select components: **Keep all defaults checked**
   - Choose default editor: **Use default (Nano editor)** or choose Notepad++
   - Adjust PATH: **Use Git from the command line and also from 3rd-party software** (recommended)
   - Choose HTTPS transport: **Use the OpenSSL library** (default)
   - Configure line ending conversions: **Checkout Windows-style, commit Unix-style line endings** (default)
   - Configure terminal emulator: **Use Windows' default console window** (default)
   - Configure extra options: **Enable file system caching** (default)
   - Click "Install"
5. **Wait for installation** to complete
6. **Click "Finish"**

### Option B: Install via Winget (Windows 11/10 with Package Manager)

Open **PowerShell as Administrator** and run:
```powershell
winget install --id Git.Git -e --source winget
```

### Verify Git Installation

1. **Open Command Prompt** (Press `Win + R`, type `cmd`, press Enter)
2. **Type:**
   ```batch
   git --version
   ```
3. **You should see:** `git version 2.x.x` (or similar)

If you see an error, restart Command Prompt or restart your computer.

---

## Step 2: Install Python on Windows

1. **Go to:** https://www.python.org/downloads/
2. **Download** Python 3.10 or 3.11 (latest stable version)
3. **Run the installer**
4. **IMPORTANT:** Check the box **"Add Python to PATH"** at the bottom
5. **Click "Install Now"**
6. **Wait for installation** to complete
7. **Click "Close"**

### Verify Python Installation

1. **Open a NEW Command Prompt** (close and reopen if needed)
2. **Type:**
   ```batch
   python --version
   ```
3. **You should see:** `Python 3.x.x`

If you see an error, Python may not be in PATH. Restart your computer or manually add Python to PATH.

---

## Step 3: Clone the Repository

1. **Open Command Prompt**
2. **Navigate to where you want the project** (e.g., Desktop or Documents):
   ```batch
   cd Desktop
   ```
   Or:
   ```batch
   cd Documents
   ```

3. **Clone the repository:**
   ```batch
   git clone https://github.com/ngupta10/gym.git
   ```

4. **Navigate into the project folder:**
   ```batch
   cd gym
   ```

5. **Verify files are there:**
   ```batch
   dir
   ```
   You should see files like `main.py`, `requirements.txt`, etc.

---

## Step 4: Install Python Dependencies

1. **Make sure you're in the gym folder:**
   ```batch
   cd gym
   ```

2. **Upgrade pip (Python package manager):**
   ```batch
   python -m pip install --upgrade pip
   ```

3. **Install all required packages:**
   ```batch
   pip install -r requirements.txt
   ```
   This will take a few minutes. Wait for it to complete.

4. **Install PyInstaller (for building .exe):**
   ```batch
   pip install pyinstaller
   ```

---

## Step 5: Build the Windows .exe

### Option A: Use the Build Script (Easiest)

1. **Make sure you're in the gym folder:**
   ```batch
   cd gym
   ```

2. **Run the build script:**
   ```batch
   build_exe.bat
   ```

3. **When prompted, choose:**
   - Type `2` and press Enter for **DEBUG build** (shows console, easier to test)
   - Or type `1` and press Enter for **RELEASE build** (no console, final version)

4. **Wait for build to complete** (5-10 minutes)

5. **Find your .exe file:**
   ```batch
   dir dist
   ```
   You should see `GymManagementSystem.exe` or `GymManagementSystem_DEBUG.exe`

### Option B: Manual Build

1. **Make sure you're in the gym folder:**
   ```batch
   cd gym
   ```

2. **Build debug version (recommended first):**
   ```batch
   pyinstaller build_exe_debug.spec --clean
   ```

3. **Or build release version:**
   ```batch
   pyinstaller build_exe.spec --clean
   ```

4. **Find your .exe:**
   ```batch
   dir dist
   ```

---

## Step 6: Test the .exe

1. **Navigate to the dist folder:**
   ```batch
   cd dist
   ```

2. **Run the .exe:**
   ```batch
   GymManagementSystem_DEBUG.exe
   ```
   Or:
   ```batch
   GymManagementSystem.exe
   ```

3. **If it opens successfully**, you're done! 🎉

4. **If it doesn't open:**
   - Check the console window for error messages (if using DEBUG version)
   - See `TROUBLESHOOTING_EXE.md` for help

---

## Quick Reference: All Commands in Order

Copy and paste these commands one by one in Command Prompt:

```batch
REM Step 1: Verify Git is installed
git --version

REM Step 2: Verify Python is installed
python --version

REM Step 3: Navigate to Desktop (or your preferred location)
cd Desktop

REM Step 4: Clone the repository
git clone https://github.com/ngupta10/gym.git

REM Step 5: Enter the project folder
cd gym

REM Step 6: Upgrade pip
python -m pip install --upgrade pip

REM Step 7: Install dependencies
pip install -r requirements.txt

REM Step 8: Install PyInstaller
pip install pyinstaller

REM Step 9: Build the .exe (choose one)
REM For DEBUG build (shows console):
pyinstaller build_exe_debug.spec --clean

REM OR for RELEASE build (no console):
pyinstaller build_exe.spec --clean

REM Step 10: Test the .exe
cd dist
GymManagementSystem_DEBUG.exe
```

---

## Troubleshooting

### "git is not recognized"
- Git is not installed or not in PATH
- Restart Command Prompt
- Restart your computer
- Reinstall Git and make sure to select "Add to PATH"

### "python is not recognized"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart Command Prompt/computer

### "pip is not recognized"
- Python is not properly installed
- Try: `python -m pip` instead of just `pip`

### Build fails with import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try building debug version first to see error messages

### .exe doesn't open
- Run the DEBUG version to see error messages
- Check `TROUBLESHOOTING_EXE.md` for detailed help

---

## Next Steps

Once the .exe is built and working:

1. **Test it thoroughly** on the build machine
2. **Copy the .exe** to other Windows PCs to test
3. **Distribute** the .exe file (it's standalone, no Python needed on target machines)

The .exe file will be in the `dist` folder and can be copied to any Windows PC!

