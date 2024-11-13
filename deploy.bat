@echo off
title Project Python Script Runner

rem Define the variable for the project root directory
set "PROJECT_DIR=C:\Path\To\Your\Project"

rem Define the relative path to the Python script
set "PYTHON_SCRIPT=bot.py"

rem Navigate to the project directory
cd /d %PROJECT_DIR%

rem Run the Python script with Poetry
echo Running Python script with Poetry...
poetry run python %PYTHON_SCRIPT%

rem Check if the Python script executed successfully
if %errorlevel% equ 0 (
    echo Python executed successfully.

    echo Closing in 15 seconds...
    timeout /t 15

    exit /b 0
) else (
    echo Error executing the Python script.

    echo Closing in 15 seconds...
    timeout /t 15

    exit /b 1
)
