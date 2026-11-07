#Requires -Version 5.1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
# Read-only inventory. Does not install software, change auditing or change accounts.
$os = Get-CimInstance Win32_OperatingSystem
$computer = Get-CimInstance Win32_ComputerSystem
$services = @(Get-Service -Name NTDS,DNS,Splunkd,SplunkForwarder,Sysmon,Sysmon64 -ErrorAction SilentlyContinue |
    Select-Object Name,Status)
$channels = foreach ($name in @('Security','System','Microsoft-Windows-Sysmon/Operational')) {
    try {
        $channel = Get-WinEvent -ListLog $name -ErrorAction Stop
        [PSCustomObject]@{Name=$name; Enabled=$channel.IsEnabled; RecordCount=$channel.RecordCount; Error=$null}
    } catch {
        [PSCustomObject]@{Name=$name; Enabled=$null; RecordCount=$null; Error=$_.Exception.Message}
    }
}
[PSCustomObject]@{
    CollectedAtUtc=(Get-Date).ToUniversalTime().ToString('o')
    ComputerName=$env:COMPUTERNAME
    OS=$os.Caption
    Build=$os.BuildNumber
    Domain=$computer.Domain
    PartOfDomain=$computer.PartOfDomain
    DomainRole=$computer.DomainRole
    Services=$services
    EventChannels=@($channels)
} | ConvertTo-Json -Depth 5
