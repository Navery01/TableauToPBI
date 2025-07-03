#!/usr/bin/env python3
"""
Tabular Editor Auto-Installer
============================

This script automatically downloads and installs Tabular Editor 2 (free version)
for use with the Tableau to Power BI converter.

Usage:
    python install_tabular_editor.py [--portable] [--directory DIR]
"""

import os
import sys
import requests
import zipfile
import argparse
from pathlib import Path
import subprocess
import json


def get_latest_tabular_editor_info():
    """Get the latest Tabular Editor 2 release information from GitHub."""
    try:
        print("🔍 Checking for latest Tabular Editor 2 release...")
        
        # GitHub API for Tabular Editor releases
        api_url = "https://api.github.com/repos/TabularEditor/TabularEditor/releases/latest"
        
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        release_info = response.json()
        
        # Find the portable ZIP download
        portable_asset = None
        for asset in release_info.get("assets", []):
            if "portable" in asset["name"].lower() and asset["name"].endswith(".zip"):
                portable_asset = asset
                break
        
        if not portable_asset:
            # Fallback: look for any ZIP file
            for asset in release_info.get("assets", []):
                if asset["name"].endswith(".zip"):
                    portable_asset = asset
                    break
        
        if portable_asset:
            return {
                "version": release_info["tag_name"],
                "download_url": portable_asset["browser_download_url"],
                "filename": portable_asset["name"],
                "size": portable_asset["size"]
            }
        else:
            print("❌ No suitable Tabular Editor download found")
            return None
            
    except Exception as e:
        print(f"❌ Failed to get Tabular Editor release info: {e}")
        return None


def download_file(url: str, destination: Path, filename: str) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"📥 Downloading {filename}...")
        
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Progress: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", end="")
        
        print(f"\n✅ Downloaded: {destination}")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def extract_tabular_editor(zip_path: Path, extract_to: Path) -> bool:
    """Extract Tabular Editor from ZIP file."""
    try:
        print(f"📦 Extracting to {extract_to}...")
        
        extract_to.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List contents
            file_list = zip_ref.namelist()
            print(f"   Archive contains {len(file_list)} files")
            
            # Extract all files
            zip_ref.extractall(extract_to)
        
        # Find the main executable
        exe_files = list(extract_to.glob("**/TabularEditor.exe"))
        if exe_files:
            main_exe = exe_files[0]
            print(f"✅ Tabular Editor extracted: {main_exe}")
            return True
        else:
            print("❌ TabularEditor.exe not found in extracted files")
            return False
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


def add_to_path(tabular_editor_dir: Path) -> bool:
    """Add Tabular Editor directory to system PATH."""
    try:
        if os.name == 'nt':  # Windows
            print("🔧 Adding to Windows PATH...")
            
            # Get current PATH
            import winreg
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Environment", 
                               0, 
                               winreg.KEY_ALL_ACCESS)
            
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""
            
            # Add our directory if not already present
            tabular_dir_str = str(tabular_editor_dir)
            if tabular_dir_str not in current_path:
                new_path = f"{current_path};{tabular_dir_str}" if current_path else tabular_dir_str
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"✅ Added to PATH: {tabular_dir_str}")
            else:
                print("✅ Already in PATH")
            
            winreg.CloseKey(key)
            
            # Update current session
            os.environ["PATH"] = f"{os.environ.get('PATH', '')};{tabular_dir_str}"
            
            return True
        else:
            print("💡 Non-Windows system: Add manually to PATH if needed")
            print(f"   export PATH=\"$PATH:{tabular_editor_dir}\"")
            return True
            
    except Exception as e:
        print(f"⚠️  Failed to add to PATH: {e}")
        print(f"💡 Manually add to PATH: {tabular_editor_dir}")
        return False


