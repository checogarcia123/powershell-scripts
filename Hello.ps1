# Ensure the temp directory exists
New-Item -Path "C:\Temp" -ItemType Directory -Force | Out-Null
 
# Write a confirmation message to a file
"Ansible ran after reboot at $(Get-Date)" | Out-File "C:\Temp\Ansible_Ran.txt" -Force
