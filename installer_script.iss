; ===========================================
; DownNest Installer - Inno Setup 6.x
; Professional Installation Wizard
; ===========================================

[Setup]
AppName=DownNest
AppVersion=1.0.1
AppPublisher=Isiyak Solomon
AppPublisherURL=https://github.com/isiyaksolomon-dev/downnest
AppSupportURL=mailto:isiyak.solomon.01@gmail.com
DefaultDirName={autopf}\DownNest
DefaultGroupName=DownNest
OutputBaseFilename=DownNest_Setup_1.0.1
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64 x86

; Modern UI Settings
WizardStyle=modern
WizardSizePercent=100
WizardImageStretch=no

; Setup Icons
SetupIconFile=icon.ico
UninstallIconFile=icon.ico

; License and Welcome
LicenseFile=LICENSE.txt

; Permissions and Requirements
PrivilegesRequired=admin
RestartIfNeededByRun=yes
AllowNoIcons=no

; Performance
ShowLanguageDialog=no
AlwaysShowDirOnReadyPage=yes
AlwaysShowGroupOnReadyPage=yes

; Output Settings
VersionInfoVersion=1.0.1.0
VersionInfoProductName=DownNest
VersionInfoProductVersion=1.0.1

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\downnest.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\config_default.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\DownNest"; Filename: "{app}\downnest.exe"; IconFilename: "{app}\icon.ico"; Comment: "Smart Downloads Organizer"; WorkingDir: "{app}"
Name: "{autodesktop}\DownNest"; Filename: "{app}\downnest.exe"; IconFilename: "{app}\icon.ico"; Comment: "Smart Downloads Organizer"; WorkingDir: "{app}"
Name: "{app}\License.txt"; Filename: "{app}\LICENSE.txt"

[Run]
Filename: "{app}\nssm.exe"; Parameters: "install DownNest ""{app}\downnest.exe"""; Flags: runhidden waituntilterminated; StatusMsg: "Installing DownNest service..."
Filename: "{app}\nssm.exe"; Parameters: "set DownNest Start SERVICE_AUTO_START"; Flags: runhidden waituntilterminated; StatusMsg: "Configuring service..."
Filename: "{app}\nssm.exe"; Parameters: "start DownNest"; Flags: runhidden waituntilterminated; StatusMsg: "Starting DownNest service..."

[UninstallRun]
Filename: "{app}\nssm.exe"; Parameters: "stop DownNest"; Flags: runhidden; StatusMsg: "Stopping DownNest service..."
Filename: "{app}\nssm.exe"; Parameters: "remove DownNest confirm"; Flags: runhidden; StatusMsg: "Removing DownNest service..."

[Registry]
Root: HKCU; Subkey: "Software\DownNest"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\DownNest"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\DownNest"; ValueType: string; ValueName: "Version"; ValueData: "1.0.1"

[Code]

// --------------------------------------------------------
// Welcome Page Custom Message
// --------------------------------------------------------
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := '🪺 Welcome to DownNest';
  WizardForm.WelcomeLabel2.Caption := 
    'Smart Downloads Organizer' + #13#13 +
    'DownNest automatically organizes your Downloads folder into categories:' + #13 +
    '  • Documents (PDF, DOCX, TXT, etc.)' + #13 +
    '  • Images (JPG, PNG, GIF, etc.)' + #13 +
    '  • Videos (MP4, AVI, MKV, etc.)' + #13 +
    '  • Music (MP3, WAV, FLAC, etc.)' + #13 +
    '  • Archives (ZIP, RAR, 7Z, etc.)' + #13 +
    '  • Installers (EXE, MSI, etc.)' + #13 +
    '  • Code (PY, JS, HTML, CSS, etc.)' + #13#13 +
    'Click Next to continue installation.';
end;

// --------------------------------------------------------
// Finish Page Custom Message
// --------------------------------------------------------
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedHeadingLabel.Caption := '🎉 Installation Complete!';
    WizardForm.FinishedLabel.Caption := 
      'DownNest has been successfully installed!' + #13#13 +
      'Your Downloads folders are now being monitored and organized automatically.' + #13#13 +
      '✅ DownNest Service: RUNNING' + #13#13 +
      'To manage DownNest:' + #13 +
      '  1. Press Windows Key + R' + #13 +
      '  2. Type: services.msc' + #13 +
      '  3. Find "DownNest" in the list' + #13#13 +
      'Service Status Options:' + #13 +
      '  • Right-click for Start / Stop / Restart' + #13 +
      '  • Runs automatically at system startup' + #13#13 +
      'Thank you for using DownNest!';
  end;
end;

// --------------------------------------------------------
// Procedure to prompt deletion of installer
// --------------------------------------------------------
procedure PromptDeleteInstaller();
var
  InstallerPath: string;
begin
  InstallerPath := ExpandConstant('{srcexe}');
  if FileExists(InstallerPath) then
  begin
    if MsgBox('Do you want to delete the installer file now?' + #13#13 + InstallerPath,
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      MsgBox('Cannot delete the installer while it is running. Please remove it manually after closing.', mbInformation, MB_OK);
    end;
  end;
end;

// --------------------------------------------------------
// Installation Success Message
// --------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(
      '✅ Installation Successful!' + #13#13 +
      'DownNest is now installed and running as a Windows service.' + #13#13 +
      'Your Downloads folders will be organized automatically:' + #13 +
      '  • New files are sorted immediately upon download' + #13 +
      '  • Existing files can be organized on demand' + #13 +
      '  • DownNest runs silently in the background' + #13#13 +
      'For more information, visit the README file in the installation folder.',
      mbInformation, MB_OK);

    // Prompt user to delete installer after installation
    PromptDeleteInstaller();
  end;
end;

// --------------------------------------------------------
// Uninstall Cleanup (ONLY remove installation folder)
// --------------------------------------------------------
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDir: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppDir := ExpandConstant('{app}');
    if DirExists(AppDir) then
    begin
      Log('Removing installation folder: ' + AppDir);
      try
        DelTree(AppDir, True, True, True);
        Log('✅ Installation folder removed successfully.');
      except
        Log('⚠️ Failed to remove installation folder: ' + AppDir);
      end;
    end;
  end;
end;
