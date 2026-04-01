; FITS Database Installer Script
; NSIS Installer for FITS_Database v2.4

!include "MUI2.nsh"
!include "LogicLib.nsh"

; Basic settings
Name "FITS Database v2.4"
OutFile "dist/FITS_Database_v2.4_Installer.exe"
InstallDir "$PROGRAMFILES\FITS_Database"
InstallDirRegKey HKCU "Software\FITS Database" "Install_Dir"

; Request admin mode
RequestExecutionLevel admin

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy main executable
  File "dist\FITS_Database.exe"
  File "README.md"
  File "QUICK_START.md"
  File "USER_MANUAL.md"
  File "FEATURES_GUIDE.md"
  File "BUILD_INSTRUCTIONS.md"
  File "requirements.txt"
  
  ; Copy Python source if needed for development
  File "fits_gui_database.py"
  
  ; Copy FITS_Viewer folder
  SetOutPath "$INSTDIR\FITS_Viewer"
  File /r "FITS_Viewer\*.*"
  
  ; Copy FITS_Database folder
  SetOutPath "$INSTDIR\FITS_Database"
  File /r "FITS_Database\*.*"
  
  ; Create Start Menu shortcuts
  SetOutPath "$SMPROGRAMS\FITS Database"
  CreateShortcut "$SMPROGRAMS\FITS Database\FITS Database.lnk" "$INSTDIR\FITS_Database.exe" "" "$INSTDIR\FITS_Database.exe" 0
  CreateShortcut "$SMPROGRAMS\FITS Database\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\FITS Database.lnk" "$INSTDIR\FITS_Database.exe" "" "$INSTDIR\FITS_Database.exe" 0
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Registry entries
  WriteRegStr HKCU "Software\FITS Database" "Install_Dir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayName" "FITS Database v2.4"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayVersion" "2.4"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "Publisher" "Toro7777"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayIcon" "$INSTDIR\FITS_Database.exe"
  
  MessageBox MB_OK "FITS Database v2.4 has been installed successfully!$\n$\nYou can launch it from the Start Menu or Desktop shortcut."
SectionEnd

; Uninstaller
Section "Uninstall"
  ; Remove application files
  Delete "$INSTDIR\FITS_Database.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\QUICK_START.md"
  Delete "$INSTDIR\USER_MANUAL.md"
  Delete "$INSTDIR\FEATURES_GUIDE.md"
  Delete "$INSTDIR\BUILD_INSTRUCTIONS.md"
  Delete "$INSTDIR\requirements.txt"
  Delete "$INSTDIR\fits_gui_database.py"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove directories
  RMDir /r "$INSTDIR\FITS_Viewer"
  RMDir /r "$INSTDIR\FITS_Database"
  RMDir "$INSTDIR"
  
  ; Remove Start Menu shortcuts
  RMDir /r "$SMPROGRAMS\FITS Database"
  
  ; Remove desktop shortcut
  Delete "$DESKTOP\FITS Database.lnk"
  
  ; Remove registry entries
  DeleteRegKey HKCU "Software\FITS Database"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database"
  
  MessageBox MB_OK "FITS Database has been uninstalled."
SectionEnd
