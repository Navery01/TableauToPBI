# Tableau to Power BI Converter

A comprehensive Python module for converting Tableau workbooks (.twbx) to Power BI templates (.pbit).

## Features

- ✅ **Extract Tableau Workbooks**: Parse .twbx files and extract data sources, worksheets, and metadata
- ✅ **Convert Data Structures**: Transform Tableau data models to Power BI BIM (Business Intelligence Model) format
- ✅ **Generate Power BI Projects**: Create complete .pbixproj structure with all required files
- ✅ **Compile to .pbit**: Use pbi-tools to compile projects into Power BI template files
- ✅ **Modular Design**: Clean, object-oriented architecture for easy extension and maintenance
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Batch Processing**: Support for converting multiple files
- ✅ **Analysis Tools**: Analyze Tableau workbooks without conversion
- Converts to Power BI-compatible BIM model
- Generates a minimal Power BI project structure
- Compiles `.pbixproj` to `.pbit` using `pbi-tools`

---

## 📦 Requirements

### ✅ Python 3.13.5 (Standard Library Only)

- `zipfile`
- `os`
- `xml.etree.ElementTree`
- `json`
- `subprocess`

> No external Python packages required.

### 🛠️ External Dependency

#### [`pbi-tools`](https://pbi.tools/)

Used to compile Power BI project to `.pbit`. Install it globally:

```bash
dotnet tool install --global pbi-tools
