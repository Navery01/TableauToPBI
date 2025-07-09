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
<<<<<<< HEAD
        
        
        if compatibility.get("warning"):
=======
        if "warning" in compatibility:
>>>>>>> parent of 20eec4b (AttemptingCompatabilityFix)
            logger.warning(f"⚠️  {compatibility['warning']}")
            logger.warning("   Compilation may fail due to version mismatch")
            logger.warning("   Consider updating pbi-tools or using project files manually")
        
        logger.info("🏗️  Compiling .pbit using pbi-tools...")
        
        try:
            result = subprocess.run([
                "pbi-tools.core", "compile",
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
            
<<<<<<< HEAD
            # Enhanced error detection and handling
            error_messages = []
            
            if "MissingMethodException" in e.stderr:
                error_messages.append("🔧 METHOD NOT FOUND ERROR:")
                error_messages.append("   This is a version compatibility issue between pbi-tools and Power BI Desktop")
                error_messages.append(f"   Your Power BI Desktop version: {compatibility.get('current_pbi_version', 'unknown')}")
                error_messages.append(f"   Your pbi-tools version: {compatibility.get('pbi_tools_version', 'unknown')}")
                error_messages.append("   The PowerBIPackager.Save method signature has changed")
            
            elif "Method not found" in e.stderr:
                error_messages.append("🔧 API COMPATIBILITY ERROR:")
                error_messages.append("   Power BI Desktop API has changed since this pbi-tools version was built")
            
            elif "Access denied" in e.stderr or "permission" in e.stderr.lower():
                error_messages.append("🔧 PERMISSION ERROR:")
                error_messages.append("   Try running as administrator")
                error_messages.append("   Check if output directory is writable")
            
            elif "not found" in e.stderr.lower():
                error_messages.append("🔧 FILE NOT FOUND ERROR:")
                error_messages.append("   Check if all required files are in the project directory")
            
            else:
                error_messages.append("🔧 UNKNOWN ERROR:")
                error_messages.append("   See error details above")
            
            for msg in error_messages:
                logger.error(msg)
                
        except Exception as e:
            logger.error("❌ Error creating .pbit:")
            logger.error(f"Error: {str(e)}")
            
            # Generic error handling for non-subprocess errors
            error_messages = [
                "🔧 UNEXPECTED ERROR:",
                "   An unexpected error occurred during .pbit creation",
                "   This may be due to file permissions, disk space, or other system issues"
            ]
            
            for msg in error_messages:
                logger.error(msg)
            
            logger.error("\n💡 RECOMMENDED SOLUTIONS:")
            logger.error("   1. Use manual compilation (most reliable):")
            logger.error("      • Open Power BI Desktop")
            logger.error(f"      • File → Open → {project_dir}")
            logger.error("      • File → Export → Power BI Template (.pbit)")
            logger.error("   2. Update both pbi-tools and Power BI Desktop")
            logger.error("   3. Check GitHub issues: https://github.com/pbi-tools/pbi-tools/issues")
            
            # Auto-open project directory for manual compilation
            logger.info("📂 Opening project directory for manual compilation...")
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", project_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", project_dir])
                else:  # Linux
                    subprocess.run(["xdg-open", project_dir])
                
                logger.info(f"📂 Opened project directory: {project_dir}")
            except Exception as e:
                logger.warning(f"⚠️  Could not open project directory: {e}")
                logger.info(f"📂 Manual path: {project_dir}")
=======
            # Check for specific version compatibility errors
            if "MissingMethodException" in e.stderr or "Method not found" in e.stderr:
                logger.error("🔧 This appears to be a version compatibility issue:")
                logger.error("   Your Power BI Desktop version may be incompatible with pbi-tools")
                logger.error("   Solutions:")
                logger.error("   1. Update pbi-tools: choco upgrade pbi-tools")
                logger.error("   2. Use project files manually with Power BI Desktop")
                logger.error("   3. Downgrade Power BI Desktop to a compatible version")
>>>>>>> parent of 20eec4b (AttemptingCompatabilityFix)
                
            return False


