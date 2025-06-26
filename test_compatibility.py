#!/usr/bin/env python3
"""
Test the improved error handling for pbi-tools compatibility issues
"""

import sys
import os
from pathlib import Path

# Setup paths
app_root = Path(__file__).parent
sys.path.insert(0, str(app_root / "src" / "extractors" / "TB2PBI"))

def test_conversion_with_compatibility_issue():
    """Test conversion with current pbi-tools compatibility issue"""
    print("TESTING CONVERSION WITH PBI-TOOLS COMPATIBILITY")
    print("=" * 60)
    
    try:
        from tableau_to_powerbi import TableauToPowerBIConverter
        
        # Use sample file
        input_file = "examples/helloworld.twbx"
        output_file = "output/test_compatibility.pbit"
        project_dir = "output/test_compatibility_project"
        
        if not os.path.exists(input_file):
            print(f"❌ Sample file not found: {input_file}")
            return False
        
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Project: {project_dir}")
        print()
        
        # Create converter
        converter = TableauToPowerBIConverter()
        
        # Attempt conversion
        print("🔄 Starting conversion...")
        success = converter.convert(
            twbx_path=input_file,
            output_path=output_file,
            project_dir=project_dir,
            cleanup_temp=False
        )
        
        print(f"\n📊 Conversion Result: {'SUCCESS' if success else 'FAILED'}")
        
        # Check what files were created
        project_path = Path(project_dir)
        if project_path.exists():
            print("✅ Project files created:")
            for file in project_path.rglob("*"):
                if file.is_file():
                    print(f"   📄 {file.relative_to(project_path)}")
        else:
            print("❌ No project files found")
        
        pbit_path = Path(output_file)
        if pbit_path.exists():
            print(f"✅ .pbit file created: {output_file}")
        else:
            print("ℹ️  .pbit file not created (expected due to compatibility issue)")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function"""
    print("PBI-TOOLS COMPATIBILITY TEST")
    print("=" * 60)
    
    success = test_conversion_with_compatibility_issue()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED")
        print("   Conversion handled compatibility issues gracefully")
        print("   Project files should be available for manual compilation")
    else:
        print("💥 TEST FAILED")
        print("   Check error messages above")
    
    print("\n💡 MANUAL STEPS:")
    print("   1. Check output/test_compatibility_project folder")
    print("   2. Open Power BI Desktop")
    print("   3. File → Open → Select the project folder")
    print("   4. File → Export → Power BI Template")
    print("=" * 60)

if __name__ == "__main__":
    main()
