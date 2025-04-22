$desktop = [Environment]::GetFolderPath("Desktop")
$filepath = Join-Path $desktop "Ansible_Ran.txt"
"Ansible ran after reboot at $(Get-Date)" | Out-File $filepath -Force
