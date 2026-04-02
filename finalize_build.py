#!/usr/bin/env python3
import shutil
import os
import subprocess

os.chdir(r"F:\Documentos\Python\FITS_Database")

print("=" * 60)
print("FINALIZING MODERN GUI BUILD")
print("=" * 60 + "\n")

# Backup old
print("1. Backing up old executable...")
if os.path.exists("dist/FITS_Database.exe"):
    shutil.move("dist/FITS_Database.exe", "dist/FITS_Database_old_gui.exe")
    print("   ✓ Backed up to: dist/FITS_Database_old_gui.exe")

# Copy new
print("\n2. Installing new modern GUI executable...")
shutil.copy("dist_temp/fits_gui_database.exe", "dist/FITS_Database.exe")
print("   ✓ Installed: dist/FITS_Database.exe")

# Get sizes
old_size = os.path.getsize("dist/FITS_Database_old_gui.exe") / 1024 / 1024
new_size = os.path.getsize("dist/FITS_Database.exe") / 1024 / 1024

print(f"\n   Size comparison:")
print(f"   • Old GUI: {old_size:.2f} MB")
print(f"   • New GUI: {new_size:.2f} MB")

# Cleanup
print("\n3. Cleaning up build artifacts...")
shutil.rmtree("dist_temp")
if os.path.exists(".build_temp"):
    shutil.rmtree(".build_temp")
if os.path.exists("build_output.txt"):
    os.remove("build_output.txt")
if os.path.exists("build_errors.txt"):
    os.remove("build_errors.txt")
print("   ✓ Cleaned")

# Rebuild installer
print("\n4. Rebuilding NSIS installer...")
nsis_path = r"C:\Program Files (x86)\NSIS\makensis.exe"
if not os.path.exists(nsis_path):
    nsis_path = r"C:\Program Files\NSIS\makensis.exe"

if os.path.exists(nsis_path):
    result = subprocess.run([nsis_path, "installer.nsi"], capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✓ Installer rebuilt!")
        
        installer_size = os.path.getsize("dist/FITS_Database_v2.4_Installer.exe") / 1024 / 1024
        
        print("\n" + "=" * 60)
        print("✅ BUILD COMPLETE!")
        print("=" * 60)
        print("\n📦 Release Files Ready:")
        print(f"   • FITS_Database.exe ({new_size:.2f} MB)")
        print("     → Standalone executable with modern GUI")
        print(f"   • FITS_Database_v2.4_Installer.exe ({installer_size:.2f} MB)")
        print("     → Windows installer package")
        print("\n✨ Modern GUI Features:")
        print("   ✓ Dark/Light theme toggle")
        print("   ✓ Professional blue colors")
        print("   ✓ Import CSV button")
        print("   ✓ Session folder rename")
        print("   ✓ All v2.4 features")
        print("\n🎉 Ready to upload to GitHub release!")
    else:
        print("   ✗ Installer build failed")
        print(result.stderr)
else:
    print("   ⚠ NSIS not found")
    print("   Executables are ready but installer not rebuilt")

print("\n" + "=" * 60 + "\n")
