# Manual Power BI Compilation Guide

## When pbi-tools Fails Due to Version Compatibility

If you're getting `System.MissingMethodException` errors when using pbi-tools, it's likely due to a version mismatch between pbi-tools and your Power BI Desktop installation.

## Current Issue
- **Power BI Desktop Version**: 2.144.1155.0 (June 2025)
- **pbi-tools Version**: 1.2.0 (built for 2.138.782.0)
- **Problem**: API methods have changed between versions

## Solutions

### Option 1: Update pbi-tools (Recommended)

```bash
# Update via Chocolatey
choco upgrade pbi-tools

# Or check for latest release
# Visit: https://github.com/pbi-tools/pbi-tools/releases
```

### Option 2: Use Project Files Manually

If pbi-tools still fails, you can use the generated project files manually:

1. **Locate Project Files**: Find the `{filename}_project` folder in your output directory
2. **Open Power BI Desktop**: Launch Power BI Desktop
3. **Import from Folder**: 
   - File → Import → Power BI project folder
   - Select the project folder created by the converter
4. **Save as Template**: File → Export → Power BI Template (.pbit)

### Option 3: Use Alternative Compilation Method

Create a PowerShell script to use Power BI Desktop directly:

```powershell
# save_as_pbit.ps1
param(
    [string]$ProjectPath,
    [string]$OutputPath
)

# Start Power BI Desktop with the project
$pbiPath = "C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_*\bin\PBIDesktop.exe"
$actualPath = Get-ChildItem $pbiPath | Sort-Object LastWriteTime -Desc | Select-Object -First 1

& $actualPath.FullName $ProjectPath
```

### Option 4: Downgrade Power BI Desktop

**⚠️ Not recommended for production environments**

Download an older version of Power BI Desktop compatible with pbi-tools 1.2.0:
- Version 2.138.x from Microsoft downloads archive

## What the Converter Still Provides

Even when .pbit compilation fails, the converter still creates:

### ✅ Complete Project Structure
```
{filename}_project/
├── DataModelSchema/
│   ├── Model.bim          # Complete data model
│   ├── connections.json   # Data connections
│   └── DiagramLayout     # Model layout
├── Report/
│   ├── Layout            # Report layout
│   └── StaticResources.json
├── ReportMetadata.json   # Report metadata
├── ReportSettings.json   # Report settings
├── SecurityBindings.json # Security settings
├── Settings              # Project settings
├── Metadata             # Project metadata
└── Version.txt          # Version info
```

### ✅ Manual Import Process

1. **Open Power BI Desktop**
2. **File → Open → Browse**
3. **Navigate to project folder**
4. **Select the folder** (not individual files)
5. **Power BI will import the project**
6. **File → Export → Power BI Template** to save as .pbit

## Verification Steps

After manual compilation:

1. **Open the .pbit file** in Power BI Desktop
2. **Check data sources** are properly configured
3. **Verify calculated fields** are present
4. **Test report functionality**
5. **Save/publish** as needed

## Future Compatibility

- **Monitor pbi-tools updates** for newer Power BI Desktop support
- **Consider using Power BI REST APIs** for programmatic deployment
- **Test with each Power BI Desktop update** before upgrading

---

**Note**: The Tableau to Power BI converter focuses on creating the correct project structure. The compilation step is just the final packaging - the real conversion work is complete even without .pbit generation.
