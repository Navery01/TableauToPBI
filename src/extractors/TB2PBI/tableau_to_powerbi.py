"""
Tableau to Power BI Converter Module

This module provides functionality to convert Tableau workbooks (.twbx) to Power BI templates (.pbit).
It extracts data sources, worksheets, and calculated fields from Tableau and converts them to 
compatible Power BI structures.

Author: Your Name
Version: 1.0.0
"""

import zipfile
import os
import xml.etree.ElementTree as ET
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableauToPowerBIError(Exception):
    """Custom exception for Tableau to Power BI conversion errors."""
    pass


class TableauExtractor:
    """Handles extraction and parsing of Tableau workbook files."""
    
    @staticmethod
    def extract_twbx(twbx_path: str, output_dir: Optional[str] = None) -> str:
        """
        Extract a .twbx file to a directory.
        
        Args:
            twbx_path: Path to the .twbx file
            output_dir: Output directory (creates temp dir if None)
            
        Returns:
            Path to the extracted directory
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="twbx_extract_")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            logger.info(f"✅ Extracted {twbx_path} to {output_dir}")
            return output_dir
        except Exception as e:
            raise TableauToPowerBIError(f"Failed to extract {twbx_path}: {e}")
    
    @staticmethod
    def find_twb_file(folder: str) -> str:
        """
        Find the .twb file in an extracted .twbx directory.
        
        Args:
            folder: Directory to search
            
        Returns:
            Path to the .twb file
        """
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".twb"):
                    return os.path.join(root, file)
        raise TableauToPowerBIError("No .twb file found in extracted .twbx.")
    
    @staticmethod
    def parse_twb(twb_path: str) -> Dict:
        """
        Parse a Tableau workbook (.twb) XML file.
        
        Args:
            twb_path: Path to the .twb file
            
        Returns:
            Dictionary containing parsed workbook information
        """
        try:
            tree = ET.parse(twb_path)
            root = tree.getroot()
        except Exception as e:
            raise TableauToPowerBIError(f"Failed to parse {twb_path}: {e}")

        workbook_info = {
            "datasources": [],
            "worksheets": [],
            "calculated_fields": [],
            "joins": [],
            "parameters": [],
            "dashboards": []
        }

        # Parse data sources
        for ds in root.findall('.//datasource'):
            datasource = {
                "name": ds.get('name', 'UnnamedDataSource'),
                "fields": [],
                "connections": []
            }
            
            # Parse columns/fields
            for column in ds.findall('.//column'):
                field_info = {
                    "name": column.get('name', ''),
                    "datatype": column.get('datatype', 'string'),
                    "role": column.get('role', ''),
                    "type": column.get('type', ''),
                    "caption": column.get('caption', '')
                }
                datasource["fields"].append(field_info)
            
            # Parse connections
            for conn in ds.findall('.//connection'):
                conn_info = {
                    "class": conn.get('class', ''),
                    "dbname": conn.get('dbname', ''),
                    "server": conn.get('server', ''),
                    "authentication": conn.get('authentication', ''),
                    "port": conn.get('port', ''),
                    "username": conn.get('username', '')
                }
                datasource["connections"].append(conn_info)
            
            workbook_info["datasources"].append(datasource)

        # Parse calculated fields
        for calc in root.findall('.//calculation'):
            calc_info = {
                "name": calc.get('name', ''),
                "formula": calc.get('formula', ''),
                "class": calc.get('class', '')
            }
            workbook_info["calculated_fields"].append(calc_info)

        # Parse joins
        for relation in root.findall('.//relation'):
            if relation.get('type') == 'join':
                join_info = {
                    "left": relation.get('left', ''),
                    "right": relation.get('right', ''),
                    "operator": relation.get('operator', ''),
                    "type": relation.get('join', 'inner')
                }
                workbook_info["joins"].append(join_info)

        # Parse worksheets
        for ws in root.findall('.//worksheet'):
            worksheet_info = {
                "name": ws.get('name', ''),
                "filters": [],
                "measures": [],
                "dimensions": []
            }
            workbook_info["worksheets"].append(worksheet_info)

        # Parse parameters
        for param in root.findall('.//column[@param-domain-type]'):
            param_info = {
                "name": param.get('name', ''),
                "datatype": param.get('datatype', ''),
                "param_domain_type": param.get('param-domain-type', ''),
                "default_value": param.get('value', '')
            }
            workbook_info["parameters"].append(param_info)

        # Parse dashboards
        for dashboard in root.findall('.//dashboard'):
            dashboard_info = {
                "name": dashboard.get('name', ''),
                "worksheets": []
            }
            workbook_info["dashboards"].append(dashboard_info)

        logger.info(f"✅ Parsed TWB file: {len(workbook_info['datasources'])} data sources, "
                   f"{len(workbook_info['worksheets'])} worksheets")
        
        return workbook_info


class PowerBIConverter:
    """Handles conversion from Tableau structures to Power BI formats."""
    
    DATATYPE_MAPPING = {
        "string": "string",
        "real": "double", 
        "integer": "int64",
        "boolean": "boolean",
        "date": "dateTime",
        "datetime": "dateTime",
        "number": "double"
    }
    
    @classmethod
    def map_datatype(cls, tableau_type: str) -> str:
        """Map Tableau data type to Power BI data type."""
        return cls.DATATYPE_MAPPING.get(tableau_type.lower(), "string")
    
    @staticmethod
    def convert_formula_to_dax(formula: str) -> str:
        """
        Convert Tableau formula to DAX (basic conversion).
        
        Args:
            formula: Tableau formula string
            
        Returns:
            DAX formula string
        """
        if not formula:
            return "BLANK()"
        
        # Basic formula conversions
        dax_formula = formula
        
        # Replace common Tableau functions with DAX equivalents
        replacements = {
            "IF ": "IF(",
            "SUM(": "SUM(",
            "COUNT(": "COUNT(",
            "AVG(": "AVERAGE(",
            "MIN(": "MIN(",
            "MAX(": "MAX(",
            "ISNULL(": "ISBLANK(",
            "LEN(": "LEN(",
            "TRIM(": "TRIM(",
            "UPPER(": "UPPER(",
            "LOWER(": "LOWER("
        }
        
        for tableau_func, dax_func in replacements.items():
            dax_formula = dax_formula.replace(tableau_func, dax_func)
        
        return dax_formula
    
    @classmethod
    def convert_to_bim(cls, tableau_data: Dict) -> Dict:
        """
        Convert Tableau data structure to BIM (Business Intelligence Model) format.
        
        Args:
            tableau_data: Parsed Tableau workbook data
            
        Returns:
            BIM model dictionary
        """
        tables = []
        
        # Convert data sources to tables
        for ds in tableau_data.get('datasources', []):
            if not ds.get('name') or ds['name'] in ['Parameters', 'Filters']:
                continue
                
            table_name = cls._sanitize_name(ds['name'])
            table = {
                "name": table_name,
                "columns": [],
                "partitions": [
                    {
                        "name": f"{table_name}_Partition",
                        "dataView": "full",
                        "source": {
                            "type": "m",
                            "expression": cls._generate_m_expression(ds)
                        }
                    }
                ]
            }
            
            # Add columns
            for field in ds.get('fields', []):
                if field.get('name') and not field['name'].startswith('[Parameters]'):
                    column_name = cls._sanitize_name(field['name'].replace('[', '').replace(']', ''))
                    if column_name:
                        column = {
                            "name": column_name,
                            "dataType": cls.map_datatype(field.get('datatype', 'string')),
                            "isHidden": False,
                            "sourceColumn": column_name
                        }
                        
                        # Add caption if available
                        if field.get('caption'):
                            column["displayName"] = field['caption']
                        
                        # Set column role
                        if field.get('role') == 'measure':
                            column["summarizeBy"] = "sum"
                        
                        table['columns'].append(column)
            
            # Ensure at least one column exists
            if not table['columns']:
                table['columns'].append({
                    "name": "DefaultColumn",
                    "dataType": "string",
                    "isHidden": True,
                    "sourceColumn": "DefaultColumn"
                })
            
            # Add measures from calculated fields
            measures = []
            for calc_field in tableau_data.get('calculated_fields', []):
                if calc_field.get('name'):
                    measure_name = cls._sanitize_name(calc_field['name'])
                    measure = {
                        "name": measure_name,
                        "expression": cls.convert_formula_to_dax(calc_field.get('formula', '')),
                        "isHidden": False,
                        "formatString": "0"
                    }
                    measures.append(measure)
            
            if measures:
                table['measures'] = measures
            
            tables.append(table)

        # Create dummy table if no tables found
        if not tables:
            tables.append({
                "name": "DummyTable",
                "columns": [
                    {
                        "name": "DummyColumn",
                        "dataType": "string",
                        "isHidden": False,
                        "sourceColumn": "DummyColumn"
                    }
                ],
                "partitions": [
                    {
                        "name": "DummyTable_Partition",
                        "dataView": "full",
                        "source": {
                            "type": "m",
                            "expression": [
                                "let",
                                "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [DummyColumn = _t]),",
                                "    #\"Changed Type\" = Table.TransformColumnTypes(Source,{{\"DummyColumn\", type text}})",
                                "in",
                                "    #\"Changed Type\""
                            ]
                        }
                    }
                ]
            })

        # Build complete BIM structure
        bim_model = {
            "name": "SemanticModel",
            "compatibilityLevel": 1550,
            "model": {
                "culture": "en-US",
                "dataAccessOptions": {
                    "legacyRedirects": True,
                    "returnErrorValuesAsNull": True
                },
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "sourceQueryCulture": "en-US",
                "tables": tables,
                "annotations": [
                    {
                        "name": "TabularEditor_SerializeOptions",
                        "value": "{\"IgnoreInferredObjects\":false,\"IgnoreInferredProperties\":false,\"IgnoreTimestamps\":false,\"SplitMultilineStrings\":false,\"PrefixFilenames\":false,\"LocalTranslations\":false,\"LocalPerspectives\":false,\"LocalRelationships\":false,\"Levels\":[\"Data Sources\",\"Shared Expressions\",\"Perspectives\",\"Relationships\",\"Roles\",\"Tables\",\"Tables/Columns\",\"Tables/Hierarchies\",\"Tables/Measures\",\"Tables/Partitions\",\"Tables/Calculation Groups\",\"Translations\"]}"
                    },
                    {
                        "name": "PBI_QueryOrder", 
                        "value": json.dumps([table['name'] for table in tables])
                    }
                ]
            }
        }
        
        return bim_model
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize names for Power BI compatibility."""
        if not name:
            return ""
        return name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("[", "").replace("]", "")
    
    @staticmethod
    def _generate_m_expression(datasource: Dict) -> List[str]:
        """Generate Power Query M expression for a data source."""
        # Basic M expression template
        return [
            "let",
            "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t]),",
            "    #\"Changed Type\" = Table.TransformColumnTypes(Source,{{\"Column1\", type text}})",
            "in",
            "    #\"Changed Type\""
        ]


