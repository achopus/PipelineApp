# PipelineApp Installer Script for NSIS
# This creates a Windows installer that packages the application

!define APP_NAME "PipelineApp"
!define APP_VERSION "1.0.0"
!define PUBLISHER "Video Tracking Pipeline"
!define WEB_SITE "https://github.com/achopus/PipelineApp"
!define COPYRIGHT "© 2025 ${PUBLISHER}"
!define DESCRIPTION "Video Tracking Pipeline Application"
!define INSTALLER_NAME "PipelineApp_Setup.exe"
!define MAIN_APP_EXE "PipelineApp.exe"
!define INSTALL_TYPE "SetShellVarContext current"
!define REG_ROOT "HKCU"
!define REG_APP_PATH "Software\Microsoft\Windows\CurrentVersion\App Paths\${MAIN_APP_EXE}"
!define UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

# MUI Settings / Icons
!define MUI_ICON "resources\rat_icon.ico"
!define MUI_UNICON "resources\rat_icon.ico"

# MUI Settings / Header
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP "resources\rat_icon.ico"
!define MUI_HEADERIMAGE_UNBITMAP "resources\rat_icon.ico"

# MUI Settings / Wizard
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\rat_icon.ico"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "resources\rat_icon.ico"

######################################################################

VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${PUBLISHER}"
VIAddVersionKey "LegalCopyright" "${COPYRIGHT}"
VIAddVersionKey "FileDescription" "${DESCRIPTION}"
VIAddVersionKey "FileVersion" "${APP_VERSION}.0"

######################################################################

SetCompressor lzma
Name "${APP_NAME}"
Caption "${APP_NAME}"
OutFile "${INSTALLER_NAME}"
BrandingText "${APP_NAME}"
XPStyle on
InstallDirRegKey "${REG_ROOT}" "${REG_APP_PATH}" ""
InstallDir "$LOCALAPPDATA\${APP_NAME}"

######################################################################

!include "MUI.nsh"

!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

!insertmacro MUI_PAGE_WELCOME

!ifdef LICENSE_TXT
!insertmacro MUI_PAGE_LICENSE "${LICENSE_TXT}"
!endif

!insertmacro MUI_PAGE_DIRECTORY

!ifdef REG_START_MENU
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "PipelineApp"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${REG_ROOT}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${UNINSTALL_PATH}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${REG_START_MENU}"
!insertmacro MUI_PAGE_STARTMENU Application $SM_Folder
!endif

!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_RUN "$INSTDIR\${MAIN_APP_EXE}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

######################################################################

Section -MainProgram
${INSTALL_TYPE}
SetOverwrite ifnewer
SetOutPath "$INSTDIR"

# Copy main executable
File "dist\${MAIN_APP_EXE}"

# Copy any additional resources
File /r "resources\"

SectionEnd

######################################################################

Section -Icons_Reg
SetOutPath "$INSTDIR"
WriteUninstaller "$INSTDIR\uninstall.exe"

!ifdef REG_START_MENU
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
CreateDirectory "$SMPROGRAMS\$SM_Folder"
CreateShortCut "$SMPROGRAMS\$SM_Folder\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}"
CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}"
CreateShortCut "$SMPROGRAMS\$SM_Folder\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"

!ifdef WEB_SITE
WriteIniStr "$INSTDIR\${APP_NAME} website.url" "InternetShortcut" "URL" "${WEB_SITE}"
CreateShortCut "$SMPROGRAMS\$SM_Folder\${APP_NAME} Website.lnk" "$INSTDIR\${APP_NAME} website.url"
!endif
!insertmacro MUI_STARTMENU_WRITE_END
!endif

!ifndef REG_START_MENU
CreateDirectory "$SMPROGRAMS\PipelineApp"
CreateShortCut "$SMPROGRAMS\PipelineApp\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}"
CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}"
CreateShortCut "$SMPROGRAMS\PipelineApp\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"

!ifdef WEB_SITE
WriteIniStr "$INSTDIR\${APP_NAME} website.url" "InternetShortcut" "URL" "${WEB_SITE}"
CreateShortCut "$SMPROGRAMS\PipelineApp\${APP_NAME} Website.lnk" "$INSTDIR\${APP_NAME} website.url"
!endif
!endif

WriteRegStr "${REG_ROOT}" "${REG_APP_PATH}" "" "$INSTDIR\${MAIN_APP_EXE}"
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "DisplayName" "${APP_NAME}"
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "UninstallString" "$INSTDIR\uninstall.exe"
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "DisplayIcon" "$INSTDIR\${MAIN_APP_EXE}"
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "DisplayVersion" "${APP_VERSION}"
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "Publisher" "${PUBLISHER}"

!ifdef WEB_SITE
WriteRegStr "${REG_ROOT}" "${UNINSTALL_PATH}" "URLInfoAbout" "${WEB_SITE}"
!endif
SectionEnd

######################################################################

Section Uninstall
${INSTALL_TYPE}
Delete "$INSTDIR\${MAIN_APP_EXE}"
Delete "$INSTDIR\uninstall.exe"
!ifdef WEB_SITE
Delete "$INSTDIR\${APP_NAME} website.url"
!endif

RmDir /r "$INSTDIR\resources"

!ifdef REG_START_MENU
!insertmacro MUI_STARTMENU_GETFOLDER "Application" $SM_Folder
Delete "$SMPROGRAMS\$SM_Folder\${APP_NAME}.lnk"
Delete "$SMPROGRAMS\$SM_Folder\Uninstall ${APP_NAME}.lnk"
!ifdef WEB_SITE
Delete "$SMPROGRAMS\$SM_Folder\${APP_NAME} Website.lnk"
!endif
RmDir "$SMPROGRAMS\$SM_Folder"
!endif

!ifndef REG_START_MENU
Delete "$SMPROGRAMS\PipelineApp\${APP_NAME}.lnk"
Delete "$SMPROGRAMS\PipelineApp\Uninstall ${APP_NAME}.lnk"
!ifdef WEB_SITE
Delete "$SMPROGRAMS\PipelineApp\${APP_NAME} Website.lnk"
!endif
RmDir "$SMPROGRAMS\PipelineApp"
!endif

Delete "$DESKTOP\${APP_NAME}.lnk"

RmDir "$INSTDIR"

DeleteRegKey "${REG_ROOT}" "${REG_APP_PATH}"
DeleteRegKey "${REG_ROOT}" "${UNINSTALL_PATH}"
SectionEnd

######################################################################
