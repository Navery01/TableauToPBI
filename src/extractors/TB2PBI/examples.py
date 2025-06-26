"""
Example usage of the Tableau to Power BI converter module.
"""

import os
import sys
import logging
from pathlib import Path

# Add the module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tableau_to_powerbi import (
    TableauToPowerBIConverter,
    convert_tableau_to_powerbi,
    analyze_tableau_workbook,
    TableauToPowerBIError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def example_basic_conversion():
    """Example: Basic conversion using convenience function."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Conversion")
    print("=" * 60)
    
    input_file = "examples\helloworld.twbx"
    output_file = "./output/converted_workbook.pbit"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Converting: {input_file} -> {output_file}")
    
    try:
        success = convert_tableau_to_powerbi(input_file, output_file)
        
        if success:
            print("✅ Conversion completed successfully!")
            print(f"📁 Output file: {output_file}")
        else:
            print("❌ Conversion failed. Check logs for details.")
            
    except TableauToPowerBIError as e:
        print(f"❌ Conversion error: {e}")


def example_advanced_conversion():
    """Example: Advanced conversion with custom settings."""
    print("=" * 60)
    print("EXAMPLE 2: Advanced Conversion")
    print("=" * 60)
    
    input_file = "examples\helloworld.twbx"
    output_file = "./output/advanced_conversion.pbit"
    project_dir = "./output/project_files"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    # Create converter instance
    converter = TableauToPowerBIConverter()
    
    print(f"Converting: {input_file}")
    print(f"Output: {output_file}")
    print(f"Project files: {project_dir}")
    
    try:
        success = converter.convert(
            twbx_path=input_file,
            output_path=output_file,
            project_dir=project_dir,
            cleanup_temp=False  # Keep temp files for inspection
        )
        
        if success:
            print("✅ Advanced conversion completed!")
            print(f"📁 Output file: {output_file}")
            print(f"📂 Project files preserved at: {project_dir}")
        else:
            print("❌ Conversion failed, but project files are available for inspection.")
            print(f"📂 Project files: {project_dir}")
            
    except TableauToPowerBIError as e:
        print(f"❌ Conversion error: {e}")


def example_analyze_workbook():
    """Example: Analyze Tableau workbook structure."""
    print("=" * 60)
    print("EXAMPLE 3: Workbook Analysis")
    print("=" * 60)
    
    input_file = "examples\helloworld.twbx"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    try:
        print(f"Analyzing: {input_file}")
        workbook_info = analyze_tableau_workbook(input_file)
        
        print("\n📊 WORKBOOK ANALYSIS RESULTS:")
        print("-" * 40)
        
        # Data sources
        print(f"📋 Data Sources: {len(workbook_info.get('datasources', []))}")
        for i, ds in enumerate(workbook_info.get('datasources', []), 1):
            print(f"  {i}. {ds.get('name', 'Unnamed')} ({len(ds.get('fields', []))} fields)")
        
        # Worksheets
        print(f"\n📈 Worksheets: {len(workbook_info.get('worksheets', []))}")
        for i, ws in enumerate(workbook_info.get('worksheets', []), 1):
            print(f"  {i}. {ws.get('name', 'Unnamed')}")
        
        # Calculated fields
        calc_fields = workbook_info.get('calculated_fields', [])
        print(f"\n🧮 Calculated Fields: {len(calc_fields)}")
        for i, calc in enumerate(calc_fields[:5], 1):  # Show first 5
            print(f"  {i}. {calc.get('name', 'Unnamed')}")
        if len(calc_fields) > 5:
            print(f"  ... and {len(calc_fields) - 5} more")
        
        # Parameters
        parameters = workbook_info.get('parameters', [])
        print(f"\n⚙️  Parameters: {len(parameters)}")
        for i, param in enumerate(parameters, 1):
            print(f"  {i}. {param.get('name', 'Unnamed')} ({param.get('datatype', 'unknown')})")
        
        # Dashboards
        dashboards = workbook_info.get('dashboards', [])
        print(f"\n📊 Dashboards: {len(dashboards)}")
        for i, dash in enumerate(dashboards, 1):
            print(f"  {i}. {dash.get('name', 'Unnamed')}")
            
    except TableauToPowerBIError as e:
        print(f"❌ Analysis error: {e}")


def example_batch_conversion():
    """Example: Batch convert multiple files."""
    print("=" * 60)
    print("EXAMPLE 4: Batch Conversion")
    print("=" * 60)
    
    input_dir = "./"
    output_dir = "./output/batch/"
    
    # Find all .twbx files
    twbx_files = list(Path(input_dir).glob("*.twbx"))
    
    if not twbx_files:
        print(f"❌ No .twbx files found in {input_dir}")
        return
    
    print(f"Found {len(twbx_files)} Tableau workbook(s)")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    converter = TableauToPowerBIConverter()
    successful = 0
    failed = 0
    
    for twbx_file in twbx_files:
        print(f"\n🔄 Converting: {twbx_file.name}")
        
        output_file = os.path.join(output_dir, f"{twbx_file.stem}.pbit")
        
        try:
            success = converter.convert(
                twbx_path=str(twbx_file),
                output_path=output_file
            )
            
            if success:
                print(f"  ✅ Success: {output_file}")
                successful += 1
            else:
                print(f"  ❌ Failed: {twbx_file.name}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print(f"\n📊 BATCH CONVERSION RESULTS:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Output directory: {output_dir}")


def check_prerequisites():
    """Check if all prerequisites are available."""
    print("=" * 60)
    print("CHECKING PREREQUISITES")
    print("=" * 60)
    
    # Check pbi-tools
    from tableau_to_powerbi import PBIToolsCompiler
    
    if PBIToolsCompiler.is_pbi_tools_available():
        print("✅ pbi-tools is available")
    else:
        print("❌ pbi-tools is NOT available")
        print("   Install with: choco install pbi-tools")
        print("   Or download from: https://github.com/pbi-tools/pbi-tools/releases")
    
    # Check input file
    input_file = "examples\helloworld.twbx"
    if os.path.exists(input_file):
        print(f"✅ Sample input file found: {input_file}")
    else:
        print(f"❌ Sample input file NOT found: {input_file}")
        print("   Place a Tableau workbook (.twbx) in the current directory")
    
    print()


def main():
    """Run all examples."""
    print("TABLEAU TO POWER BI CONVERTER - EXAMPLES")
    print("=" * 60)
    
    # Check prerequisites first
    check_prerequisites()
    
    # Run examples
    try:
        example_analyze_workbook()
        print("\n")
        
        example_basic_conversion()
        print("\n")
        
        example_advanced_conversion()  
        print("\n")
        
        example_batch_conversion()
        
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
