#Requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('Security','System','Microsoft-Windows-Sysmon/Operational')]
    [string]$LogName='Security',
    [ValidateRange(1,1440)][int]$LastMinutes=15,
    [ValidateRange(1,10000)][int]$MaxEvents=500,
    [string]$OutputPath='.\artifacts\events.xml'
)
$ErrorActionPreference='Stop'
if (Test-Path -LiteralPath $OutputPath) { throw 'Choose a new filename; existing evidence will not be overwritten.' }
$events=@(Get-WinEvent -FilterHashtable @{LogName=$LogName; StartTime=(Get-Date).AddMinutes(-$LastMinutes)} -MaxEvents $MaxEvents)
$fullPath=[IO.Path]::GetFullPath($OutputPath)
$parent=Split-Path -Parent $fullPath
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$stream=[IO.File]::Open($fullPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write)
$writer=New-Object IO.StreamWriter($stream, (New-Object Text.UTF8Encoding($false)))
try {
    $writer.WriteLine('<Events>')
    foreach ($event in $events) { $writer.WriteLine($event.ToXml()) }
    $writer.WriteLine('</Events>')
} finally { $writer.Dispose() }
Write-Output "Exported $($events.Count) events. Review/redact identities and addresses before publication."
