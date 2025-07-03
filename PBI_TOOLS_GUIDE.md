# PBI-Tools Auto-Installation Guide

This guide explains how the automatic pbi-tools installation feature works in TableauToPBI.

## Features

✅ **Automatic Detection**: Checks if pbi-tools is already installed  
✅ **Auto-Download**: Downloads latest version from GitHub releases  
✅ **Cross-Platform**: Works on Windows, Linux, and macOS  
✅ **PATH Management**: Automatically adds pbi-tools to system PATH  
✅ **Update Checking**: Detects when updates are available  
✅ **Version Compatibility**: Handles version mismatches gracefully  

## Usage

### Basic Conversion (Auto-Install Enabled)
```bash
# This will automatically install pbi-tools if needed
python src/extractors/TB2PBI/tableau_to_powerbi.py convert input.twbx output.pbit
```

### Disable Auto-Install
```bash
# Skip automatic installation
python src/extractors/TB2PBI/tableau_to_powerbi.py convert input.twbx output.pbit --no-auto-install
```

### Manual pbi-tools Management

#### Check Installation Status
```bash
python src/extractors/TB2PBI/tableau_to_powerbi.py pbi-tools status
```

#### Install pbi-tools
```bash
python src/extractors/TB2PBI/tableau_to_powerbi.py pbi-tools install
```

#### Update pbi-tools
```bash
python src/extractors/TB2PBI/tableau_to_powerbi.py pbi-tools update
```

#### Force Reinstall
```bash
python src/extractors/TB2PBI/tableau_to_powerbi.py pbi-tools reinstall
```

#### Uninstall
```bash
python src/extractors/TB2PBI/tableau_to_powerbi.py pbi-tools uninstall
```

## Installation Process

1. **Detection**: Checks if pbi-tools is already installed using `pbi-tools` command
2. **Version Check**: Compares installed version with latest GitHub release
3. **Platform Detection**: Determines OS and architecture (Windows x64, Linux x64, etc.)
4. **Download**: Downloads appropriate binary from GitHub releases
5. **Extraction**: Extracts to `~/.pbi-tools/bin/` directory
6. **PATH Update**: Adds installation directory to system PATH
7. **Verification**: Tests installation by running pbi-tools

## Installation Locations

### Default Installation Directory
- **Windows**: `C:\Users\{username}\.pbi-tools\bin\`
- **Linux/macOS**: `~/.pbi-tools/bin/`

### PATH Configuration
- **Windows**: Updates user PATH via `setx` command
- **Linux/macOS**: Adds export to `.bashrc`, `.bash_profile`, `.zshrc`, or `.profile`

## Troubleshooting

### Permission Issues
If you encounter permission errors:
```bash
# Run as administrator on Windows
# Use sudo on Linux/macOS if needed
```

### PATH Not Updated
If pbi-tools is not found after installation:
1. **Restart terminal/IDE**
2. **Check PATH manually**:
   ```bash
   echo $PATH  # Linux/macOS
   echo %PATH%  # Windows
   ```
3. **Manual PATH update**:
   ```bash
   # Add to your shell profile
   export PATH="$HOME/.pbi-tools/bin:$PATH"
   ```

### Version Compatibility
If compilation fails due to version mismatch:
1. **Update pbi-tools**: Use the update command
2. **Check Power BI Desktop version**: Ensure compatibility
3. **Use project files manually**: Import into Power BI Desktop directly

### Network Issues
If download fails:
1. **Check internet connection**
2. **Check proxy settings**
3. **Manual download**: Get from [GitHub releases](https://github.com/pbi-tools/pbi-tools/releases)

## Manual Installation (Fallback)

If auto-installation fails, you can install manually:

### Option 1: Chocolatey (Windows)
```bash
choco install pbi-tools
```

### Option 2: Manual Download
1. Go to [pbi-tools releases](https://github.com/pbi-tools/pbi-tools/releases)
2. Download appropriate version for your platform
3. Extract to a directory
4. Add directory to PATH

### Option 3: Use Project Files Only
If pbi-tools installation fails completely:
1. The converter will still create project files
2. Open Power BI Desktop
3. File → Open → Browse to project folder
4. File → Export → Power BI Template (.pbit)

## Integration with TableauToPBI

The auto-installer is seamlessly integrated:

```python
from tableau_to_powerbi import TableauToPowerBIConverter

# Auto-install enabled by default
converter = TableauToPowerBIConverter(auto_install_pbi_tools=True)

# Disable auto-install
converter = TableauToPowerBIConverter(auto_install_pbi_tools=False)

# Manual installer access
from tableau_to_powerbi import PBIToolsInstaller
installer = PBIToolsInstaller()
installer.install_or_update()
```

## Security Considerations

- Downloads are verified from official GitHub releases
- Installation occurs in user directory (no admin rights needed)
- Source code is open and auditable
- No modification of system-wide settings (except user PATH)

## Contributing

If you encounter issues with the auto-installer:
1. Check the logs for error messages
2. Report issues with OS/platform details
3. Include error output and system information
