# TableauToPBI

TableauToPBI is a Python tool designed to help users migrate Tableau dashboards and data sources to Microsoft Power BI. It streamlines the conversion process, making it easier to transition between analytics platforms.

## Features

- Convert Tableau workbooks to Power BI format
- Migrate data sources and queries
- Preserve dashboard layouts and visualizations (where possible)
- Command-line interface for batch processing

## Installation

```bash
python -m pip install -r requirements.txt
```
OR
```bash
docker build -t tableautopbi .
```

## Usage

```bash
docker run -rm -v "$(pwd):/app"
```
OR
```bash
python src/app/app.py
```

<img src="config\obj\dashboard_empty.png">
## Requirements

- Python 3.11+
- Tableau workbook files (`.twb` or `.twbx`)
- Power BI Desktop (for opening `.pbix` files)

## Contributing

Contributions are welcome! Please open issues or submit pull requests.
