; Weekly Planner Installer

[Setup]
AppName=Weekly Planner
AppVersion=1.0
DefaultDirName={autopf}\Weekly Planner
DefaultGroupName=Weekly Planner
OutputDir=installer
OutputBaseFilename=WeeklyPlannerSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\WeeklyPlanner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "memory\timetable.json"; DestDir: "{app}\memory"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\Weekly Planner"; Filename: "{app}\WeeklyPlanner.exe"
Name: "{group}\Weekly Planner"; Filename: "{app}\WeeklyPlanner.exe"