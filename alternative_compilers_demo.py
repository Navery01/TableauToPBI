#!/usr/bin/env python3
"""
Alternative PBIT Compilation Methods Demo
========================================

This script demonstrates various methods to compile Power BI Template (.pbit) files
without relying on pbi-tools. These are useful when pbi-tools is incompatible or
unavailable.

Methods included:
1. Tabular Editor (free and paid versions)
2. Manual ZIP-based PBIT creation
3. Power BI Desktop automation
4. Analysis Services deployment
5. PowerShell cmdlets
6. Python-based compilation

Usage:
    python alternative_compilers_demo.py --project-dir "path/to/project" --output "output.pbit"
"""

import os
import sys
import json
import zipfile
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extractors.TB2PBI.tableau_to_powerbi import AlternativeCompilers


def check_system_requirements() -> Dict[str, Any]:
    """Check what compilation tools are available on the system."""
    print("🔍 Checking system requirements for alternative compilation methods...")
    
    requirements = {
        "tabular_editor": False,
        "power_bi_desktop": False,
        "powershell": False,
        "analysis_services": False,
        "python_packages": {}
    }
    
    # Check Tabular Editor
    tabular_paths = [
        r"C:\Program Files (x86)\Tabular Editor\TabularEditor.exe",
        r"C:\Program Files\Tabular Editor\TabularEditor.exe",
        r"C:\Program Files\Tabular Editor 3\TabularEditor3.exe",
        r".\TabularEditor.exe"
    ]
    
    for path in tabular_paths:
        if Path(path).exists():
            requirements["tabular_editor"] = path
            print(f"✅ Found Tabular Editor: {path}")
            break
    
    if not requirements["tabular_editor"]:
        print("❌ Tabular Editor not found")
        print("💡 Download from: https://tabulareditor.com/")
    
    # Check Power BI Desktop
    pbi_paths = [
        r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
        r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
    ]
    
    for path in pbi_paths:
        if Path(path).exists():
            requirements["power_bi_desktop"] = path
            print(f"✅ Found Power BI Desktop: {path}")
            break
    
    if not requirements["power_bi_desktop"]:
        print("❌ Power BI Desktop not found")
        print("💡 Download from: https://powerbi.microsoft.com/desktop/")
    
    # Check PowerShell
    try:
        result = subprocess.run(["powershell.exe", "-Command", "Get-Host"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            requirements["powershell"] = True
            print("✅ PowerShell available")
        else:
            print("❌ PowerShell not available")
    except:
        print("❌ PowerShell not available")
    
    # Check Python packages
    packages_to_check = ['msal', 'requests', 'adodbapi', 'pythonnet']
    for package in packages_to_check:
        try:
            __import__(package)
            requirements["python_packages"][package] = True
            print(f"✅ Python package available: {package}")
        except ImportError:
            requirements["python_packages"][package] = False
            print(f"❌ Python package missing: {package}")
    
    return requirements


def demonstrate_manual_pbit_creation(project_dir: str, output_path: str) -> bool:
    """Demonstrate manual PBIT creation with detailed logging."""
    print("\n🔧 Demonstrating Manual PBIT Creation Method")
    print("=" * 50)
    
    project_path = Path(project_dir)
    output_path = Path(output_path)
    
    # Check for required files
    bim_file = project_path / "DataModelSchema" / "Model.bim"
    if not bim_file.exists():
        print(f"❌ Model.bim not found at {bim_file}")
        return False
    
    print(f"📁 Project directory: {project_path}")
    print(f"📄 BIM file: {bim_file}")
    print(f"🎯 Output: {output_path}")
    
    try:
        # Load BIM content
        print("\n📖 Loading BIM model...")
        with open(bim_file, 'r', encoding='utf-8') as f:
            bim_content = json.load(f)
        
        print(f"✅ BIM loaded successfully ({len(json.dumps(bim_content)):,} characters)")
        
        # Analyze BIM structure
        print("\n🔍 Analyzing BIM structure...")
        if isinstance(bim_content, dict):
            if "model" in bim_content:
                model = bim_content["model"]
                print(f"   - Model name: {model.get('name', 'Unknown')}")
                print(f"   - Tables: {len(model.get('tables', []))}")
                print(f"   - Relationships: {len(model.get('relationships', []))}")
                print(f"   - Measures: {sum(len(table.get('measures', [])) for table in model.get('tables', []))}")
        
        # Create PBIT file
        print("\n📦 Creating PBIT file...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as pbit:
            
            # Add DataModel
            print("   📝 Adding DataModel...")
            datamodel_json = json.dumps(bim_content, separators=(',', ':'), ensure_ascii=False)
            pbit.writestr("DataModel", datamodel_json.encode('utf-8'))
            
            # Add Metadata
            print("   📋 Adding Metadata...")
            metadata = {
                "version": "3.0",
                "createdFromTemplate": True,
                "templateDisplayName": output_path.stem
            }
            pbit.writestr("Metadata", json.dumps(metadata, separators=(',', ':')))
            
            # Add Version
            print("   🔢 Adding Version...")
            pbit.writestr("Version", "3.0")
            
            # Add Settings
            print("   ⚙️  Adding Settings...")
            pbit.writestr("Settings", "{}")
            
            # Add SecurityBindings
            print("   🔒 Adding SecurityBindings...")
            security = {"version": "3.0", "bindings": []}
            pbit.writestr("SecurityBindings", json.dumps(security, separators=(',', ':')))
            
            # Add Report Layout
            print("   📄 Adding Report Layout...")
            layout = {
                "id": 0,
                "resourcePackages": [],
                "config": json.dumps({
                    "version": "5.43",
                    "themeCollection": {"baseTheme": {"name": "CY24SU06"}}
                }),
                "layoutOptimization": 0,
                "sections": [{
                    "id": 0,
                    "name": "ReportSection",
                    "displayName": "Page 1",
                    "visualContainers": [],
                    "config": json.dumps({"visibility": 0})
                }],
                "publicCustomVisuals": []
            }
            pbit.writestr("Report/Layout", json.dumps(layout, separators=(',', ':')))
        
        # Verify creation
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"\n✅ PBIT created successfully!")
            print(f"   📁 File: {output_path}")
            print(f"   📏 Size: {file_size:,} bytes")
            
            # Verify ZIP structure
            with zipfile.ZipFile(output_path, 'r') as test_zip:
                files = test_zip.namelist()
                print(f"   📦 Contains: {', '.join(files)}")
            
            return True
        else:
            print("❌ PBIT file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Manual PBIT creation failed: {e}")
        return False


def demonstrate_tabular_editor_method(project_dir: str, output_path: str) -> bool:
    """Demonstrate Tabular Editor compilation method."""
    print("\n🔧 Demonstrating Tabular Editor Method")
    print("=" * 40)
    
    # Use the AlternativeCompilers class
    alt_compiler = AlternativeCompilers(project_dir, output_path)
    return alt_compiler.compile_with_tabular_editor()


def create_sample_project(base_dir: str) -> str:
    """Create a sample project for demonstration."""
    print("\n🏗️  Creating sample project for demonstration...")
    
    project_dir = Path(base_dir) / "sample_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create DataModelSchema directory
    schema_dir = project_dir / "DataModelSchema"
    schema_dir.mkdir(exist_ok=True)
    
    # Create a simple BIM model
    sample_bim = {
        "name": "SampleModel",
        "compatibilityLevel": 1600,
        "model": {
            "name": "SampleModel",
            "culture": "en-US",
            "tables": [
                {
                    "name": "SampleTable",
                    "columns": [
                        {
                            "name": "ID",
                            "dataType": "int64",
                            "sourceColumn": "ID"
                        },
                        {
                            "name": "Name",
                            "dataType": "string",
                            "sourceColumn": "Name"
                        }
                    ],
                    "partitions": [
                        {
                            "name": "Partition",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    "    Source = Table.FromRows({",
                                    "        {1, \"Sample 1\"},",
                                    "        {2, \"Sample 2\"}",
                                    "    }, {\"ID\", \"Name\"})",
                                    "in",
                                    "    Source"
                                ]
                            }
                        }
                    ]
                }
            ],
            "relationships": [],
            "cultures": [
                {
                    "name": "en-US"
                }
            ]
        }
    }
    
    # Write BIM file
    bim_file = schema_dir / "Model.bim"
    with open(bim_file, 'w', encoding='utf-8') as f:
        json.dump(sample_bim, f, indent=2)
    
    # Create other project files
    (project_dir / "Metadata").write_text('{"version": "3.0"}')
    (project_dir / "Version.txt").write_text("3.0")
    (project_dir / "Settings").write_text("{}")
    (project_dir / "SecurityBindings").write_text('{"version": "3.0", "bindings": []}')
    
    # Create Report directory
    report_dir = project_dir / "Report"
    report_dir.mkdir(exist_ok=True)
    
    print(f"✅ Sample project created: {project_dir}")
    return str(project_dir)


