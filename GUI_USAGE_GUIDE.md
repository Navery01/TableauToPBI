# Tableau to Power BI Converter - GUI Application

## Overview

The Tableau to Power BI Converter provides a user-friendly graphical interface for converting Tableau workbooks (.twb/.twbx files) to Power BI templates (.pbit files).

## Features

### 🎯 Core Functionality
- **Batch Conversion**: Convert multiple Tableau files simultaneously
- **File Analysis**: Analyze Tableau workbooks to understand their structure
- **Progress Tracking**: Real-time progress monitoring with detailed statistics
- **Comprehensive Logging**: Detailed conversion logs with timestamps
- **Flexible Output**: Generates both .pbit files and project directories

### 🔧 User Interface Features
- **Drag & Drop Support**: Easy file addition (planned)
- **Context Menus**: Right-click for file analysis and properties
- **Export Path Selection**: Choose where to save converted files
- **Conversion Options**: Configure preservation settings
- **Real-time Statistics**: Track queued, processed, and failed conversions

## Getting Started

### Prerequisites

1. **Python 3.8+** with required packages:
   ```bash
   pip install PySide6 tableauhyperapi
   ```

2. **pbi-tools** (optional but recommended):
   ```bash
   # Via Chocolatey
   choco install pbi-tools
   
   # Or download from GitHub
   # https://github.com/pbi-tools/pbi-tools/releases
   ```

### Launching the Application

```bash
# From the project root directory
python main.py
```

## Usage Guide

### 1. Adding Files

**Add Individual Files:**
- Click "Add Files" button
- Select .twb or .twbx files from the file dialog
- Multiple files can be selected at once

**Add Entire Folders:**
- Click "Add Folder" button
- Select a directory containing Tableau files
- All .twb/.twbx files in the folder will be added

**File Management:**
- Select files and click "Remove" to remove specific files
- Click "Clear All" to remove all files from the queue
- Right-click files for context menu options

### 2. Configuration

**Export Path:**
- Click "Browse" to select output directory
- Default: `./output` in the project directory

**Conversion Options:**
- ✅ **Preserve Connections**: Maintain data source connections
- ✅ **Preserve Formatting**: Keep visual formatting where possible
- ✅ **Create Log**: Generate detailed conversion logs
- ✅ **Include Data**: Include data extracts in conversion

### 3. File Analysis

**Analyze Individual Files:**
- Right-click on a file in the list
- Select "📊 Analyze Workbook"
- View detailed structure information including:
  - Data sources and field counts
  - Worksheets and their names
  - Calculated fields
  - Parameters
  - Dashboards

### 4. Running Conversions

**Start Conversion:**
- Ensure files are added and export path is set
- Click "Begin Migration"
- Monitor progress via:
  - Progress bar
  - Real-time statistics
  - Detailed output log

**During Conversion:**
- The interface remains responsive
- Progress updates in real-time
- Individual file results are logged
- "Begin Migration" button is disabled during processing

### 5. Monitoring Progress

**Statistics Panel:**
- **Files Queued**: Total files to be processed
- **Files Processed**: Successfully converted files
- **Process Time**: Elapsed time since start
- **Failures**: Number of failed conversions

**Output Log:**
- Timestamped progress messages
- Detailed error information
- Analysis results
- Final conversion summary

## Understanding Output

### Generated Files

For each converted Tableau file, the following is created:

1. **{filename}.pbit** - Power BI template file (if pbi-tools available)
2. **{filename}_project/** - Power BI project directory containing:
   - `DataModelSchema/Model.bim` - Data model definition
   - `Report/Layout` - Report layout
   - Various metadata files

### Conversion Success Indicators

✅ **Successful Conversion:**
- .pbit file created (if pbi-tools available)
- Project directory with all required files
- "✅ Successfully converted" message in log

❌ **Failed Conversion:**
- Error messages in output log
- Project files may still be created for manual compilation
- Specific error details provided

## Troubleshooting

### Common Issues

**"pbi-tools not found" Warning:**
- Install pbi-tools for complete .pbit generation
- Project files are still created for manual compilation
- Follow installation instructions in Prerequisites

**"No Files Selected" Error:**
- Add .twb or .twbx files before starting conversion
- Use "Add Files" or "Add Folder" buttons

**"Export Path Error":**
- Ensure the output directory is writable
- Check disk space availability
- Verify path permissions

**Conversion Failures:**
- Check output log for specific error details
- Verify input files are valid Tableau workbooks
- Ensure sufficient disk space for output

### Performance Tips

- **Large Files**: Allow extra time for complex workbooks
- **Batch Processing**: Process files in smaller batches if memory is limited
- **Disk Space**: Ensure adequate space for both project files and .pbit outputs

## Advanced Features

### Context Menu Options

Right-click on files in the list for:
- **📊 Analyze Workbook**: Detailed structure analysis
- **🗑️ Remove from List**: Remove selected files
- **ℹ️ Properties**: View file properties and metadata

### Log Management

- **Clear Log**: Remove all log entries
- **Save Log**: Export log to text file for later review

## Technical Notes

### Supported File Types
- **.twbx**: Tableau Workbook (packaged)
- **.twb**: Tableau Workbook (XML)

### Output Formats
- **.pbit**: Power BI Template (requires pbi-tools)
- **Project Directory**: Power BI project files for manual compilation

### Dependencies
- **PySide6**: GUI framework
- **tableauhyperapi**: Tableau file parsing (if using Hyper extracts)
- **pbi-tools**: Power BI compilation (optional but recommended)

## Support

For issues, questions, or contributions:
1. Check the output log for detailed error information
2. Verify all prerequisites are installed
3. Test with a simple Tableau file first
4. Review this guide for troubleshooting tips

---

**Version**: 1.0.0  
**Last Updated**: December 2024
