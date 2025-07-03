# Manual Power BI Compilation Guide

## 🚨 Common Error: MissingMethodException

**Error Message:**
```
System.MissingMethodException: Method not found: 'Void Microsoft.PowerBI.Packaging.PowerBIPackager.Save
```

**Cause:** Version mismatch between pbi-tools and Power BI Desktop. Your Power BI Desktop (2.144.1155.0) is newer than what your pbi-tools version supports.

## Your Specific Issue
- **Power BI Desktop**: 2.144.1155.0 (June 2025)
- **pbi-tools**: Likely version 1.x (built for older PBI versions)
- **Problem**: The PowerBIPackager.Save method signature changed in newer Power BI Desktop versions

## 📋 Manual Compilation Steps

### Step 1: Locate Your Project Files
After running the TableauToPBI converter, you'll have a project directory:
```
C:\Users\nvave\Documents\Projects\Python\TableauToPBI\output\helloworld_project\
├── DataModelSchema/
│   ├── Model.bim
│   ├── connections.json
│   └── DiagramLayout
├── Report/
│   ├── Layout
│   └── StaticResources.json
├── Version.txt
├── Metadata
├── Settings
├── ReportMetadata.json
├── SecurityBindings.json
└── ReportSettings.json
```

### Step 2: Open in Power BI Desktop

1. **Launch Power BI Desktop**
   - Start → Power BI Desktop

2. **Open the Project Folder**
   - **File** → **Open**
   - Navigate to: `C:\Users\nvave\Documents\Projects\Python\TableauToPBI\output\helloworld_project\`
   - **Select the entire folder**, not individual files
   - Click **Open**

### Step 3: Export as Template

1. **File** → **Export** → **Power BI Template (.pbit)**
2. **Save as:** `C:\Users\nvave\Documents\Projects\Python\TableauToPBI\output\helloworld.pbit`
3. **Add description** if desired
4. Click **OK**

## 🔄 Alternative: Update pbi-tools

Try updating pbi-tools to latest version:

```bash
# Using the auto-installer
python tableau_to_powerbi.py pbi-tools update

# Or manual update via Chocolatey
choco upgrade pbi-tools

# Or download latest from GitHub
# https://github.com/pbi-tools/pbi-tools/releases
```

## 🔧 Troubleshooting

### Cannot Open Project Folder
- Ensure all required files are present
- Try opening `DataModelSchema/Model.bim` directly

### Data Connection Issues
- **Transform Data** → **Data Source Settings**
- Update connections to point to actual data sources

### Invalid Model Errors
- Check `Model.bim` is valid JSON
- Re-run converter if file is corrupted

## 💡 Success Tips

1. **Always use the latest Power BI Desktop**
2. **Keep pbi-tools updated**
3. **Manual compilation is often more reliable**
4. **Test with simple workbooks first**

This approach will get you a working `.pbit` file despite the version compatibility issues!

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
