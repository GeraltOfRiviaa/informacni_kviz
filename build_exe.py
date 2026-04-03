"""
Build Script for Creating Standalone Executable using PyInstaller

This script creates a standalone application that can be distributed without Python.

Usage:
    python build_exe.py
    
Requirements:
    pip install pyinstaller
"""

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path


class PyInstallerBuilder:
    """Handles PyInstaller build process for Informační Kvíz."""
    
    def __init__(self, onefile: bool = False, clean: bool = True):
        self.root_dir = Path(__file__).parent
        self.dist_dir = self.root_dir / "dist"
        self.build_dir = self.root_dir / "build"
        self.spec_dir = self.root_dir
        self.main_file = self.root_dir / "main.py"
        self.onefile = onefile
        self.clean = clean
        
    def clean_previous_builds(self):
        """Remove previous builds."""
        if not self.clean:
            print("[1/5] Cleaning previous builds... skipped")
            return

        print("[1/5] Cleaning previous builds...")
        for directory in [self.dist_dir, self.build_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"  ✓ Removed {directory.name}/")

        spec_file = self.root_dir / "informacni_kviz.spec"
        if spec_file.exists():
            spec_file.unlink()
            print("  ✓ Removed informacni_kviz.spec")
    
    def check_dependencies(self):
        """Check if PyInstaller is installed."""
        print("[2/5] Checking dependencies...")
        try:
            import PyInstaller
            print(f"  ✓ PyInstaller found (v{PyInstaller.__version__})")
        except ImportError:
            print("  ✗ PyInstaller not found!")
            print("\nInstall with: pip install pyinstaller")
            sys.exit(1)
    
    def create_build_command(self):
        """Build PyInstaller command."""
        print("[3/5] Building PyInstaller command...")
        
        # Hidden imports needed
        hidden_imports = [
            "PIL",
            "PIL.Image",
            "PIL.ImageFilter",
            "cryptography",
            "services.answer_checker",
            "services.hint_system",
            "services.image_handler",
            "services.question_loader",
            "services.round_manager",
            "services.score_manager",
            "services.timer_service",
        ]
        
        # Data files to include
        datas = [
            (str(self.root_dir / "data"), "data"),
            (str(self.root_dir / "assets"), "assets"),
            (str(self.root_dir / "docs"), "docs"),
        ]
        
        # Build command
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile" if self.onefile else "--onedir",
            "--windowed",  # No console window
            "--name=informacni_kviz",
            "--icon=assets/icon.ico" if (self.root_dir / "assets" / "icon.ico").exists() else "",
        ]

        # Add data mappings (one --add-data per mapping)
        for src, dst in datas:
            cmd.append(f"--add-data={src}{os.pathsep}{dst}")
        
        # Add hidden imports
        for imp in hidden_imports:
            cmd.append(f"--hidden-import={imp}")
        
        # Add the main file
        cmd.append(str(self.main_file))
        
        # Remove empty strings
        cmd = [c for c in cmd if c]
        
        print(f"  Command: {' '.join(cmd[:5])}...")
        return cmd
    
    def run_pyinstaller(self, cmd):
        """Execute PyInstaller."""
        print("[4/5] Running PyInstaller (this may take 1-2 minutes)...")
        try:
            result = subprocess.run(cmd, cwd=str(self.root_dir))
            if result.returncode == 0:
                print("  ✓ PyInstaller succeeded")
                return True
            else:
                print(f"  ✗ PyInstaller failed with code {result.returncode}")
                return False
        except Exception as e:
            print(f"  ✗ Error running PyInstaller: {e}")
            return False
    
    def create_distribution_package(self):
        """Create distribution package."""
        print("[5/5] Creating distribution package...")

        if self.onefile:
            exe_path = self.dist_dir / "informacni_kviz.exe"
            if not exe_path.exists():
                print("  ✗ Build executable not found!")
                return False

            dist_app = self.dist_dir / "informacni_kviz"
            if dist_app.exists():
                shutil.rmtree(dist_app)
            dist_app.mkdir(parents=True, exist_ok=True)

            shutil.copy2(exe_path, dist_app / "informacni_kviz.exe")
            print("  ✓ Copied informacni_kviz.exe")
        else:
            dist_app = self.dist_dir / "informacni_kviz"
            if not dist_app.exists():
                print("  ✗ Build directory not found!")
                return False
        
        # Copy README to dist
        readme_src = self.root_dir / "README.md"
        readme_dst = dist_app / "README.md"
        if readme_src.exists():
            shutil.copy(readme_src, readme_dst)
            print(f"  ✓ Copied README.md")
        
        # Copy ADMIN_GUIDE.md
        admin_guide_src = self.root_dir / "ADMIN_GUIDE.md"
        admin_guide_dst = dist_app / "ADMIN_GUIDE.md"
        if admin_guide_src.exists():
            shutil.copy(admin_guide_src, admin_guide_dst)
            print(f"  ✓ Copied ADMIN_GUIDE.md")
        
        # Create a launch script (batch file for Windows)
        if sys.platform == "win32":
            launch_script = dist_app / "run.bat"
            launch_script.write_text(
                "@echo off\n"
                "cd /d %~dp0\n"
                "informacni_kviz.exe\n"
                "pause\n"
            )
            print(f"  ✓ Created run.bat")
        
        # Create ZIP archive
        zip_path = self.dist_dir / "informacni_kviz_v1.0.zip"
        print(f"\n  Creating archive: {zip_path.name}")
        shutil.make_archive(
            str(zip_path.with_suffix("")),
            "zip",
            self.dist_dir,
            "informacni_kviz"
        )
        print(f"  ✓ Archive created: {zip_path.name}")
        
        return True
    
    def print_summary(self):
        """Print build summary."""
        print("\n" + "="*60)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("="*60)

        exe_path = self.dist_dir / "informacni_kviz" / "informacni_kviz.exe"
        zip_path = self.dist_dir / "informacni_kviz_v1.0.zip"

        build_mode = "onefile" if self.onefile else "onedir"
        print(f"\nBuild mode: {build_mode}")
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nExecutable: {exe_path.name}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"Path: {exe_path.parent}")
        
        if zip_path.exists():
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            print(f"\nArchive: {zip_path.name}")
            print(f"Size: {size_mb:.1f} MB")
        
        print("\nTo distribute:")
        print(f"1. Zip the folder: {self.dist_dir / 'informacni_kviz'}")
        print(f"2. Or use the pre-created: {zip_path.name}")
        print(f"3. Extract and run: informacni_kviz.exe or run.bat")
        print("\n" + "="*60)
    
    def build(self):
        """Execute full build process."""
        print("\n" + "="*60)
        print("INFORMAČNÍ KVÍZ - Build Process")
        print("="*60 + "\n")
        
        self.clean_previous_builds()
        self.check_dependencies()
        cmd = self.create_build_command()
        
        if not self.run_pyinstaller(cmd):
            print("\n✗ Build FAILED!")
            sys.exit(1)
        
        if not self.create_distribution_package():
            print("\n⚠ Build succeeded but packaging failed")
            sys.exit(1)
        
        self.print_summary()
        print("\n✓ Ready for distribution!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build standalone executable for Informační Kvíz")
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build single-file executable and package it into dist/informacni_kviz/",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete previous build/dist artifacts before build",
    )
    args = parser.parse_args()

    try:
        builder = PyInstallerBuilder(onefile=args.onefile, clean=not args.no_clean)
        builder.build()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠ Build cancelled by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
