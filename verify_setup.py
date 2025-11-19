#!/usr/bin/env python3
"""
Final Verification Script - Confirms all files are in place
Run this on your Mac or any computer to verify the setup package is complete
"""

import os
import sys

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"{GREEN}✓{END} {description}")
        if size > 0:
            print(f"  └─ {size} bytes")
        return True
    else:
        print(f"{RED}✗{END} {description}")
        return False

def check_directory(path, description):
    """Check if a directory exists"""
    if os.path.isdir(path):
        files = len(os.listdir(path))
        print(f"{GREEN}✓{END} {description}")
        print(f"  └─ {files} items inside")
        return True
    else:
        print(f"{RED}✗{END} {description}")
        return False

def main():
    print("\n" + "="*70)
    print(f"{BLUE}VOICE ASSISTANT SETUP VERIFICATION{END}")
    print("="*70 + "\n")
    
    base_path = "/Users/tusharbhaliya/Desktop/AI/respeaker-ai"
    
    if not os.path.exists(base_path):
        print(f"{RED}ERROR: Project directory not found at {base_path}{END}")
        sys.exit(1)
    
    print(f"{BLUE}Checking files in: {base_path}{END}\n")
    
    all_good = True
    
    # Check main program
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}MAIN PROGRAM{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_file(
        os.path.join(base_path, "hello_ai_pi_custom.py"),
        "hello_ai_pi_custom.py (optimized for ReSpeaker)"
    )
    print()
    
    # Check test files
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}TEST & DIAGNOSTIC SCRIPTS{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_file(
        os.path.join(base_path, "test_respeaker_setup.py"),
        "test_respeaker_setup.py (hardware verification)"
    )
    all_good &= check_file(
        os.path.join(base_path, "test_tts.py"),
        "test_tts.py (speaker test)"
    )
    all_good &= check_file(
        os.path.join(base_path, "test_tts_improved.py"),
        "test_tts_improved.py (advanced speaker test)"
    )
    print()
    
    # Check documentation
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}DOCUMENTATION{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_file(
        os.path.join(base_path, "00_START_HERE_RASPBERRY_PI.md"),
        "00_START_HERE_RASPBERRY_PI.md ⭐ START HERE!"
    )
    all_good &= check_file(
        os.path.join(base_path, "COMPLETE_SUMMARY.md"),
        "COMPLETE_SUMMARY.md (complete overview)"
    )
    all_good &= check_file(
        os.path.join(base_path, "QUICK_START.md"),
        "QUICK_START.md (3-minute guide)"
    )
    all_good &= check_file(
        os.path.join(base_path, "RASPBERRY_PI_SETUP_CUSTOM.md"),
        "RASPBERRY_PI_SETUP_CUSTOM.md (detailed setup)"
    )
    all_good &= check_file(
        os.path.join(base_path, "SETUP_CHECKLIST.md"),
        "SETUP_CHECKLIST.md (track progress)"
    )
    all_good &= check_file(
        os.path.join(base_path, "TROUBLESHOOTING.md"),
        "TROUBLESHOOTING.md (fix problems)"
    )
    all_good &= check_file(
        os.path.join(base_path, "FILE_OVERVIEW.md"),
        "FILE_OVERVIEW.md (complete file reference)"
    )
    all_good &= check_file(
        os.path.join(base_path, "SYSTEM_ARCHITECTURE.md"),
        "SYSTEM_ARCHITECTURE.md (architecture diagrams)"
    )
    print()
    
    # Check models
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}SPEECH RECOGNITION MODELS{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_directory(
        os.path.join(base_path, "models"),
        "models/ (directory for speech models)"
    )
    all_good &= check_directory(
        os.path.join(base_path, "models", "en"),
        "models/en/ (English speech model)"
    )
    print()
    
    # Check virtual environment
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}PYTHON VIRTUAL ENVIRONMENT{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_directory(
        os.path.join(base_path, "venv"),
        "venv/ (Python virtual environment)"
    )
    all_good &= check_file(
        os.path.join(base_path, "venv", "bin", "python"),
        "venv/bin/python (Python interpreter)"
    )
    print()
    
    # Check other files
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}OTHER FILES & SCRIPTS{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    all_good &= check_file(
        os.path.join(base_path, "install_rpi.sh"),
        "install_rpi.sh (automated installer)"
    )
    all_good &= check_file(
        os.path.join(base_path, "requirements_rpi.txt"),
        "requirements_rpi.txt (Python dependencies)"
    )
    print()
    
    # Summary
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}")
    print(f"{BLUE}VERIFICATION SUMMARY{END}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}\n")
    
    if all_good:
        print(f"{GREEN}✓ ALL FILES VERIFIED SUCCESSFULLY!{END}\n")
        print(f"{BLUE}Your voice assistant package is complete.{END}\n")
        print("Next steps:")
        print("1. Copy this folder to your Raspberry Pi")
        print("2. Read: 00_START_HERE_RASPBERRY_PI.md")
        print("3. Follow the setup instructions")
        print("4. Run: python3 hello_ai_pi_custom.py\n")
    else:
        print(f"{RED}✗ SOME FILES ARE MISSING!{END}\n")
        print("Please ensure all files were created properly.")
        print("Check the red X marks above.\n")
    
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{END}\n")
    
    # Show directory structure
    print(f"{BLUE}Directory Structure:{END}\n")
    os.system(f"ls -la {base_path} | grep -E '^-|^d' | head -20")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
