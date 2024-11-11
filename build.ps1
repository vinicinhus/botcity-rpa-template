# Define arrays for exclusion
$excludeVirtualEnvs = @(".env", "env", ".venv", "venv")
$excludeFolders = @("logs") # Add more folders if needed

$exclude = $excludeVirtualEnvs + $excludeFolders + "project_template.zip"

# Get the files excluding specified folders and virtual envs
$files = Get-ChildItem -Path . -Exclude $exclude -Recurse

# Compress the files
Compress-Archive -Path $files -DestinationPath "project.zip" -Force