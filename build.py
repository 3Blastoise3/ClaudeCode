#!/usr/bin/env python3
"""
Build script for creating standalone executables.

Usage:
    python build.py           # Build for current platform
    python build.py --clean   # Clean build artifacts first
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_artifacts():
    """Remove build artifacts."""
    artifacts = ["build", "dist", "__pycache__"]
    root = Path(__file__).parent

    for artifact in artifacts:
        path = root / artifact
        if path.exists():
            print(f"Removing {path}")
            shutil.rmtree(path)

    # Clean .pyc files
    for pyc in root.rglob("*.pyc"):
        pyc.unlink()

    # Clean __pycache__ directories
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache)


def build_executable():
    """Build the standalone executable using PyInstaller."""
    root = Path(__file__).parent
    spec_file = root / "census_extract.spec"

    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}", file=sys.stderr)
        sys.exit(1)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"])

    # Run PyInstaller
    print("Building executable...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"],
        cwd=root
    )

    if result.returncode != 0:
        print("Build failed!", file=sys.stderr)
        sys.exit(1)

    # Report success
    dist_dir = root / "dist"
    if dist_dir.exists():
        executables = list(dist_dir.glob("census-extract*"))
        if executables:
            print(f"\nBuild successful! Executable at: {executables[0]}")
        else:
            print(f"\nBuild complete. Check {dist_dir} for output.")


def main():
    parser = argparse.ArgumentParser(description="Build census-extract executable")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--clean-only", action="store_true", help="Only clean, don't build")
    args = parser.parse_args()

    if args.clean or args.clean_only:
        clean_build_artifacts()

    if not args.clean_only:
        build_executable()


if __name__ == "__main__":
    main()
