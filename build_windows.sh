#!/bin/bash

# Speech Coach Windows Build Script
# Builds Windows executable and installer from Linux

echo "🪟 Building Speech Coach for Windows..."

# Activate virtual environment
source .venv/bin/activate

# Check if we have Wine installed for Windows builds
if ! command -v wine &> /dev/null; then
    echo "⚠️  Wine not found. Installing Wine for Windows builds..."
    echo "Run: sudo apt update && sudo apt install wine"
    echo "Then run this script again."
    exit 1
fi

# Create a simple placeholder icon if it doesn't exist
if [ ! -f "assets/speech_coach_icon.ico" ]; then
    echo "🎨 Creating placeholder icon..."
    # Create a simple 32x32 ICO file (you should replace this with a proper icon)
    cat > assets/speech_coach_icon.ico << 'EOF'
# This is a placeholder - replace with a proper .ico file
# You can create one at https://favicon.io/favicon-generator/
# Or use any online ICO converter
EOF
    echo "⚠️  Using placeholder icon. Replace assets/speech_coach_icon.ico with a proper icon!"
fi

# Build Windows executable
echo "📦 Building Windows executable with PyInstaller..."

# Method 1: Cross-compile (may have issues with some dependencies)
echo "🔧 Attempting cross-compilation..."
pyinstaller speech_coach_windows.spec --clean --distpath dist/windows

# Check if build was successful
if [ -f "dist/windows/SpeechCoach.exe" ]; then
    echo "✅ Windows executable built successfully!"
    
    # Create Windows distribution folder
    echo "📁 Creating Windows distribution package..."
    mkdir -p dist/SpeechCoach_Windows
    
    # Copy executable and documentation
    cp dist/windows/SpeechCoach.exe dist/SpeechCoach_Windows/
    cp README.md dist/SpeechCoach_Windows/
    cp DISTRIBUTION.md dist/SpeechCoach_Windows/
    
    # Create Windows installation instructions
    cat > dist/SpeechCoach_Windows/INSTALL_WINDOWS.txt << 'EOF'
🎤 Speech Coach - Windows Installation
=====================================

QUICK START:
1. Double-click SpeechCoach.exe to run the application
2. Windows may show a security warning - click "More info" then "Run anyway"
3. Allow microphone access when prompted

DESKTOP SHORTCUT:
1. Right-click SpeechCoach.exe → "Send to" → "Desktop (create shortcut)"
2. Rename the shortcut to "Speech Coach"

SYSTEM REQUIREMENTS:
- Windows 10 or 11 (64-bit)
- 4GB RAM minimum, 8GB recommended
- Microphone/audio input device
- 500MB free disk space

FEATURES:
✅ Real-time speech analysis
✅ Professional communication scoring
✅ Practice lessons and exercises
✅ Session tracking and progress monitoring
✅ Modern dark theme interface

TROUBLESHOOTING:
- If Windows Defender blocks the app, add an exception
- Ensure microphone permissions are granted
- Run as Administrator if audio issues occur

For support: https://github.com/yourusername/speech-coach/issues

Enjoy improving your communication skills! 🎯
EOF
    
    # Create a batch file for easy launching
    cat > dist/SpeechCoach_Windows/run_speech_coach.bat << 'EOF'
@echo off
echo Starting Speech Coach...
SpeechCoach.exe
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to close.
    pause > nul
)
EOF
    
    # Create ZIP archive for distribution
    echo "📦 Creating Windows distribution archive..."
    cd dist
    zip -r "../SpeechCoach-v1.0-windows.zip" SpeechCoach_Windows/
    cd ..
    
    echo "✅ Windows build complete!"
    echo "📦 Distribution created: SpeechCoach-v1.0-windows.zip"
    echo ""
    echo "📋 Files created:"
    echo "- dist/SpeechCoach_Windows/SpeechCoach.exe (main application)"
    echo "- SpeechCoach-v1.0-windows.zip (distribution archive)"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Test SpeechCoach.exe on a Windows machine"
    echo "2. Replace assets/speech_coach_icon.ico with a proper icon"
    echo "3. Consider creating an NSIS installer for professional distribution"
    echo "4. Upload to GitHub Releases"
    
else
    echo "❌ Windows build failed!"
    echo ""
    echo "🔧 Alternative approach - Manual Windows Build:"
    echo "1. Copy your project to a Windows machine"
    echo "2. Install Python 3.11+ on Windows"
    echo "3. Run: pip install -r requirements.txt"
    echo "4. Run: pip install pyinstaller"
    echo "5. Run: pyinstaller speech_coach_windows.spec"
    echo ""
    echo "💡 Or use GitHub Actions for automated Windows builds"
fi

# Build installer (requires NSIS on Windows)
echo ""
echo "🛠️  To create a Windows installer:"
echo "1. Install NSIS on Windows (https://nsis.sourceforge.io/)"
echo "2. Copy speech_coach_installer.nsi to Windows"
echo "3. Right-click speech_coach_installer.nsi → 'Compile NSIS Script'"
echo "4. This creates: SpeechCoach-v1.0-windows-installer.exe"
