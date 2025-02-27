@echo off
setlocal enabledelayedexpansion

:: Set the source and destination directories
set "source_dir=E:\khalid\gamification_backend"
set "dest_dir=E:\khalid\hostfrontend"

:: Set the directories and files to be skipped
set "skip_dirs=GamificationVenv .git .idea"
set "skip_files=.env .gitignore"

:: Ensure destination directory exists
if not exist "%dest_dir%" mkdir "%dest_dir%"

:: Copy directories, skipping unwanted ones
for /D %%d in ("%source_dir%\*") do (
    set "dir_name=%%~nxd"
    set "skip=false"

    :: Check if the directory should be skipped
    for %%s in (%skip_dirs%) do (
        if /I "!dir_name!"=="%%s" set "skip=true"
    )

    if "!skip!"=="false" (
        echo Copying Directory: "%%d"
        xcopy "%%d" "%dest_dir%\%%~nxd" /E /H /Y /I
    )
)

:: Copy files, skipping unwanted ones
for %%f in ("%source_dir%\*") do (
    set "file_name=%%~nxf"
    set "skip=false"

    :: Check if the file should be skipped
    for %%s in (%skip_files%) do (
        if /I "!file_name!"=="%%s" set "skip=true"
    )

    if "!skip!"=="false" (
        echo Copying File: "%%f"
        xcopy "%%f" "%dest_dir%\" /H /Y
    )
)

echo Files and directories copied with exclusions.

:: Navigate to destination directory
cd /d "%dest_dir%"

:: Check if it's a git repository
if not exist ".git" (
    echo This is not a Git repository. Skipping Git operations.
    goto end
)

:: Get commit message from user
set /p commit_message="Enter commit message: "

:: Get branch name from user
set /p branch_name="Enter branch name to push: "

:: Execute Git commands
git add .
git commit -m "%commit_message%"
git push origin %branch_name%

echo Git changes pushed to %branch_name%.

:end
echo.
echo Press any key to exit...
pause > nul

endlocal
