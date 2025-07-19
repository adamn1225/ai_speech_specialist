#!/bin/bash

# Speech Coach Build Script
# This script creates a distributable executable for Speech Coach

echo "🚀 Building Speech Coach Application..."

# Activate virtual environment
source .venv/bin/activate

# Check if whisper model exists
if [ ! -f "whisper.cpp/models/ggml-base.en.bin" ]; then
    echo "⚠️  Warning: Whisper model not found. Users will need to download it."
    echo "   Run: cd whisper.cpp && bash ./models/download-ggml-model.sh base.en"
fi

# Build the application
echo "📦 Creating executable with PyInstaller..."
pyinstaller speech_coach.spec --clean

# Create distribution folder
echo "📁 Creating distribution package..."
mkdir -p dist/SpeechCoach_Distribution

# Copy executable
cp dist/SpeechCoach dist/SpeechCoach_Distribution/

# Create installation instructions
cat > dist/SpeechCoach_Distribution/README.txt << 'EOF'
🎤 Speech Coach - Professional Communication Trainer
===================================================

INSTALLATION INSTRUCTIONS:
1. Extract this folder to your desired location
2. Run the 'SpeechCoach' executable
3. (Optional) Download Whisper model for better performance:
   - Visit: https://github.com/ggerganov/whisper.cpp
   - Download the base.en model
   - Place in whisper.cpp/models/ folder

SYSTEM REQUIREMENTS:
- Linux (Ubuntu 20.04+ recommended)
- Audio input device (microphone)
- 4GB RAM minimum, 8GB recommended
- 2GB free disk space

FEATURES:
✅ Real-time speech analysis
✅ Professional communication scoring
✅ Practice lessons and exercises
✅ Session tracking and progress monitoring
✅ Dark theme interface

For support or issues, visit: https://github.com/yourusername/speech-coach

Enjoy improving your communication skills! 🎯
EOF

# Create a simple launcher script
cat > dist/SpeechCoach_Distribution/run_speech_coach.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./SpeechCoach
EOF

chmod +x dist/SpeechCoach_Distribution/run_speech_coach.sh

echo "✅ Build complete!"
echo "📦 Distribution package created in: dist/SpeechCoach_Distribution/"
echo ""
echo "Next steps:"
echo "1. Test the executable: ./dist/SpeechCoach_Distribution/SpeechCoach"
echo "2. Create a .tar.gz archive: tar -czf SpeechCoach-v1.0-linux.tar.gz -C dist SpeechCoach_Distribution"
echo "3. Upload to GitHub Releases for easy download"
