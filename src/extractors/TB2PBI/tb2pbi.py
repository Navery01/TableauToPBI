import zipfile
import os
import xml.etree.ElementTree as ET
import json
import subprocess

# ========== STEP 1: Extract TWBX and Find TWB ==========
def extract_twbx(twbx_path, output_dir="extracted_twbx"):
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(twbx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    print(f"✅ Extracted to {output_dir}")
    return output_dir

def find_twb_file(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".twb"):
                return os.path.join(root, file)
    raise FileNotFoundError("No .twb file found in extracted .twbx.")

# ========== STEP 2: Parse TWB XML ==========
def parse_twb(twb_path):
    tree = ET.parse(twb_path)
    root = tree.getroot()

    workbook_info = {
        "datasources": [],
        "worksheets": [],
        "calculated_fields": [],
        "joins": [],
        "parameters": []
    }

    for ds in root.findall('.//datasource'):
        datasource = {
            "name": ds.get('name'),
            "fields": [],
            "connections": []
        }
        for column in ds.findall('.//column'):
            datasource["fields"].append({
                "name": column.get('name'),
                "datatype": column.get('datatype'),
                "role": column.get('role'),
                "type": column.get('type')
            })
        for conn in ds.findall('.//connection'):
            datasource["connections"].append({
                "class": conn.get('class'),
                "dbname": conn.get('dbname'),
                "server": conn.get('server'),
                "authentication": conn.get('authentication')
            })
        workbook_info["datasources"].append(datasource)

    for calc in root.findall('.//calculation'):
        workbook_info["calculated_fields"].append({
            "name": calc.get('name'),
            "formula": calc.get('formula')
        })

    for relation in root.findall('.//relation'):
        if relation.get('type') == 'join':
            workbook_info["joins"].append({
                "left": relation.get('left'),
                "right": relation.get('right'),
                "operator": relation.get('operator')
            })

    for ws in root.findall('.//worksheet'):
        workbook_info["worksheets"].append({
            "name": ws.get('name')
        })

    for param in root.findall('.//column[@param-domain-type]'):
        workbook_info["parameters"].append({
            "name": param.get('name'),
            "datatype": param.get('datatype'),
            "param-domain-type": param.get('param-domain-type')
        })

    return workbook_info

# ========== STEP 3: Convert to BIM ==========
def map_datatype(tableau_type):
    mapping = {
        "string": "string",
        "real": "double",
        "integer": "int64",
        "boolean": "boolean",
        "date": "DateTime"
    }
    return mapping.get(tableau_type.lower(), "string")

def convert_formula_to_dax(formula):
    if not formula:
        return "BLANK()"
    formula = formula.replace("IF ", "IF(")
    return formula  # Placeholder

def convert_to_bim(tableau_data):
    tables = []
    for ds in tableau_data['datasources']:
        if not ds.get('name'):
            continue
            
        table_name = ds['name'].replace(" ", "_").replace("-", "_")
        table = {
            "name": table_name,
            "columns": [],
            "partitions": [
                {
                    "name": "Partition",
                    "dataView": "full",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t]),",
                            "    #\"Changed Type\" = Table.TransformColumnTypes(Source,{{\"Column1\", type text}})",
                            "in",
                            "    #\"Changed Type\""
                        ]
                    }
                }
            ]
        }
        
        # Add columns
        for field in ds.get('fields', []):
            if field.get('name'):
                column_name = field['name'].replace("[", "").replace("]", "").replace(" ", "_").replace("-", "_")
                table['columns'].append({
                    "name": column_name,
                    "dataType": map_datatype(field.get('datatype', 'string')),
                    "isHidden": False,
                    "sourceColumn": column_name
                })
        
        # Ensure at least one column exists
        if not table['columns']:
            table['columns'].append({
                "name": "DefaultColumn",
                "dataType": "string",
                "isHidden": False,
                "sourceColumn": "DefaultColumn"
            })
        
        tables.append(table)

    # If no tables found, create a dummy table
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
                    "name": "Partition",
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

    # Enhanced V3 BIM structure with all required elements
    return {
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
            "dataSources": [
                {
                    "type": "structured",
                    "name": "localhost",
                    "connectionDetails": {
                        "protocol": "tds",
                        "address": {
                            "server": "localhost",
                            "database": "SampleDB"
                        }
                    },
                    "credential": {
                        "AuthenticationKind": "UsernamePassword",
                        "kind": "SQL",
                        "path": "localhost;SampleDB"
                    }
                }
            ],
            "tables": tables,
            "annotations": [
                {
                    "name": "TabularEditor_SerializeOptions",
                    "value": "{\"IgnoreInferredObjects\":false,\"IgnoreInferredProperties\":false,\"IgnoreTimestamps\":false,\"SplitMultilineStrings\":false,\"PrefixFilenames\":false,\"LocalTranslations\":false,\"LocalPerspectives\":false,\"LocalRelationships\":false,\"Levels\":[\"Data Sources\",\"Shared Expressions\",\"Perspectives\",\"Relationships\",\"Roles\",\"Tables\",\"Tables/Columns\",\"Tables/Hierarchies\",\"Tables/Measures\",\"Tables/Partitions\",\"Tables/Calculation Groups\",\"Translations\"]}"
                },
                {
                    "name": "PBI_QueryOrder",
                    "value": "[\"DummyTable\"]"
                }
            ]
        }
    }

# ========== STEP 4: Write PbixProj Layout ==========
def save_bim_model(bim_data, pbixproj_dir="pbixproj_model"):
    dms_dir = os.path.join(pbixproj_dir, "DataModelSchema")
    os.makedirs(dms_dir, exist_ok=True)
    bim_path = os.path.join(dms_dir, "Model.bim")
    with open(bim_path, 'w') as f:
        json.dump(bim_data, f, indent=2)
    print(f"✅ Saved BIM to {bim_path}")

