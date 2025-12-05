# Building Windows .exe from Mac

Since PyInstaller must run on Windows (you can't cross-compile from Mac to Windows), here are your options:

## Option 1: Build on the Windows PC (Easiest)

1. **Transfer your code to the Windows PC:**
   - Copy the entire project folder to the Windows machine
   - Or use Git to clone/pull the repository

2. **On the Windows PC:**
   ```batch
   # Install Python 3.8+ if not already installed
   # Download from python.org
   
   # Open Command Prompt in project folder
   cd path\to\gym\project
   
   # Install dependencies
   pip install -r requirements.txt
   pip install pyinstaller
   
   # Build the .exe
   pyinstaller build_exe.spec --clean
   
   # Or use the batch script
   build_exe.bat
   ```

3. **Find your .exe:**
   - Location: `dist\GymManagementSystem.exe`
   - This file can be distributed to any Windows PC

## Option 2: Use GitHub Actions (Automated)

I've created a GitHub Actions workflow that automatically builds the .exe on Windows whenever you push to GitHub.

### Setup:

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to GitHub Actions:**
   - Visit: `https://github.com/yourusername/yourrepo/actions`
   - Click "Build Windows Executable" workflow
   - Click "Run workflow" button
   - Wait for build to complete (5-10 minutes)

3. **Download the .exe:**
   - After build completes, click on the workflow run
   - Scroll down to "Artifacts"
   - Download "GymManagementSystem-Windows"
   - Extract and use the .exe file

### Automatic Builds:

The workflow is set to run:
- When you push to `main` branch
- When you create a version tag (like `v1.0.0`)
- Manually via "Run workflow" button

## Option 3: Use Windows VM or Remote Windows Machine

If you have access to:
- **Windows VM** (Parallels, VMware, VirtualBox)
- **Remote Windows server/PC**
- **Cloud Windows instance** (AWS, Azure, etc.)

You can build there using the same instructions as Option 1.

## Option 4: Use Wine (Not Recommended)

Wine allows running Windows executables on Mac, but building with PyInstaller through Wine is:
- Complex to set up
- Often unreliable
- May produce broken executables

**Not recommended** - use one of the options above instead.

## Recommended Approach

**For one-time build:** Use Option 1 (build directly on Windows PC)

**For ongoing builds:** Use Option 2 (GitHub Actions) - this way you can build from anywhere and always get a Windows .exe

## Quick Start (Windows PC)

If you're on the Windows PC right now:

1. Open Command Prompt
2. Navigate to project folder
3. Run:
   ```batch
   build_exe.bat
   ```
4. Choose option 2 (Debug build) first to test
5. If debug works, build release version

## Troubleshooting

If the build fails on Windows, check:
- Python 3.8+ is installed
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller installed: `pip install pyinstaller`
- Run debug build to see error messages

See `TROUBLESHOOTING_EXE.md` for more help.

