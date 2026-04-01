; FITS Database Installer (NSIS)
; 
; This script creates a professional installer for FITS_Database
; 
; To build:
;   1. Install NSIS: http://nsis.sourceforge.net/
;   2. Right-click this file and select "Compile NSIS script"
;   3. Output: FITS_Database_v2.3_Installer.exe

!include "MUI2.nsh"
!include "x64.nsh"

; Basic settings
Name "FITS Database v2.3"
OutFile "FITS_Database_v2.3_Installer.exe"
InstallDir "$PROGRAMFILES\FITS_Database"
RequestExecutionLevel admin

; UI settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install FITS Library"
  SetOutPath "$INSTDIR"
  
  ; Copy main executable
  File "dist\FITS_Library.exe"
  
  ; Copy documentation and config files
  File "*.md"
  File "requirements.txt"
  File "*.bat"
  
  ; Copy FITS_Viewer folder and contents
  SetOutPath "$INSTDIR\FITS_Viewer"
  File /r "FITS_Viewer\*.*"
  
  ; Create start menu shortcuts (Windows)
  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\FITS Database"
  CreateShortCut "$SMPROGRAMS\FITS Database\FITS Database.lnk" "$INSTDIR\FITS_Database.exe" "" "$INSTDIR\FITS_Database.exe" 0
  CreateShortCut "$SMPROGRAMS\FITS Database\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\FITS Database.lnk" "$INSTDIR\FITS_Database.exe" "" "$INSTDIR\FITS_Database.exe" 0
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Write installation info to registry (for Programs and Features)
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayName" "FITS Database v2.3"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayVersion" "2.3"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database" "DisplayIcon" "$INSTDIR\FITS_Database.exe"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove shortcuts
  Delete "$DESKTOP\FITS Database.lnk"
  RMDir /r "$SMPROGRAMS\FITS Database"
  
  ; Remove files
  RMDir /r "$INSTDIR\FITS_Viewer"
  Delete "$INSTDIR\FITS_Database.exe"
  Delete "$INSTDIR\*.md"
  Delete "$INSTDIR\*.bat"
  Delete "$INSTDIR\*.txt"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove directory
  RMDir "$INSTDIR"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FITS_Database"
SectionEnd

; Functions
Function .onInstSuccess
  MessageBox MB_OK "FITS Database has been successfully installed!$\n$\nYou can now launch it from the Start Menu or Desktop."
FunctionEnd
