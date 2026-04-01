# Build FITS_Database Executable

This guide explains how to compile FITS_Database into a standalone executable that doesn't require Python or dependencies.

## Prerequisites

### Option 1: Simple EXE (Recommended for Colleagues)

**What you need:**
- Python 3.7+ (already installed)
- PyInstaller: `pip install pyinstaller`

**Build Time:** ~5-10 minutes
**Output Size:** ~150-200 MB
**User Experience:** Download .exe → Run → Done!

### Option 2: Professional Installer (Best for Distribution)

**What you need:**
- Everything from Option 1, PLUS
- NSIS Installer: http://nsis.sourceforge.net/

**Build Time:** ~10-15 minutes
**Output Size:** ~150-200 MB (executable), ~70-100 MB (installer)
**User Experience:** Download installer → Run → Follow wizard → Done!

---

## Build Instructions

### Step 1: Install PyInstaller

Open PowerShell and run:
```powershell
pip install pyinstaller
```

Verify installation:
```powershell
pyinstaller --version
```

### Step 2: Build the Executable

Navigate to the FITS_Database folder:
```powershell
cd F:\Documentos\Python\FITS_Database
python build_exe.py
```

**Wait for completion...** This will:
- Clean up previous builds
- Compile fits_gui_database.py with all dependencies
- Bundle FITS_Viewer folder inside
- Create: `dist/FITS_Library.exe`

**Output:**
```
============================================================
✓ Build successful!
============================================================

Executable created at:
  F:\Documentos\Python\FITS_Library\dist\FITS_Library.exe

File size: ~150-200 MB

To test the executable:
  .\dist\FITS_Library.exe
```

### Step 3: Test the Executable

```powershell
cd F:\Documentos\Python\FITS_Library\dist
.\FITS_Library.exe
```

**Test these features:**
- [ ] Application launches GUI
- [ ] Database scanning works
- [ ] FITS Viewer launches
- [ ] NINA JSON export works
- [ ] Plot functionality works

### Step 4a: Share Just the EXE (Simple)

Your colleagues can now:
1. Download `FITS_Library.exe`
2. Run it directly
3. Start using immediately

**No setup required!**

### Step 4b: Create Professional Installer (Advanced)

If you want a proper Windows installer:

1. **Install NSIS**
   - Download: http://nsis.sourceforge.net/Main_Page
   - Run installer and complete wizard

2. **Build the Installer**
   - Right-click `installer.nsi` in FITS_Library folder
   - Select "Compile NSIS script"
   - Wait for completion

3. **Output**
   - Creates: `FITS_Library_v2.3_Installer.exe` (~75-100 MB)
   - This is what you share with colleagues

4. **Colleagues Install By**
   - Download installer
   - Run `.exe` file
   - Follow installation wizard
   - Shortcuts appear in Start Menu and Desktop
   - Can uninstall via Programs and Features

---

## Distribution

### For Simple EXE Distribution:

**File:** `dist/FITS_Library.exe`

**Share via:**
- Email (if < 25 MB, check after compression)
- Google Drive / OneDrive / DropBox
- GitHub Releases
- Direct download link

**Size:** ~150-200 MB

**Colleagues do:**
1. Download FITS_Library.exe
2. Save anywhere on their computer
3. Double-click to launch
4. Done!

### For Professional Installer Distribution:

**File:** `FITS_Library_v2.3_Installer.exe`

**Share via:**
- Same methods as above
- More professional appearance

**Colleagues do:**
1. Download FITS_Library_v2.3_Installer.exe
2. Run the installer
3. Choose installation location (default: C:\Program Files\FITS_Library)
4. Shortcuts created automatically
5. Can be removed via Programs and Features

**Size after compression:** ~70-120 MB

---

## Troubleshooting

### "PyInstaller not found"
```powershell
pip install pyinstaller
```

### Build takes a very long time (>30 min)
- This is normal for first build
- Subsequent builds are faster
- Total time depends on system speed

### EXE file is very large (200+ MB)
- Normal! Includes all Python libraries + dependencies
- Can't be reduced much (core requirements)

### "FITS_Viewer folder not found"
- Ensure FITS_Viewer folder exists: `F:\Documentos\Python\FITS_Library\FITS_Viewer`
- Edit build_exe.py if folder structure is different

### EXE won't launch on colleagues' computers
- Make sure Windows Defender/Antivirus allows it
- Check Windows version (7+)
- Verify they have Visual C++ Redistributable installed (usually pre-installed)

### To distribute a fix/update
- Simply delete `build/` and `dist/` folders
- Run `python build_exe.py` again
- Creates new EXE with latest code

---

## What Gets Included in EXE

✅ **Included automatically:**
- astropy (FITS file reading)
- pandas (data handling)
- matplotlib (plotting)
- numpy (calculations)
- tkinter (GUI)
- All Python standard library

✅ **Bundled specially:**
- FITS_Viewer folder and all contents

✅ **Not included (not needed):**
- Source .py files (compiled into EXE)
- Test files
- Documentation (stays as separate files if needed)

---

## Quick Reference

```powershell
# Install PyInstaller (one-time)
pip install pyinstaller

# Build simple EXE
cd F:\Documentos\Python\FITS_Library
python build_exe.py

# Test it
.\dist\FITS_Library.exe

# Share dist\FITS_Library.exe with colleagues
```

## File Locations After Build

```
FITS_Library/
├── build/                          (temporary, can delete)
├── dist/
│   └── FITS_Library.exe           ← Share this!
├── build_exe.py                   (the build script)
├── fits_gui_database.py           (source code)
├── installer.nsi                  (for NSIS installer)
└── FITS_Viewer/                   (automatically bundled in EXE)
```

---

## Next Steps

1. Run: `python build_exe.py`
2. Test: `.\dist\FITS_Library.exe`
3. Share: `dist/FITS_Library.exe` with colleagues
4. They run it - no Python needed!

**You're done!** 🎉