def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description="Demonstrate alternative PBIT compilation methods")
    parser.add_argument("--project-dir", help="Path to existing project directory")
    parser.add_argument("--output", default="sample_output.pbit", help="Output PBIT file path")
    parser.add_argument("--create-sample", action="store_true", help="Create a sample project for testing")
    parser.add_argument("--method", choices=["all", "manual", "tabular", "check"], default="all",
                       help="Which method to demonstrate")
    
    args = parser.parse_args()
    
    print("🚀 Alternative PBIT Compilation Methods Demo")
    print("=" * 50)
    
    # Check system requirements
    if args.method in ["all", "check"]:
        requirements = check_system_requirements()
        if args.method == "check":
            return
    
    # Create or use project directory
    if args.create_sample or not args.project_dir:
        project_dir = create_sample_project(".")
    else:
        project_dir = args.project_dir
    
    output_path = args.output
    
    print(f"\n🎯 Using project: {project_dir}")
    print(f"🎯 Output file: {output_path}")
    
    success_count = 0
    total_methods = 0
    
    # Demonstrate methods
    if args.method in ["all", "manual"]:
        total_methods += 1
        if demonstrate_manual_pbit_creation(project_dir, f"manual_{output_path}"):
            success_count += 1
    
    if args.method in ["all", "tabular"]:
        total_methods += 1
        if demonstrate_tabular_editor_method(project_dir, f"tabular_{output_path}"):
            success_count += 1
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 20)
    print(f"✅ Successful methods: {success_count}/{total_methods}")
    
    if success_count > 0:
        print("🎉 At least one alternative compilation method worked!")
        print("💡 You can use these methods when pbi-tools is not available")
    else:
        print("❌ No compilation methods succeeded")
        print("💡 Consider installing Tabular Editor or Power BI Desktop")
    
    print("\n📚 Additional Resources:")
    print("   - Tabular Editor: https://tabulareditor.com/")
    print("   - Power BI Desktop: https://powerbi.microsoft.com/desktop/")
    print("   - PBIT format documentation: Microsoft Power BI documentation")


if __name__ == "__main__":
    main()
