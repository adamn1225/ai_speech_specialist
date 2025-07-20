#!/bin/bash

# Speech Coach Easy Installer
# This script sets up Speech Coach with minimal user intervention

set -e

echo "🎤 Speech Coach Installer"
echo "========================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "   Please install python3-pip and try again."
    exit 1
fi

echo "✅ Found pip3"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv speech_coach_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source speech_coach_env/bin/activate

# Install compatible dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip

# Install core GUI framework first
pip install PyQt5>=5.15.0

# Install audio dependencies
pip install PyAudio>=0.2.11 soundfile>=0.10.0 pulsectl

# Install analysis dependencies  
pip install numpy scipy librosa praat-parselmouth scikit-learn

# Install API dependencies
pip install requests openai

echo "✅ Installation complete!"
echo ""
echo "🚀 To run Speech Coach:"
echo "   1. cd $(pwd)"
echo "   2. source speech_coach_env/bin/activate"
echo "   3. python main.py"
echo ""
echo "📝 A desktop shortcut will be created for easier access."

# Create desktop shortcut
DESKTOP_FILE="$HOME/Desktop/SpeechCoach.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Speech Coach
Comment=Professional Communication Trainer
Exec=bash -c 'cd $(pwd) && source speech_coach_env/bin/activate && python main.py'
Icon=$(pwd)/assets/icon.png
Terminal=false
Categories=AudioVideo;Audio;
EOF

chmod +x "$DESKTOP_FILE"

echo "🎯 Desktop shortcut created: $DESKTOP_FILE"
echo ""
echo "Happy practicing! 🎤"
