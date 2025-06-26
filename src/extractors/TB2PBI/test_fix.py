#!/usr/bin/env python3
"""
Test script to verify ReportSettings.json fix
"""

import sys
import os
from pathlib import Path

# Add the module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tableau_to_powerbi import TableauToPowerBIConverter

def test_conversion():
    """Test the conversion to verify ReportSettings.json is created correctly."""
    
    # Use the sample file
    input_file = "../../../examples/helloworld.twbx"
    output_file = "./test_output/test_conversion.pbit"
    project_dir = "./test_output/project_files"
    
    if not os.path.exists(input_file):
        print(f"❌ Sample file not found: {input_file}")
        return False
    
    print("🧪 Testing ReportSettings.json fix...")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Project: {project_dir}")
    
    # Create converter and test
    converter = TableauToPowerBIConverter()
    
    try:
        success = converter.convert(
            twbx_path=input_file,
            output_path=output_file,
            project_dir=project_dir,
            cleanup_temp=False  # Keep files for inspection
        )
        
        if success:
            print("✅ Conversion completed successfully!")
            
            # Check if ReportSettings.json was created and is valid
            report_settings_path = Path(project_dir) / "ReportSettings.json"
            if report_settings_path.exists():
                print("✅ ReportSettings.json was created")
                
                # Try to read and validate the JSON
                import json
                try:
                    with open(report_settings_path, 'r') as f:
                        data = json.load(f)
                    print("✅ ReportSettings.json is valid JSON")
                    print(f"📄 Content preview: {json.dumps(data, indent=2)[:200]}...")
                    return True
                except json.JSONDecodeError as e:
                    print(f"❌ ReportSettings.json is invalid JSON: {e}")
                    return False
            else:
                print("❌ ReportSettings.json was not created")
                return False
        else:
            print("❌ Conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

if __name__ == "__main__":
    print("TESTING REPORTSETTINGS.JSON FIX")
    print("=" * 50)
    
    success = test_conversion()
    
    print("=" * 50)
    if success:
        print("🎉 Test PASSED - ReportSettings.json fix is working!")
    else:
        print("💥 Test FAILED - ReportSettings.json issue persists")
