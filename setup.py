#!/usr/bin/env python3
"""
Quick setup script for MLB YRFI/NRFI Predictor Dashboard
Helps users get started with GitHub Pages deployment.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{description} completed successfully")
            return True
        else:
            print(f"{description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"{description} failed: {str(e)}")
        return False

def check_git_repo():
    """Check if we're in a git repository."""
    return os.path.exists('.git')

def main():
    print("MLB YRFI/NRFI Predictor Dashboard Setup")
    print("=" * 50)
    
    # Check if in project directory
    if not os.path.exists('generate_static_site.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        sys.exit(1)
    
    print("Python version check passed")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Dependency installation failed. Please install manually:")
        print("   pip install -r requirements.txt")
    
    # Setup database
    if not run_command("python setup_database.py", "Setting up database"):
        print("Database setup failed")
    
    # Generate initial static site
    if not run_command("python generate_static_site.py", "Generating initial dashboard"):
        print("Static site generation failed")
    
    # Check if git repo exists
    if not check_git_repo():
        print("\n📋 Next Steps:")
        print("1. Initialize git repository: git init")
        print("2. Add files: git add .")
        print("3. Commit: git commit -m 'Initial commit'")
        print("4. Push to GitHub")
        print("5. Enable GitHub Pages in repository settings")
    else:
        print("Git repository detected")
        
        # Check if docs folder exists
        if os.path.exists('docs/index.html'):
            print("Static site files ready in docs/ folder")
            print("\nFinal Steps:")
            print("1. Push to GitHub: git add . ; git commit -m 'Setup dashboard' ; git push")
            print("2. Go to GitHub repo Settings → Pages")
            print("3. Set Source to 'Deploy from a branch'")
            print("4. Set Branch to 'main' and Folder to '/docs'")
            print("5. Save and wait for deployment")
            print("\nYour dashboard will be live at:")
            print("   https://yourusername.github.io/your-repo-name")
        else:
            print("Static site files not found in docs/ folder")
    
    print("\nDashboard Features:")
    print("• Daily auto-updates at 6 AM EST")
    print("• Mobile-responsive design")
    print("• Real-time MLB data")
    print("• Confidence-based predictions")
    print("• Zero maintenance required")
    
    print("\nNeed help? Check README.md for troubleshooting")

if __name__ == "__main__":
    main()
