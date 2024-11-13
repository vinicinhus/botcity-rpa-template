# Define arrays for exclusion
$excludeVirtualEnvs = @(".env", "env", ".venv", "venv")
$excludeFolders = @("logs") # Add more folders if needed

# Get the current folder name and set zip file name
$currentFolderName = Split-Path -Path (Get-Location) -Leaf
$zipFileName = "$currentFolderName.zip"

# Add the zip file name to the exclusion list
$exclude = $excludeVirtualEnvs + $excludeFolders + $zipFileName

# Get the files excluding specified folders, virtual envs, and the zip file itself
$files = Get-ChildItem -Path . -Exclude $exclude

# Compress the files
Compress-Archive -Path $files -DestinationPath $zipFileName -Force