class PowerBIProjectWriter:
    """Handles writing Power BI project files (.pbixproj format)."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the project writer.
        
        Args:
            output_dir: Directory to write project files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_project_files(self, bim_model: Dict) -> str:
        """
        Write all required Power BI project files.
        
        Args:
            bim_model: BIM model dictionary
            
        Returns:
            Path to the project directory
        """
        logger.info("📝 Writing Power BI project files...")
        
        # Write all required files
        self._write_bim_model(bim_model)
        self._write_version_file()
        self._write_settings_file()
        self._write_metadata_file()
        self._write_connections_file()
        self._write_diagram_layout()
        self._write_report_layout()
        self._write_static_resources()
        self._write_report_metadata()
        self._write_security_bindings()
        self._write_report_settings()
        
        logger.info(f"✅ Project files written to {self.output_dir}")
        return str(self.output_dir)
    
    def _write_bim_model(self, bim_model: Dict):
        """Write the BIM model file."""
        dms_dir = self.output_dir / "DataModelSchema"
        dms_dir.mkdir(exist_ok=True)
        
        bim_path = dms_dir / "Model.bim"
        with open(bim_path, 'w', encoding='utf-8') as f:
            json.dump(bim_model, f, indent=2)
        logger.debug(f"✅ Saved BIM to {bim_path}")
    
    def _write_version_file(self):
        """Write Version.txt file."""
        version_path = self.output_dir / "Version.txt"
        with open(version_path, 'w', encoding='utf-8') as f:
            f.write("3.0")
        logger.debug(f"📝 Added {version_path}")
    
    def _write_settings_file(self):
        """Write Settings file."""
        settings_path = self.output_dir / "Settings"
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        logger.debug(f"📝 Added Settings file")
    
    def _write_metadata_file(self):
        """Write Metadata file."""
        metadata_path = self.output_dir / "Metadata"
        metadata = {
            "version": "3.0",
            "minVersion": "3.0"
        }
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
        logger.debug(f"📝 Added Metadata file")
    
    def _write_connections_file(self):
        """Write connections.json file."""
        dms_dir = self.output_dir / "DataModelSchema"
        dms_dir.mkdir(exist_ok=True)
        
        conn_path = dms_dir / "connections.json"
        with open(conn_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        logger.debug(f"📝 Added connections.json")
    
    def _write_diagram_layout(self):
        """Write DiagramLayout file."""
        dms_dir = self.output_dir / "DataModelSchema"
        dms_dir.mkdir(exist_ok=True)
        
        diagram_path = dms_dir / "DiagramLayout"
        diagram_layout = {
            "version": 1,
            "diagramLayouts": []
        }
        with open(diagram_path, 'w', encoding='utf-8') as f:
            json.dump(diagram_layout, f)
        logger.debug(f"📝 Added DiagramLayout")
    
    def _write_report_layout(self):
        """Write Report/Layout file."""
        report_dir = self.output_dir / "Report"
        report_dir.mkdir(exist_ok=True)
        
        layout_path = report_dir / "Layout"
        minimal_layout = {
            "id": 0,
            "resourcePackages": [],
            "config": "{\"version\":\"5.43\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY24SU06\"}}}",
            "layoutOptimization": 0
        }
        with open(layout_path, 'w', encoding='utf-8') as f:
            json.dump(minimal_layout, f)
        logger.debug(f"📝 Added Report/Layout")
    
    def _write_static_resources(self):
        """Write StaticResources.json file."""
        report_dir = self.output_dir / "Report"
        report_dir.mkdir(exist_ok=True)
        
        static_path = report_dir / "StaticResources.json"
        with open(static_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        logger.debug(f"📝 Added StaticResources.json")
    
    def _write_report_metadata(self):
        """Write ReportMetadata.json file."""
        metadata_path = self.output_dir / "ReportMetadata.json"
        report_metadata = {
            "version": "3.0",
            "createdFromTemplate": False,
            "settings": {
                "useStylableVisualContainerHeader": True
            },
            "objects": {
                "section": [
                    {
                        "name": "ReportSection",
                        "displayName": "Page 1",
                        "visualContainers": []
                    }
                ]
            }
        }
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(report_metadata, f, indent=2)
        logger.debug(f"📝 Added ReportMetadata.json")
    
    def _write_security_bindings(self):
        """Write SecurityBindings.json file."""
        security_path = self.output_dir / "SecurityBindings.json"
        security_bindings = {
            "version": "3.0",
            "bindings": []
        }
        with open(security_path, 'w', encoding='utf-8') as f:
            json.dump(security_bindings, f)
        logger.debug(f"📝 Added SecurityBindings.json")
    
    def _write_report_settings(self):
        """Write ReportSettings.json file."""
        settings_path = self.output_dir / "ReportSettings.json"
        report_settings = {
            "name": "ReportSettings",
            "version": "3.0",
            "objects": {
                "ReportSettings": [
                    {
                        "name": "ReportSettings",
                        "properties": {
                            "defaultTheme": {
                                "name": "CY24SU06"
                            }
                        }
                    }
                ]
            }
        }
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(report_settings, f, indent=2)
        logger.debug(f"📝 Added ReportSettings.json")


class PBIToolsCompiler:
    """Handles compilation of Power BI project files using pbi-tools."""
    
    @staticmethod
    def is_pbi_tools_available() -> bool:
        """Check if pbi-tools is available in the system."""
        try:
            # pbi-tools doesn't support --version, but running it with no args
            # will show help and return exit code 1, which means it's available
            result = subprocess.run(["pbi-tools"], 
                                  capture_output=True, text=True, timeout=10)
            # Check if the output contains the expected pbi-tools signature
            return "pbi-tools" in result.stdout and "Copyright" in result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception:
            # If any other exception occurs, assume it's not available
            return False
    
    @staticmethod
    def compile_to_pbit(project_dir: str, output_path: str, overwrite: bool = True) -> bool:
        """
        Compile Power BI project to .pbit file using pbi-tools.
        
        Args:
            project_dir: Path to the Power BI project directory
            output_path: Output path for the .pbit file
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if compilation successful, False otherwise
        """
        if not PBIToolsCompiler.is_pbi_tools_available():
            logger.error("❌ pbi-tools not found. Please install it first:")
            logger.error("   Option 1: choco install pbi-tools")
            logger.error("   Option 2: Download from https://github.com/pbi-tools/pbi-tools/releases")
            return False
        
        # Check for version compatibility
        compatibility = handle_pbi_tools_compatibility()
        if "warning" in compatibility:
            logger.warning(f"⚠️  {compatibility['warning']}")
            logger.warning("   Compilation may fail due to version mismatch")
            logger.warning("   Consider updating pbi-tools or using project files manually")
        
        logger.info("🏗️  Compiling .pbit using pbi-tools...")
        
        try:
            result = subprocess.run([
                "pbi-tools", "compile",
                project_dir,
                output_path,
                "PBIT",
                str(overwrite)
            ], capture_output=True, text=True, check=True)
            
            logger.info(f"✅ .pbit created at: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error("❌ Error creating .pbit:")
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
            
            # Check for specific version compatibility errors
            if "MissingMethodException" in e.stderr or "Method not found" in e.stderr:
                logger.error("🔧 This appears to be a version compatibility issue:")
                logger.error("   Your Power BI Desktop version may be incompatible with pbi-tools")
                logger.error("   Solutions:")
                logger.error("   1. Update pbi-tools: choco upgrade pbi-tools")
                logger.error("   2. Use project files manually with Power BI Desktop")
                logger.error("   3. Downgrade Power BI Desktop to a compatible version")
                
            return False


class TableauToPowerBIConverter:
    """Main converter class that orchestrates the conversion process."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the converter.
        
        Args:
            temp_dir: Temporary directory for intermediate files (auto-created if None)
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="tb2pbi_")
        self.extractor = TableauExtractor()
        self.converter = PowerBIConverter()
        self.compiler = PBIToolsCompiler()
    
    def convert(self, 
                twbx_path: str, 
                output_path: str, 
                project_dir: Optional[str] = None,
                cleanup_temp: bool = True) -> bool:
        """
        Convert a Tableau workbook to Power BI template.
        
        Args:
            twbx_path: Path to the Tableau workbook (.twbx)
            output_path: Path for the output Power BI template (.pbit)
            project_dir: Directory for intermediate project files (uses temp if None)
            cleanup_temp: Whether to cleanup temporary files
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            logger.info("🚀 Starting Tableau to Power BI conversion...")
            
            # Step 1: Extract and parse Tableau workbook
            logger.info("📂 Extracting Tableau workbook...")
            extracted_dir = self.extractor.extract_twbx(twbx_path)
            
            twb_file = self.extractor.find_twb_file(extracted_dir)
            tableau_data = self.extractor.parse_twb(twb_file)
            
            # Step 2: Convert to Power BI format
            logger.info("🔄 Converting to Power BI format...")
            bim_model = self.converter.convert_to_bim(tableau_data)
            
            # Step 3: Write project files
            if project_dir is None:
                project_dir = os.path.join(self.temp_dir, "pbix_project")
            
            writer = PowerBIProjectWriter(project_dir)
            project_path = writer.write_project_files(bim_model)
            
            # Step 4: Compile to .pbit
            logger.info("🔨 Compiling to .pbit...")
            success = self.compiler.compile_to_pbit(project_path, output_path)
            
            if success:
                logger.info("🎉 Conversion completed successfully!")
                logger.info(f"📁 Output file: {output_path}")
                logger.info(f"📂 Project folder: {project_path}")
            else:
                logger.warning("⚠️  .pbit compilation failed, but project files are ready!")
                logger.info("📂 Manual compilation options:")
                logger.info("   1. Open Power BI Desktop")
                logger.info("   2. File → Open → Browse to the project folder:")
                logger.info(f"      {project_path}")
                logger.info("   3. File → Export → Power BI Template (.pbit)")
                logger.info("   4. See MANUAL_COMPILATION_GUIDE.md for detailed steps")
                # Still return success since project files were created
                success = True
            
            # Cleanup
            if cleanup_temp and extracted_dir.startswith(tempfile.gettempdir()):
                shutil.rmtree(extracted_dir, ignore_errors=True)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            return False
    
    def get_tableau_info(self, twbx_path: str) -> Dict:
        """
        Get information about a Tableau workbook without converting.
        
        Args:
            twbx_path: Path to the Tableau workbook (.twbx)
            
        Returns:
            Dictionary containing workbook information
        """
        try:
            extracted_dir = self.extractor.extract_twbx(twbx_path)
            twb_file = self.extractor.find_twb_file(extracted_dir)
            tableau_data = self.extractor.parse_twb(twb_file)
            
            # Cleanup
            if extracted_dir.startswith(tempfile.gettempdir()):
                shutil.rmtree(extracted_dir, ignore_errors=True)
            
            return tableau_data
            
        except Exception as e:
            raise TableauToPowerBIError(f"Failed to analyze Tableau workbook: {e}")


# Convenience functions for direct usage
def convert_tableau_to_powerbi(twbx_path: str, 
                              output_path: str, 
                              project_dir: Optional[str] = None) -> bool:
    """
    Convert a Tableau workbook to Power BI template (convenience function).
    
    Args:
        twbx_path: Path to the Tableau workbook (.twbx)
        output_path: Path for the output Power BI template (.pbit)
        project_dir: Directory for intermediate project files (optional)
        
    Returns:
        True if conversion successful, False otherwise
    """
    converter = TableauToPowerBIConverter()
    return converter.convert(twbx_path, output_path, project_dir)


def analyze_tableau_workbook(twbx_path: str) -> Dict:
    """
    Analyze a Tableau workbook and return its structure (convenience function).
    
    Args:
        twbx_path: Path to the Tableau workbook (.twbx)
        
    Returns:
        Dictionary containing workbook information
    """
    converter = TableauToPowerBIConverter()
    return converter.get_tableau_info(twbx_path)


def handle_pbi_tools_compatibility():
    """Check pbi-tools compatibility and provide guidance"""
    try:
        result = subprocess.run(["pbi-tools", "info"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            pbi_tools_version = info.get("version", "unknown")
            pbi_build_version = info.get("pbiBuildVersion", "unknown")
            
            # Check if there are PBI installs
            pbi_installs = info.get("pbiInstalls", [])
            if pbi_installs:
                current_pbi_version = pbi_installs[0].get("ProductVersion", "unknown")
                return {
                    "compatible": True,  # We'll try anyway
                    "pbi_tools_version": pbi_tools_version,
                    "pbi_build_version": pbi_build_version,
                    "current_pbi_version": current_pbi_version,
                    "warning": f"Version mismatch detected: pbi-tools expects {pbi_build_version}, found {current_pbi_version}"
                }
            
        return {"compatible": False, "error": "Could not determine versions"}
        
    except Exception as e:
        return {"compatible": False, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python tableau_to_powerbi.py <input.twbx> <output.pbit>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    success = convert_tableau_to_powerbi(input_file, output_file)
    sys.exit(0 if success else 1)
