# TableauToPBI

TableauToPBI is a robust Python tool designed to help users migrate Tableau workbooks to Microsoft Power BI templates. It provides multiple compilation methods to ensure reliable conversion even when standard tools are unavailable.

## 🌟 Key Features

- **Multi-format Support**: Convert Tableau workbooks (`.twb`/`.twbx`) to Power BI templates (`.pbit`)
- **Multiple Compilation Methods**: 6 different ways to create PBIT files
- **Robust Fallback System**: Automatically tries alternative methods when primary tools fail
- **Auto-installer**: Automatically installs and manages pbi-tools
- **GUI Dashboard**: User-friendly interface for batch processing
- **Docker Support**: Containerized execution for consistent environments
- **Enterprise Ready**: Supports Analysis Services and XMLA endpoints

## 🚀 Quick Start

### Option 1: Standard Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/TableauToPBI.git
cd TableauToPBI

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python src/app/app.py
```

### Option 2: Docker
```bash
# Build the container
docker build -t tableautopbi .

# Run with volume mounting
docker run --rm -v "$(pwd):/app/data" tableautopbi
```

## 🔧 Compilation Methods

This tool provides multiple ways to create Power BI templates:

| Method | Difficulty | Reliability | Speed | Auto-Available |
|--------|------------|-------------|--------|----------------|
| **pbi-tools** | Easy | High* | Fast | ✅ Auto-install |
| **Tabular Editor** | Easy | Very High | Fast | ⚙️ Auto-detect |
| **Manual ZIP** | Medium | High | Medium | ✅ Always |
| **Power BI Desktop** | Easy | High | Slow | ⚙️ Auto-detect |
| **Custom ZIP** | Medium | High | Fast | ✅ Always |
| **Analysis Services** | Hard | Medium | Medium | ⚙️ Enterprise |

*pbi-tools may have compatibility issues with newer Power BI Desktop versions

### 🎯 Recommended Setup

For the best experience, install Tabular Editor 2 (free):

```bash
# Automatic installation
python install_tabular_editor.py

# Or manual download from:
# https://tabulareditor.com/
```

## 📖 Usage

### Command Line Interface

```bash
# Convert a single file
python main.py convert input.twbx --output output.pbit

# Batch conversion
python main.py convert input_folder/ --output output_folder/

# Check available compilation methods
python alternative_compilers_demo.py --method check

# Test compilation methods
python alternative_compilers_demo.py --create-sample --method all
```

### GUI Application

```bash
# Launch the GUI
python src/app/app.py
```

Features:
- Drag & drop file selection
- Batch processing
- Real-time progress tracking
- Method selection
- Detailed logging

### Python API

```python
from src.extractors.TB2PBI.tableau_to_powerbi import EnhancedTableauToPowerBIConverter

converter = EnhancedTableauToPowerBIConverter()
result = converter.convert_workbook("input.twbx", "output.pbit")
```

## 🔍 Troubleshooting

### When pbi-tools Fails

If you see errors like:
- `MissingMethodException`
- `pbi-tools is incompatible`
- `System.IO.FileNotFoundException`

The tool automatically tries alternative methods:

1. **Tabular Editor** - Most reliable alternative
2. **Manual ZIP Creation** - Always works
3. **Power BI Desktop** - Manual process

### Common Issues

**Issue**: "No compilation methods succeeded"
**Solution**: 
```bash
# Install Tabular Editor
python install_tabular_editor.py

# Or check what's available
python alternative_compilers_demo.py --method check
```

**Issue**: "Model.bim not found"
**Solution**: Ensure Tableau workbook was properly extracted and processed

**Issue**: "PBIT file corrupted"
**Solution**: Try different compilation method or check disk space

## 📁 Project Structure

```
TableauToPBI/
├── src/
│   ├── app/                    # GUI application
│   ├── extractors/            # Tableau extraction logic
│   │   └── TB2PBI/           # Core conversion engine
│   └── utils/                # Utility functions
├── examples/                  # Sample files
├── output/                   # Generated PBIT files
├── docs/                     # Documentation
│   ├── ALTERNATIVE_COMPILATION_GUIDE.md
│   ├── PBI_TOOLS_GUIDE.md
│   └── MANUAL_COMPILATION_GUIDE.md
├── alternative_compilers_demo.py  # Test compilation methods
├── install_tabular_editor.py      # Auto-installer
├── main.py                        # CLI entry point
└── requirements.txt
```

## 📚 Documentation

- **[Alternative Compilation Guide](ALTERNATIVE_COMPILATION_GUIDE.md)** - Complete guide to all compilation methods
- **[PBI Tools Guide](PBI_TOOLS_GUIDE.md)** - Managing pbi-tools installation and updates
- **[Manual Compilation Guide](MANUAL_COMPILATION_GUIDE.md)** - Step-by-step manual processes
- **[GUI Usage Guide](GUI_USAGE_GUIDE.md)** - Using the graphical interface

## 🛠️ Requirements

### Minimum Requirements
- Python 3.8+
- Windows, macOS, or Linux

### Optional Tools (Auto-detected)
- **Tabular Editor 2/3** - Best alternative to pbi-tools
- **Power BI Desktop** - For manual compilation
- **pbi-tools** - Primary compilation tool (auto-installed)

### Python Dependencies
```
requests>=2.25.0
pathlib
zipfile
json
xml.etree.ElementTree
tkinter (usually included with Python)
PySide6 (optional, for enhanced GUI)
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/your-repo/TableauToPBI.git
cd TableauToPBI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Running Tests

```bash
# Test all compilation methods
python alternative_compilers_demo.py --create-sample --method all

# Test specific components
python test_compatibility.py
python test_gui.py
```

## 🐳 Docker Usage

```bash
# Build image
docker build -t tableautopbi .

# Run with volume mounting for file access
docker run --rm -v "${PWD}:/app/data" tableautopbi

# Interactive mode
docker run -it --rm -v "${PWD}:/app/data" tableautopbi bash
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional Tableau feature support
- Enhanced Power BI visual mapping
- Performance optimizations
- More compilation method integrations

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Tabular Editor** team for the excellent free modeling tool
- **pbi-tools** project for Power BI automation capabilities
- Microsoft for Power BI and Tableau for their excellent documentation

## 🔗 Links

- **Tabular Editor**: https://tabulareditor.com/
- **Power BI Desktop**: https://powerbi.microsoft.com/desktop/
- **pbi-tools**: https://pbi-tools.github.io/
