# PowerShell script to help with Power BI project import
# Save as: import_pbi_project.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath
)

Write-Host "Power BI Project Import Helper" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

$projectPath = Resolve-Path $ProjectPath
Write-Host "Project path: $projectPath" -ForegroundColor Yellow

# Check if project structure is valid
$requiredFiles = @(
    "DataModelSchema\Model.bim",
    "Version.txt",
    "Metadata"
)

Write-Host "`nChecking project structure..." -ForegroundColor Yellow
$allFilesExist = $true

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $projectPath $file
    if (Test-Path $fullPath) {
        Write-Host "✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "`n🎉 Project structure is valid!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Open Power BI Desktop" -ForegroundColor White
    Write-Host "2. File → Import → Power BI Project (if available)" -ForegroundColor White
    Write-Host "3. OR: Get Data → Analysis Services → Import BIM file:" -ForegroundColor White
    Write-Host "   $projectPath\DataModelSchema\Model.bim" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Project structure is incomplete" -ForegroundColor Red
}

# Try to launch Power BI Desktop
$pbiPath = Get-ChildItem "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_*\bin\PBIDesktop.exe" | Sort-Object LastWriteTime -Desc | Select-Object -First 1

if ($pbiPath) {
    Write-Host "`n💡 Would you like to launch Power BI Desktop? (y/n): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "🚀 Launching Power BI Desktop..." -ForegroundColor Green
        Start-Process $pbiPath.FullName
    }
} else {
    Write-Host "`n⚠️  Power BI Desktop not found in standard location" -ForegroundColor Yellow
}