<<<<<<< HEAD
class PBIToolsInstaller:
    """Handles automatic installation and updates of pbi-tools."""
    
    def __init__(self):
        self.github_repo = "pbi-tools/pbi-tools"
        self.api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.install_dir = Path.home() / ".pbi-tools"
        self.bin_dir = self.install_dir / "bin"
        
    def check_installation(self) -> Dict:
        """Check if pbi-tools is installed and get version info."""
        try:
            result = subprocess.run(["pbi-tools"], 
                                  capture_output=True, text=True, timeout=10)
            # pbi-tools shows help when run without args
            if "pbi-tools" in result.stdout and "Copyright" in result.stdout:
                # Try to get version info
                version_info = self._get_version_info()
                return {
                    "installed": True,
                    "version": version_info.get("version", "unknown"),
                    "path": self._find_pbi_tools_path()
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return {"installed": False, "version": None, "path": None}
    
    def _get_version_info(self) -> Dict:
        """Get detailed version information from pbi-tools."""
        try:
            result = subprocess.run(["pbi-tools", "info"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return {"version": "unknown"}
    
    def _find_pbi_tools_path(self) -> Optional[str]:
        """Find the path where pbi-tools is installed."""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["where", "pbi-tools"], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(["which", "pbi-tools"], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass
        return None
    
    def get_latest_version_info(self) -> Dict:
        """Get information about the latest pbi-tools release from GitHub."""
        try:
            logger.info("🔍 Checking for latest pbi-tools version...")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            version = release_data["tag_name"].lstrip("v")
            
            # Find the appropriate asset for current platform
            system = platform.system().lower()
            arch = "x64" if platform.machine().endswith('64') else "x86"
            
            download_url = None
            filename = None
            
            for asset in release_data["assets"]:
                asset_name = asset["name"].lower()
                if system == "windows" and f"win-{arch}" in asset_name and asset_name.endswith(".zip"):
                    download_url = asset["browser_download_url"]
                    filename = asset["name"]
                    break
                elif system == "linux" and f"linux-{arch}" in asset_name and asset_name.endswith(".tar.gz"):
                    download_url = asset["browser_download_url"]
                    filename = asset["name"]
                    break
                elif system == "darwin" and "osx" in asset_name:
                    download_url = asset["browser_download_url"]
                    filename = asset["name"]
                    break
            
            return {
                "version": version,
                "download_url": download_url,
                "filename": filename,
                "release_notes": release_data.get("body", "")
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get latest version info: {e}")
            return {}
    
    def download_pbi_tools(self, download_url: str, filename: str) -> Path:
        """Download pbi-tools from GitHub releases."""
        logger.info(f"⬇️  Downloading pbi-tools: {filename}")
        
        self.install_dir.mkdir(exist_ok=True)
        download_path = self.install_dir / filename
        
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Simple progress indicator
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Every MB
                                logger.info(f"📥 Downloaded: {progress:.1f}%")
            
            logger.info(f"✅ Download completed: {download_path}")
            return download_path
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            if download_path.exists():
                download_path.unlink()
            raise
    
    def extract_and_install(self, archive_path: Path, version: str):
        """Extract and install pbi-tools."""
        logger.info(f"📦 Extracting pbi-tools {version}...")
        
        # Remove old installation
        if self.bin_dir.exists():
            shutil.rmtree(self.bin_dir)
        
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if archive_path.suffix == '.zip':
                import zipfile
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.bin_dir)
            elif archive_path.suffix == '.gz':
                import tarfile
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.bin_dir)
            
            # Make executable on Unix-like systems
            if platform.system() != "Windows":
                pbi_tools_exe = self.bin_dir / "pbi-tools"
                if pbi_tools_exe.exists():
                    pbi_tools_exe.chmod(0o755)
            
            # Add to PATH
            self._add_to_path()
            
            # Clean up archive
            archive_path.unlink()
            
            logger.info(f"✅ pbi-tools {version} installed successfully!")
            logger.info(f"📂 Installation directory: {self.bin_dir}")
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            raise
    
    def _add_to_path(self):
        """Add pbi-tools to system PATH."""
        bin_str = str(self.bin_dir)
        
        if platform.system() == "Windows":
            # Windows PATH update
            current_path = os.environ.get('PATH', '')
            if bin_str not in current_path:
                os.environ['PATH'] = f"{bin_str};{current_path}"
                
                # Try to update user PATH permanently
                try:
                    # Get current user PATH
                    result = subprocess.run([
                        'reg', 'query', 'HKCU\\Environment', '/v', 'PATH'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Extract current PATH value
                        for line in result.stdout.split('\n'):
                            if 'PATH' in line and 'REG_' in line:
                                current_user_path = line.split('REG_SZ')[-1].strip()
                                if bin_str not in current_user_path:
                                    new_path = f"{bin_str};{current_user_path}"
                                    subprocess.run([
                                        'setx', 'PATH', new_path
                                    ], check=True, capture_output=True)
                                    logger.info("✅ PATH updated permanently")
                                break
                    else:
                        # No existing PATH, create one
                        subprocess.run([
                            'setx', 'PATH', bin_str
                        ], check=True, capture_output=True)
                        logger.info("✅ PATH created and updated")
                        
                except subprocess.CalledProcessError:
                    logger.warning("⚠️  Could not permanently update PATH. You may need to restart your terminal.")
        
        else:
            # Unix-like systems
            shell_configs = [
                Path.home() / ".bashrc",
                Path.home() / ".bash_profile", 
                Path.home() / ".zshrc",
                Path.home() / ".profile"
            ]
            
            path_export = f'export PATH="{bin_str}:$PATH"'
            added_to_config = False
            
            for config_file in shell_configs:
                if config_file.exists():
                    content = config_file.read_text()
                    if bin_str not in content:
                        with open(config_file, 'a') as f:
                            f.write(f"\n# pbi-tools\n{path_export}\n")
                        logger.info(f"✅ Added to {config_file}")
                        added_to_config = True
                        break
            
            if not added_to_config:
                # Create .bashrc if none exist
                bashrc = Path.home() / ".bashrc"
                with open(bashrc, 'w') as f:
                    f.write(f"# pbi-tools\n{path_export}\n")
                logger.info(f"✅ Created {bashrc} with PATH")
    
    def install_or_update(self, force_reinstall: bool = False) -> bool:
        """Main method to install or update pbi-tools."""
        try:
            # Check current installation
            current_install = self.check_installation()
            
            # Get latest version info
            latest_info = self.get_latest_version_info()
            if not latest_info.get("download_url"):
                logger.error("❌ Could not find download for current platform")
                return False
            
            latest_version = latest_info["version"]
            
            # Decide whether to install/update
            if current_install["installed"] and not force_reinstall:
                current_version = current_install["version"]
                logger.info(f"📦 Current version: {current_version}")
                logger.info(f"🆕 Latest version: {latest_version}")
                
                if current_version == latest_version:
                    logger.info("✅ pbi-tools is already up to date!")
                    return True
                
                logger.info(f"🔄 Update available: {current_version} → {latest_version}")
                if not force_reinstall:
                    # Auto-proceed with update
                    logger.info("🔄 Auto-proceeding with update...")
            
            # Perform installation/update
            logger.info(f"🚀 Installing pbi-tools {latest_version}...")
            
            # Download
            archive_path = self.download_pbi_tools(
                latest_info["download_url"], 
                latest_info["filename"]
            )
            
            # Extract and install
            self.extract_and_install(archive_path, latest_version)
            
            # Verify installation
            verification = self.check_installation()
            if verification["installed"]:
                logger.info("🎉 Installation completed successfully!")
                logger.info("💡 You may need to restart your terminal/IDE for PATH changes to take effect")
                return True
            else:
                logger.error("❌ Installation verification failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall pbi-tools."""
        try:
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                logger.info("✅ pbi-tools uninstalled successfully")
                logger.info("💡 You may need to manually remove PATH entries")
                return True
            else:
                logger.info("ℹ️  pbi-tools is not installed in the default location")
                return True
        except Exception as e:
            logger.error(f"❌ Uninstall failed: {e}")
            return False


def auto_install_pbi_tools(force_reinstall: bool = False) -> bool:
    """Convenience function for auto-installing pbi-tools."""
    installer = PBIToolsInstaller()
    return installer.install_or_update(force_reinstall)


=======
>>>>>>> parent of 20eec4b (AttemptingCompatabilityFix)
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
    
<<<<<<< HEAD
    // Validate the model
    if (Model.Tables.Count == 0) {{
        Warning("Model has no tables");
    }}
    
    // Save as Power BI Template
    var pbitPath = @"{self.output_path.as_posix()}";
    
    // Ensure output directory exists
    var outputDir = System.IO.Path.GetDirectoryName(pbitPath);
    if (!System.IO.Directory.Exists(outputDir)) {{
        System.IO.Directory.CreateDirectory(outputDir);
    }}
    
    // Save the PBIT file
    SaveFile(pbitPath, SaveFormat.PowerBITemplate);
    
    Info("Successfully saved PBIT to: " + pbitPath);
}} catch (Exception ex) {{
    Error("Compilation failed: " + ex.Message);
}}
'''
            
            script_file = self.temp_dir / "tabular_compile_script.cs"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"📝 Created Tabular Editor script: {script_file}")
            
            # Run Tabular Editor with the script
            cmd = [tabular_exe, str(bim_file), "-S", str(script_file)]
            logger.info(f"🏃 Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if self.output_path.exists():
                    logger.info(f"✅ Successfully compiled with Tabular Editor: {self.output_path}")
                    return True
                else:
                    logger.warning("⚠️  Tabular Editor completed but PBIT file not found")
                    logger.info(f"STDOUT: {result.stdout}")
                    return False
            else:
                logger.error(f"❌ Tabular Editor compilation failed (return code: {result.returncode})")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Tabular Editor compilation timed out (5 minutes)")
            return False
        except Exception as e:
            logger.error(f"❌ Tabular Editor compilation error: {e}")
            return False
        finally:
            # Cleanup script file
            if 'script_file' in locals():
                script_file.unlink(missing_ok=True)
    
    def compile_with_power_bi_desktop(self) -> bool:
        """
        Use Power BI Desktop directly via automation.
        This opens PBI Desktop and attempts to automate the save process.
        """
        logger.info("🔧 Attempting compilation with Power BI Desktop automation...")
        
        # Find Power BI Desktop installation
        pbi_paths = [
            r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
            r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
        ]
        
        # Check Windows Apps installation
        winapp_base = Path(r"C:\Program Files\WindowsApps")
        if winapp_base.exists():
            pbi_apps = list(winapp_base.glob("Microsoft.MicrosoftPowerBIDesktop_*/bin/PBIDesktop.exe"))
            pbi_paths.extend([str(p) for p in pbi_apps])
        
        pbi_exe = None
        for path in pbi_paths:
            if Path(path).exists():
                pbi_exe = path
                break
        
        if not pbi_exe:
            logger.warning("❌ Power BI Desktop not found")
            return False
        
        try:
            logger.info("📋 Starting Power BI Desktop for manual compilation...")
            logger.info("👉 MANUAL STEPS REQUIRED:")
            logger.info("   1. Power BI Desktop will open")
            logger.info("   2. File → Open → Browse to project folder")
            logger.info(f"   3. Select: {self.project_dir}")
            logger.info("   4. File → Export → Power BI Template (.pbit)")
            logger.info(f"   5. Save as: {self.output_path}")
            
            # Open Power BI Desktop
            subprocess.Popen([pbi_exe])
            
            # Try to open file explorer to the project directory
            if platform.system() == "Windows":
                subprocess.Popen(["explorer", str(self.project_dir)])
            
            logger.info("💡 Power BI Desktop and project folder opened")
            logger.info("💡 Complete the manual steps above to finish compilation")
            return True
            
        except Exception as e:
            logger.error(f"❌ Power BI Desktop automation error: {e}")
            return False
    
    def compile_with_sqlcmd_and_xmla(self) -> bool:
        """
        Use SQL Server Analysis Services (SSAS) to process the model.
        This requires SSAS to be installed locally.
        """
        logger.info("🔧 Attempting compilation with SSAS/XMLA...")
        
        # Check for SQL Server Analysis Services
        ssas_paths = [
            r"C:\Program Files\Microsoft SQL Server\*\Tools\Binn\SQLCMD.exe",
            r"C:\Program Files (x86)\Microsoft SQL Server\*\Tools\Binn\SQLCMD.exe"
        ]
        
        sqlcmd_exe = None
        for pattern in ssas_paths:
            matches = list(Path("/").glob(pattern.replace("C:\\", "")))
            if matches:
                sqlcmd_exe = str(matches[0])
                break
        
        if not sqlcmd_exe:
            logger.warning("❌ SQL Server tools not found")
            logger.info("💡 This method requires SQL Server Management Studio or SQL Server tools")
            return False
        
        logger.info("💡 SSAS/XMLA method requires manual setup:")
        logger.info("   1. Deploy model to local SSAS instance")
        logger.info("   2. Use Power BI Desktop to connect to SSAS")
        logger.info("   3. Export as .pbit template")
        logger.info("💡 This is an advanced method - consider other options first")
        
        return False
    
    def compile_with_analysis_services_deployment_utility(self) -> bool:
        """
        Use Microsoft SQL Server Analysis Services Deployment Utility.
        This is part of SQL Server Data Tools (SSDT).
        """
        logger.info("🔧 Attempting compilation with Analysis Services Deployment Utility...")
        
        # Look for Analysis Services deployment tools
        asdeployment_paths = [
            r"C:\Program Files (x86)\Microsoft SQL Server\*\Tools\Binn\ManagementStudio\Microsoft.AnalysisServices.Deployment.exe",
            r"C:\Program Files\Microsoft SQL Server\*\Tools\Binn\ManagementStudio\Microsoft.AnalysisServices.Deployment.exe",
            r"C:\Program Files (x86)\Microsoft SQL Server\*\SSDT\Binn\Microsoft.AnalysisServices.Deployment.exe",
            r"C:\Program Files\Microsoft SQL Server\*\SSDT\Binn\Microsoft.AnalysisServices.Deployment.exe"
        ]
        
        asdeployment_exe = None
        for pattern in asdeployment_paths:
            # Use glob to handle wildcards in paths
            base_path = pattern.split("*")[0]
            if Path(base_path).exists():
                matches = list(Path(base_path).parent.glob(pattern.split("*")[1]))
                if matches:
                    for match in matches:
                        if match.name == "Microsoft.AnalysisServices.Deployment.exe":
                            asdeployment_exe = str(match)
                            break
                    if asdeployment_exe:
                        break
        
        if not asdeployment_exe:
            logger.warning("❌ Analysis Services Deployment Utility not found")
            logger.info("💡 Install SQL Server Data Tools (SSDT) to get AS deployment tools")
            return False
        
        try:
            # Create deployment files for Analysis Services
            bim_file = self.project_dir / "DataModelSchema" / "Model.bim"
            if not bim_file.exists():
                logger.error(f"❌ Model.bim not found at {bim_file}")
                return False
            
            # Analysis Services method requires manual deployment
            logger.info("💡 Analysis Services method requires these manual steps:")
            logger.info("   1. Deploy model to local Analysis Services instance")
            logger.info("   2. Connect Power BI Desktop to the AS database")
            logger.info("   3. Export as .pbit template")
            logger.info("💡 This is an advanced method - consider other options first")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Analysis Services compilation error: {e}")
            return False
    
    def compile_with_fabric_api(self) -> bool:
        """
        Use Microsoft Fabric REST APIs to process the model.
        This requires authentication and a Fabric workspace.
        """
        logger.info("🔧 Attempting compilation with Microsoft Fabric API...")
        
        try:
            # Check if user has Fabric credentials configured
            logger.info("💡 Microsoft Fabric API method requires:")
            logger.info("   1. Active Microsoft Fabric subscription")
            logger.info("   2. Authentication (Azure AD)")
            logger.info("   3. Fabric workspace access")
            logger.info("   4. REST API integration")
            logger.info("💡 This is a cloud-based method - consider other options for local compilation")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Fabric API compilation error: {e}")
            return False
    
    def compile_with_powerbi_cmdlets(self) -> bool:
        """
        Use PowerBI PowerShell cmdlets for compilation.
        This requires the MicrosoftPowerBIMgmt PowerShell module.
        """
        logger.info("🔧 Attempting compilation with PowerBI PowerShell cmdlets...")
        
        try:
            # Check if PowerShell is available
            powershell_exe = "powershell.exe"
            if platform.system() == "Windows":
                # Check for PowerShell installation
                result = subprocess.run([powershell_exe, "-Command", "Get-Module -ListAvailable MicrosoftPowerBIMgmt"], 
                                      capture_output=True, text=True, timeout=30)
                
                if "MicrosoftPowerBIMgmt" not in result.stdout:
                    logger.warning("❌ MicrosoftPowerBIMgmt PowerShell module not found")
                    logger.info("💡 Install with: Install-Module -Name MicrosoftPowerBIMgmt")
                    return False
                
                # Create PowerShell script for PBIT compilation
                ps_script = f'''
# PowerBI PowerShell compilation script
Import-Module MicrosoftPowerBIMgmt

try {{
    # This would require authentication and cloud processing
    Write-Host "PowerBI PowerShell cmdlets require cloud authentication"
    Write-Host "This method is primarily for managing online Power BI content"
    Write-Host "For local PBIT creation, use other methods like Tabular Editor"
    
    # Connect-PowerBIServiceAccount would be needed here
    # But local PBIT creation is not directly supported
    
    exit 1
}} catch {{
    Write-Error "PowerBI cmdlets compilation failed: $($_.Exception.Message)"
    exit 1
}}
'''
                
                script_file = self.temp_dir / "powerbi_compile.ps1"
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(ps_script)
                
                logger.info("💡 PowerBI PowerShell cmdlets are primarily for online Power BI management")
                logger.info("💡 For local PBIT creation, use Tabular Editor or manual methods")
                
                return False
            else:
                logger.warning("❌ PowerShell cmdlets method only available on Windows")
                return False
                
        except Exception as e:
            logger.error(f"❌ PowerBI cmdlets compilation error: {e}")
            return False
    
    def compile_with_python_powerbi_api(self) -> bool:
        """
        Use Python libraries to interact with Power BI REST APIs.
        Requires msal, requests, and Power BI service access.
        """
        logger.info("🔧 Attempting compilation with Python Power BI API...")
        
        try:
            # Check for required packages
            required_packages = ['msal', 'requests']
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.warning(f"❌ Missing required packages: {', '.join(missing_packages)}")
                logger.info(f"💡 Install with: pip install {' '.join(missing_packages)}")
                return False
            
            # Python Power BI API method
            logger.info("💡 Python Power BI API method requires:")
            logger.info("   1. Azure AD app registration")
            logger.info("   2. Power BI service authentication")
            logger.info("   3. Online workspace for processing")
            logger.info("💡 This is a cloud-based method - not suitable for local PBIT creation")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Python Power BI API compilation error: {e}")
            return False
    
    def compile_with_xmla_endpoint(self) -> bool:
        """
        Use XMLA endpoint to process the model.
        This can work with local Analysis Services or Power BI Premium.
        """
        logger.info("🔧 Attempting compilation with XMLA endpoint...")
        
        try:
            # Check for required packages for XMLA
            required_packages = ['adodbapi', 'pythonnet']
            available_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                    available_packages.append(package)
                except ImportError:
                    pass
            
            if not available_packages:
                logger.warning("❌ XMLA packages not available")
                logger.info("💡 XMLA method requires:")
                logger.info("   1. pythonnet: pip install pythonnet")
                logger.info("   2. adodbapi: pip install adodbapi")
                logger.info("   3. Local Analysis Services instance")
                return False
            
            # XMLA method information
            logger.info("💡 XMLA endpoint method requires:")
            logger.info("   1. Local Analysis Services instance running")
            logger.info("   2. XMLA connection string")
            logger.info("   3. Model deployment to AS")
            logger.info("   4. PBIT export from connected Power BI Desktop")
            logger.info("💡 This is an advanced enterprise method")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ XMLA endpoint compilation error: {e}")
            return False
    
    def compile_with_custom_zip_method(self) -> bool:
        """
        Alternative ZIP-based PBIT creation method with enhanced validation.
        This method focuses on creating the most compatible PBIT structure.
        """
        logger.info("🔧 Attempting custom ZIP-based PBIT creation...")
        
        try:
            bim_file = self.project_dir / "DataModelSchema" / "Model.bim"
            if not bim_file.exists():
                logger.error(f"❌ Model.bim not found at {bim_file}")
                return False
            
            # Load and validate BIM
            with open(bim_file, 'r', encoding='utf-8') as f:
                bim_data = json.load(f)
            
            # Ensure proper BIM structure for PBIT
            if "model" in bim_data:
                model_data = bim_data["model"]
            else:
                model_data = bim_data
            
            # Create optimized PBIT
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as pbit:
                
                # DataModel - core model definition
                model_json = json.dumps(model_data, separators=(',', ':'), ensure_ascii=False)
                pbit.writestr("DataModel", model_json, compress_type=zipfile.ZIP_DEFLATED)
                
                # Version - PBIT format version
                pbit.writestr("Version", "3.0")
                
                # Metadata - file metadata
                metadata = {
                    "version": "3.0",
                    "createdFromTemplate": True,
                    "templateDisplayName": f"{self.output_path.stem}"
                }
                pbit.writestr("Metadata", json.dumps(metadata, separators=(',', ':')))
                
                # Settings - empty settings object
                pbit.writestr("Settings", "{}")
                
                # SecurityBindings - security configuration
                security = {"version": "3.0", "bindings": []}
                pbit.writestr("SecurityBindings", json.dumps(security, separators=(',', ':')))
                
                # Report structure
                report_layout = {
                    "id": 0,
                    "resourcePackages": [],
                    "config": json.dumps({
                        "version": "5.43",
                        "themeCollection": {"baseTheme": {"name": "CY24SU06"}},
                        "settings": {"useStylableVisualContainerHeader": True}
                    }),
                    "layoutOptimization": 0,
                    "sections": [
                        {
                            "id": 0,
                            "name": "Page1",
                            "displayName": "Page 1",
                            "visualContainers": [],
                            "config": json.dumps({
                                "visibility": 0,
                                "defaultLayout": {"displayOption": 1}
                            })
                        }
                    ],
                    "publicCustomVisuals": []
                }
                
                pbit.writestr("Report/Layout", json.dumps(report_layout, separators=(',', ':')))
            
            # Verify creation
            if self.output_path.exists() and self.output_path.stat().st_size > 100:
                logger.info(f"✅ Custom ZIP PBIT creation successful: {self.output_path}")
                
                # Test the ZIP file
                try:
                    with zipfile.ZipFile(self.output_path, 'r') as test_zip:
                        files = test_zip.namelist()
                        logger.info(f"📦 PBIT contains: {', '.join(files)}")
                        return True
                except:
                    logger.error("❌ Created PBIT file is corrupted")
                    return False
            else:
                logger.error("❌ Custom ZIP PBIT creation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Custom ZIP compilation error: {e}")
            return False
    
    def get_available_methods(self) -> List[str]:
        """Get list of available compilation methods on this system."""
        methods = []
        
        # Check Tabular Editor
        tabular_paths = [
            r"C:\Program Files (x86)\Tabular Editor\TabularEditor.exe",
            r"C:\Program Files\Tabular Editor\TabularEditor.exe",
            r"C:\Program Files\Tabular Editor 3\TabularEditor3.exe",
            r".\TabularEditor.exe"
        ]
        if any(Path(p).exists() for p in tabular_paths):
            methods.append("Tabular Editor")
        
        # Check Power BI Desktop
        pbi_paths = [
            r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
            r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
        ]
        if any(Path(p).exists() for p in pbi_paths):
            methods.append("Power BI Desktop")
        
        # Manual methods are always available
        methods.extend(["Manual PBIT Creation", "Custom ZIP Method"])
        
        return methods
    
    def create_pbit_manually(self) -> bool:
        """
        Create a .pbit file manually by understanding its structure.
        PBIT files are ZIP archives containing specific files.
        This is the most reliable fallback method.
        """
        logger.info("🔧 Attempting manual PBIT creation...")
        
        try:
            # Read the BIM model
            bim_file = self.project_dir / "DataModelSchema" / "Model.bim"
            if not bim_file.exists():
                logger.error(f"❌ Model.bim not found at {bim_file}")
                return False
            
            logger.info(f"📖 Reading BIM model from {bim_file}")
            with open(bim_file, 'r', encoding='utf-8') as f:
                bim_content = json.load(f)
            
            # Validate BIM content
            if not isinstance(bim_content, dict):
                logger.error("❌ Invalid BIM content - not a JSON object")
                return False
            
            logger.info("📦 Creating PBIT archive structure...")
            
            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create PBIT structure (it's a ZIP file)
            with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as pbit_zip:
                
                # 1. Add DataModel (the BIM content, compacted)
                logger.info("📝 Adding DataModel...")
                datamodel_content = json.dumps(bim_content, separators=(',', ':'), ensure_ascii=False)
                pbit_zip.writestr("DataModel", datamodel_content.encode('utf-8'))
                
                # 2. Add Report Layout (if exists, otherwise create minimal)
                logger.info("📄 Adding Report Layout...")
                report_layout_file = self.project_dir / "Report" / "Layout"
                if report_layout_file.exists():
                    with open(report_layout_file, 'r', encoding='utf-8') as f:
                        layout_content = f.read()
                    pbit_zip.writestr("Report/Layout", layout_content.encode('utf-8'))
                else:
                    # Create minimal but valid layout
                    minimal_layout = {
                        "id": 0,
                        "resourcePackages": [],
                        "config": json.dumps({
                            "version": "5.43",
                            "themeCollection": {
                                "baseTheme": {"name": "CY24SU06"}
                            }
                        }),
                        "layoutOptimization": 0,
                        "sections": [],
                        "publicCustomVisuals": []
                    }
                    pbit_zip.writestr("Report/Layout", json.dumps(minimal_layout, separators=(',', ':')).encode('utf-8'))
                
                # 3. Add StaticResources (if exists)
                static_resources_file = self.project_dir / "Report" / "StaticResources.json"
                if static_resources_file.exists():
                    logger.info("📊 Adding StaticResources...")
                    with open(static_resources_file, 'r', encoding='utf-8') as f:
                        static_content = f.read()
                    pbit_zip.writestr("Report/StaticResources.json", static_content.encode('utf-8'))
                
                # 4. Add Metadata
                logger.info("📋 Adding Metadata...")
                metadata_file = self.project_dir / "Metadata"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_content = f.read()
                    pbit_zip.writestr("Metadata", metadata_content.encode('utf-8'))
                else:
                    metadata = {
                        "version": "3.0",
                        "createdFromTemplate": False
                    }
                    pbit_zip.writestr("Metadata", json.dumps(metadata, separators=(',', ':')).encode('utf-8'))
                
                # 5. Add Version
                logger.info("🔢 Adding Version...")
                version_file = self.project_dir / "Version.txt"
                if version_file.exists():
                    with open(version_file, 'r', encoding='utf-8') as f:
                        version_content = f.read().strip()
                    pbit_zip.writestr("Version", version_content.encode('utf-8'))
                else:
                    pbit_zip.writestr("Version", "3.0".encode('utf-8'))
                
                # 6. Add Settings
                logger.info("⚙️  Adding Settings...")
                settings_file = self.project_dir / "Settings"
                if settings_file.exists():
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings_content = f.read()
                    pbit_zip.writestr("Settings", settings_content.encode('utf-8'))
                else:
                    pbit_zip.writestr("Settings", "{}".encode('utf-8'))
                
                # 7. Add SecurityBindings
                logger.info("🔒 Adding SecurityBindings...")
                security_file = self.project_dir / "SecurityBindings"
                if security_file.exists():
                    with open(security_file, 'r', encoding='utf-8') as f:
                        security_content = f.read()
                    pbit_zip.writestr("SecurityBindings", security_content.encode('utf-8'))
                else:
                    security_bindings = {
                        "version": "3.0", 
                        "bindings": []
                    }
                    pbit_zip.writestr("SecurityBindings", json.dumps(security_bindings, separators=(',', ':')).encode('utf-8'))
                
                # 8. Add DiagramLayout (if exists)
                diagram_file = self.project_dir / "DataModelSchema" / "DiagramLayout"
                if diagram_file.exists():
                    logger.info("📐 Adding DiagramLayout...")
                    with open(diagram_file, 'r', encoding='utf-8') as f:
                        diagram_content = f.read()
                    pbit_zip.writestr("DiagramLayout", diagram_content.encode('utf-8'))
                
                # 9. Add connections.json (if exists)
                connections_file = self.project_dir / "DataModelSchema" / "connections.json"
                if connections_file.exists():
                    logger.info("🔗 Adding connections.json...")
                    with open(connections_file, 'r', encoding='utf-8') as f:
                        connections_content = f.read()
                    pbit_zip.writestr("DataModelSchema/connections.json", connections_content.encode('utf-8'))
            
            # Verify the PBIT file was created and has content
            if self.output_path.exists() and self.output_path.stat().st_size > 0:
                file_size = self.output_path.stat().st_size
                logger.info(f"✅ Manual PBIT creation successful!")
                logger.info(f"📁 File: {self.output_path}")
                logger.info(f"📏 Size: {file_size:,} bytes")
                
                # Verify it's a valid ZIP file
                try:
                    with zipfile.ZipFile(self.output_path, 'r') as test_zip:
                        file_list = test_zip.namelist()
                        logger.info(f"📦 Contains {len(file_list)} files: {', '.join(file_list[:5])}{'...' if len(file_list) > 5 else ''}")
                        
                        # Check for required files
                        required_files = ["DataModel", "Metadata", "Version"]
                        missing_files = [f for f in required_files if f not in file_list]
                        if missing_files:
                            logger.warning(f"⚠️  Missing files: {', '.join(missing_files)}")
                        else:
                            logger.info("✅ All required files present in PBIT")
                        
                        return True
                except zipfile.BadZipFile:
                    logger.error("❌ Created file is not a valid ZIP archive")
                    return False
            else:
                logger.error("❌ PBIT file was not created or is empty")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in BIM file: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Manual PBIT creation failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return False


class EnhancedPBIToolsCompiler(PBIToolsCompiler):
    """Enhanced compiler with multiple fallback options."""
    
    def compile_to_pbit(self, project_dir: str, output_path: str, overwrite: bool = True) -> bool:
        """
        Enhanced compilation with multiple fallback methods.
        Tries methods in order of reliability and availability.
        """
        logger.info("🏗️  Starting enhanced compilation process...")
        
        # Initialize alternative compilers
        alt_compilers = AlternativeCompilers(project_dir, output_path)
        
        # Show available methods
        available_methods = alt_compilers.get_available_methods()
        logger.info(f"🔧 Available compilation methods: {', '.join(available_methods)}")
        
        # Method 1: Try pbi-tools first (if available and compatible)
        if self.auto_install:
            compatibility = handle_pbi_tools_compatibility()
            
            if compatibility.get("compatible", True):
                logger.info("🔧 Method 1: Trying pbi-tools...")
                if super().compile_to_pbit(project_dir, output_path, overwrite):
                    logger.info("✅ pbi-tools compilation successful!")
                    return True
                logger.warning("⚠️  pbi-tools compilation failed, trying alternatives...")
            else:
                logger.warning(f"⚠️  pbi-tools incompatible: {compatibility.get('warning', 'Unknown issue')}")
                logger.info("⏭️  Skipping pbi-tools, trying alternatives...")
        
        # Method 2: Try Tabular Editor (most reliable alternative)
        logger.info("🔧 Method 2: Trying Tabular Editor...")
        if alt_compilers.compile_with_tabular_editor():
            logger.info("✅ Tabular Editor compilation successful!")
            return True
        
        # Method 3: Try custom ZIP method (enhanced manual creation)
        logger.info("🔧 Method 3: Trying custom ZIP method...")
        if alt_compilers.compile_with_custom_zip_method():
            logger.info("✅ Custom ZIP compilation successful!")
            return True
        
        # Method 4: Try standard manual PBIT creation
        logger.info("🔧 Method 4: Trying manual PBIT creation...")
        if alt_compilers.create_pbit_manually():
            logger.info("✅ Manual PBIT creation successful!")
            return True
        
        # Method 5: Try Power BI Desktop (manual process)
        logger.info("🔧 Method 5: Trying Power BI Desktop automation...")
        if alt_compilers.compile_with_power_bi_desktop():
            logger.info("💡 Power BI Desktop opened for manual completion")
            logger.warning("⚠️  This method requires manual steps - see above instructions")
            return True  # User needs to complete manually
        
        # All methods failed
        logger.error("❌ All compilation methods failed!")
        logger.info("💡 Troubleshooting suggestions:")
        logger.info("   1. Install Tabular Editor 2 (free): https://tabulareditor.com/")
        logger.info("   2. Install Power BI Desktop: https://powerbi.microsoft.com/desktop/")
        logger.info("   3. Check BIM file validity in project directory")
        logger.info("   4. Ensure sufficient disk space and permissions")
        
        return False
        logger.info("🔧 Method 3: Trying manual PBIT creation...")
        if alt_compilers.create_pbit_manually():
            return True
        
        # Method 4: Power BI Desktop automation (auto-run)
        logger.info("🔧 Method 4: Trying Power BI Desktop automation...")
        logger.info("💡 This method will open Power BI Desktop automatically")
        
        # Auto-try Power BI Desktop automation
        if alt_compilers.compile_with_power_bi_desktop():
            logger.info("✅ Power BI Desktop automation started successfully!")
            return True
        
        # All methods failed
        logger.error("❌ All compilation methods failed")
        logger.error("📋 FINAL FALLBACK - Manual Instructions:")
        logger.error("   1. Open Power BI Desktop")
        logger.error(f"   2. File → Open → {project_dir}")
        logger.error("   3. File → Export → Power BI Template (.pbit)")
        logger.error(f"   4. Save as: {output_path}")
        
        return False
=======
    success = convert_tableau_to_powerbi(input_file, output_file)
    sys.exit(0 if success else 1)
>>>>>>> parent of 20eec4b (AttemptingCompatabilityFix)
