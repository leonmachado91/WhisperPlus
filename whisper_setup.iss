; WhisperPlus - Inno Setup Script
; Compile this with Inno Setup Compiler (https://jrsoftware.org/isinfo.php)
; to generate a professional "Next > Next > Finish" Windows installer.

[Setup]
AppName=WhisperPlus
AppVersion=1.0
AppPublisher=WhisperPlus
DefaultDirName={localappdata}\WhisperPlus
DefaultGroupName=WhisperPlus
OutputDir=Output
OutputBaseFilename=Setup_WhisperPlus
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
DisableWelcomePage=no
DisableDirPage=no
SetupIconFile=

[Files]
; Copy project files, excluding generated/temp content
Source: "server_with_export.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "launcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "start.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "pyproject.toml"; DestDir: "{app}"; Flags: ignoreversion
Source: "uv.lock"; DestDir: "{app}"; Flags: ignoreversion
Source: "whisperlivekit\*"; DestDir: "{app}\whisperlivekit"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "WhisperPlus.exe"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{src}\WhisperPlus.exe'))
Source: "WhisperPlus.spec"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\bin"
Name: "{app}\input"
Name: "{app}\output"

[Icons]
Name: "{group}\WhisperPlus"; Filename: "{app}\WhisperPlus.exe"; WorkingDir: "{app}"
Name: "{group}\WhisperPlus (Terminal)"; Filename: "{app}\start.bat"; WorkingDir: "{app}"
Name: "{group}\Desinstalar WhisperPlus"; Filename: "{uninstallexe}"

[Run]
; Run install.bat after file copy to download dependencies
Filename: "{app}\install.bat"; Description: "Baixar dependencias (Python, PyTorch, FFmpeg)"; Flags: postinstall waituntilterminated

[Code]
function FileExists(Path: string): Boolean;
begin
  Result := FileExists(Path);
end;
