; Speech Coach Windows Installer Script
; This creates a proper Windows installer with desktop shortcuts

!define APPNAME "Speech Coach"
!define COMPANYNAME "Speech Coach Development"
!define DESCRIPTION "Professional Communication Trainer"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/speech-coach"
!define UPDATEURL "https://github.com/yourusername/speech-coach/releases"
!define ABOUTURL "https://github.com/yourusername/speech-coach"
!define INSTALLSIZE 200000 ; Size in KB (roughly 200MB)

RequestExecutionLevel admin ; Require admin rights

InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"
LicenseData "LICENSE"
Name "${APPNAME}"
Icon "assets\speech_coach_icon.ico"
outFile "SpeechCoach-v${VERSIONMAJOR}.${VERSIONMINOR}-windows-installer.exe"

!include LogicLib.nsh

page license
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ; Require admin rights
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740 ; ERROR_ELEVATION_REQUIRED
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    # Files for the install directory - to build the installer, these should be in the installer's directory
    setOutPath $INSTDIR
    
    # Main executable
    file "dist\SpeechCoach.exe"
    
    # Documentation
    file "README.md"
    file "DISTRIBUTION.md"
    
    # Create uninstaller
    writeUninstaller "$INSTDIR\uninstall.exe"

    # Desktop shortcut
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SpeechCoach.exe" "" "$INSTDIR\SpeechCoach.exe"
    
    # Start menu shortcuts
    createDirectory "$SMPROGRAMS\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\SpeechCoach.exe" "" "$INSTDIR\SpeechCoach.exe"
    createShortCut "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"

    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\SpeechCoach.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

sectionEnd

# Uninstaller
function un.onInit
    SetShellVarContext all
    MessageBox MB_OKCANCEL "Are you sure you want to remove ${APPNAME}?" IDOK next
        Abort
    next:
    !insertmacro VerifyUserIsAdmin
functionEnd

section "uninstall"
    # Remove Start Menu launcher
    delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk"
    rmDir "$SMPROGRAMS\${COMPANYNAME}"

    # Remove desktop shortcut
    delete "$DESKTOP\${APPNAME}.lnk"

    # Remove files
    delete "$INSTDIR\SpeechCoach.exe"
    delete "$INSTDIR\README.md"
    delete "$INSTDIR\DISTRIBUTION.md"

    # Remove uninstaller
    delete "$INSTDIR\uninstall.exe"

    # Try to remove the install directory
    rmDir "$INSTDIR"

    # Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
sectionEnd