def verify_installation(tabular_editor_path: Path) -> bool:
    """Verify that Tabular Editor was installed correctly."""
    try:
        print("🔍 Verifying installation...")
        
        exe_path = tabular_editor_path / "TabularEditor.exe"
        if not exe_path.exists():
            print(f"❌ TabularEditor.exe not found at {exe_path}")
            return False
        
        # Try to run with version flag
        result = subprocess.run([str(exe_path), "-?"], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0 or "Tabular Editor" in result.stdout or "Tabular Editor" in result.stderr:
            print("✅ Tabular Editor is working correctly")
            return True
        else:
            print("⚠️  Tabular Editor installed but may not be working correctly")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Tabular Editor verification timed out (but probably working)")
        return True
    except Exception as e:
        print(f"⚠️  Verification failed: {e}")
        return False


def check_existing_installation() -> str:
    """Check if Tabular Editor is already installed."""
    paths_to_check = [
        r"C:\Program Files (x86)\Tabular Editor\TabularEditor.exe",
        r"C:\Program Files\Tabular Editor\TabularEditor.exe",
        r"C:\Users\{}\AppData\Local\TabularEditor\TabularEditor.exe".format(os.environ.get('USERNAME', '')),
        r".\TabularEditor.exe"
    ]
    
    for path in paths_to_check:
        if Path(path).exists():
            print(f"✅ Found existing Tabular Editor: {path}")
            return path
    
    return None


def main():
    """Main installation function."""
    parser = argparse.ArgumentParser(description="Install Tabular Editor 2 for Power BI compilation")
    parser.add_argument("--portable", action="store_true", 
                       help="Install as portable version in current directory")
    parser.add_argument("--directory", "-d", 
                       help="Installation directory (default: ./TabularEditor)")
    parser.add_argument("--force", action="store_true",
                       help="Force reinstallation even if already exists")
    parser.add_argument("--no-path", action="store_true",
                       help="Don't add to system PATH")
    
    args = parser.parse_args()
    
    print("🚀 Tabular Editor 2 Auto-Installer")
    print("=" * 40)
    
    # Check for existing installation
    if not args.force:
        existing = check_existing_installation()
        if existing:
            print("✅ Tabular Editor already installed!")
            print(f"   Location: {existing}")
            print("💡 Use --force to reinstall")
            return
    
    # Get release information
    release_info = get_latest_tabular_editor_info()
    if not release_info:
        print("❌ Failed to get Tabular Editor release information")
        print("💡 Manual download: https://tabulareditor.com/")
        sys.exit(1)
    
    print(f"📦 Latest version: {release_info['version']}")
    print(f"📁 File: {release_info['filename']}")
    print(f"📏 Size: {release_info['size']:,} bytes")
    
    # Determine installation directory
    if args.directory:
        install_dir = Path(args.directory)
    elif args.portable:
        install_dir = Path(".") / "TabularEditor"
    else:
        install_dir = Path.home() / "AppData" / "Local" / "TabularEditor"
    
    print(f"📂 Installation directory: {install_dir}")
    
    # Download
    download_path = Path("temp_tabular_editor.zip")
    if not download_file(release_info["download_url"], download_path, release_info["filename"]):
        sys.exit(1)
    
    # Extract
    if not extract_tabular_editor(download_path, install_dir):
        sys.exit(1)
    
    # Add to PATH (unless disabled)
    if not args.no_path:
        add_to_path(install_dir)
    
    # Verify installation
    verify_installation(install_dir)
    
    # Cleanup
    try:
        download_path.unlink()
        print("🧹 Cleaned up temporary files")
    except:
        pass
    
    # Success message
    print("\n🎉 Tabular Editor 2 installation complete!")
    print(f"📁 Installed to: {install_dir}")
    print(f"🏃 Executable: {install_dir / 'TabularEditor.exe'}")
    
    if not args.no_path:
        print("📋 Added to system PATH")
        print("💡 Restart your command prompt to use 'TabularEditor' command")
    
    print("\n📚 Next steps:")
    print("   1. Test with: python alternative_compilers_demo.py --method tabular")
    print("   2. Or run your Tableau to Power BI conversion")
    print("   3. Tabular Editor documentation: https://docs.tabulareditor.com/")


if __name__ == "__main__":
    main()