def write_version_file(pbixproj_dir):
    version_path = os.path.join(pbixproj_dir, "Version.txt")
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write("3.0")
    print(f"📝 Added {version_path}")

def write_minimal_layout(pbixproj_dir):
    layout_dir = os.path.join(pbixproj_dir, "Report")
    os.makedirs(layout_dir, exist_ok=True)
    layout_path = os.path.join(layout_dir, "Layout")
    
    # Create a minimal but valid layout JSON structure
    minimal_layout = {
        "id": 0,
        "resourcePackages": [],
        "config": "{\"version\":\"5.43\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY24SU06\"}}}",
        "layoutOptimization": 0
    }
    
    with open(layout_path, 'w', encoding='utf-8') as f:
        json.dump(minimal_layout, f)
    print(f"📝 Added stub Report/Layout")

def write_static_resources(pbixproj_dir):
    layout_dir = os.path.join(pbixproj_dir, "Report")
    os.makedirs(layout_dir, exist_ok=True)
    static_path = os.path.join(layout_dir, "StaticResources.json")
    with open(static_path, 'w') as f:
        json.dump({}, f)
    print(f"📝 Added stub Report/StaticResources.json")

def write_settings_file(pbixproj_dir):
    """Write the Settings file required for V3 format"""
    settings_path = os.path.join(pbixproj_dir, "Settings")
    with open(settings_path, 'w') as f:
        json.dump({}, f)
    print(f"📝 Added Settings file")

def write_metadata_file(pbixproj_dir):
    """Write metadata file for V3 compatibility"""
    metadata_path = os.path.join(pbixproj_dir, "Metadata")
    with open(metadata_path, 'w') as f:
        json.dump({
            "version": "3.0",
            "minVersion": "3.0"
        }, f)
    print(f"📝 Added Metadata file")

def write_connections_file(pbixproj_dir):
    """Write connections file"""
    conn_dir = os.path.join(pbixproj_dir, "DataModelSchema")
    os.makedirs(conn_dir, exist_ok=True)
    conn_path = os.path.join(conn_dir, "connections.json")
    with open(conn_path, 'w') as f:
        json.dump([], f)
    print(f"📝 Added connections.json")

def write_diagram_layout(pbixproj_dir):
    """Write DiagramLayout file required for V3 format"""
    dms_dir = os.path.join(pbixproj_dir, "DataModelSchema")
    os.makedirs(dms_dir, exist_ok=True)
    diagram_path = os.path.join(dms_dir, "DiagramLayout")
    
    # Create minimal diagram layout
    diagram_layout = {
        "version": 1,
        "diagramLayouts": []
    }
    
    with open(diagram_path, 'w', encoding='utf-8') as f:
        json.dump(diagram_layout, f)
    print(f"📝 Added DiagramLayout")

def write_report_metadata(pbixproj_dir):
    """Write ReportMetadata.json file required for V3 format"""
    metadata_path = os.path.join(pbixproj_dir, "ReportMetadata.json")
    
    # Create minimal report metadata structure
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
    print(f"📝 Added ReportMetadata.json")

def write_security_bindings(pbixproj_dir):
    """Write SecurityBindings.json file for V3 format"""
    security_path = os.path.join(pbixproj_dir, "SecurityBindings.json")
    
    # Create minimal security bindings
    security_bindings = {
        "version": "3.0",
        "bindings": []
    }
    
    with open(security_path, 'w', encoding='utf-8') as f:
        json.dump(security_bindings, f)
    print(f"📝 Added SecurityBindings.json")

# ========== STEP 5: Compile to .pbit ==========
def generate_pbit_from_pbixproj(pbixproj_path, output_path="./src/extractors/TB2PBI/output.pbit"):
    print("🏗️  Compiling .pbit using pbi-tools...")
    try:
        result = subprocess.run([
            "pbi-tools", "compile",
            pbixproj_path,          # required
            output_path,            # outPath
            "PBIT",                 # format
            "True"                  # overwrite
        ], capture_output=True, text=True, check=True)
        print(f"✅ .pbit created at: {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ Error creating .pbit:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)


# ========== STEP 6: Master Function ==========
def convert_twbx_to_pbit(twbx_file):
    print("🚀 Starting conversion pipeline...")

    extracted = extract_twbx(twbx_file)
    twb = find_twb_file(extracted)
    tableau_data = parse_twb(twb)

    bim = convert_to_bim(tableau_data)
    pbixproj = "pbixproj_model"

    # Create all required files for V3 format
    save_bim_model(bim, pbixproj)
    write_version_file(pbixproj)
    write_settings_file(pbixproj)
    write_metadata_file(pbixproj)
    write_connections_file(pbixproj)
    write_minimal_layout(pbixproj)
    write_static_resources(pbixproj)
    write_diagram_layout(pbixproj)
    write_report_metadata(pbixproj)
    write_security_bindings(pbixproj)
    write_report_metadata(pbixproj)
    write_security_bindings(pbixproj)
    
    try:
        generate_pbit_from_pbixproj(pbixproj)
        print("🎉 Done! Open the generated .pbit in Power BI Desktop.")
    except Exception as e:
        print(f"⚠️  Compilation failed: {e}")
        print(f"📁 PbixProj files created at: {pbixproj}")
        print("   You can inspect the files and try manual compilation.")

# ========== MAIN ==========
if __name__ == "__main__":
    your_twbx = "./src/extractors/TB2PBI/helloworld.twbx"  # Replace with your file
    convert_twbx_to_pbit(your_twbx)
