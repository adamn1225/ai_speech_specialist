#!/bin/bash

# Speech Coach Release Script
# Creates a new release with automatic Windows and Linux builds

echo "🚀 Speech Coach Release Creator"
echo "================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Run: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Get current version or ask for new version
echo "📋 Current git tags:"
git tag -l | sort -V | tail -5

echo ""
read -p "🏷️  Enter new version (e.g., v1.0.0): " VERSION

if [ -z "$VERSION" ]; then
    echo "❌ Version cannot be empty"
    exit 1
fi

# Validate version format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must be in format v1.0.0"
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$VERSION$"; then
    echo "❌ Tag $VERSION already exists"
    exit 1
fi

echo ""
echo "📝 Creating release $VERSION..."

# Ensure we're on main/master branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    read -p "⚠️  Not on main/master branch. Continue? (y/N): " CONTINUE
    if [[ $CONTINUE != "y" ]]; then
        exit 1
    fi
fi

# Commit any pending changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "📝 Committing pending changes..."
    git add .
    git commit -m "Prepare release $VERSION"
fi

# Create and push tag
echo "🏷️  Creating tag $VERSION..."
git tag -a $VERSION -m "Release $VERSION

✨ Features:
- Real-time speech analysis
- Professional communication scoring
- Practice lessons and exercises
- Session tracking and progress monitoring
- Modern dark theme interface
- Cross-platform support (Windows & Linux)

🔧 Technical:
- PyQt6 GUI framework
- PyAudio for real-time audio capture
- Whisper.cpp for speech transcription
- OpenAI API integration
- Standalone executables (no Python required)

📦 Installation:
- Windows: Download SpeechCoach-windows.zip
- Linux: Download SpeechCoach-linux.tar.gz

🐛 Report issues: https://github.com/yourusername/speech-coach/issues"

echo "📤 Pushing tag to GitHub..."
git push origin $VERSION

echo ""
echo "✅ Release $VERSION created successfully!"
echo ""
echo "🔄 GitHub Actions will now:"
echo "   1. Build Windows executable (.exe)"
echo "   2. Build Linux executable"
echo "   3. Create distribution packages"
echo "   4. Upload to GitHub Releases"
echo ""
echo "🌐 View progress at:"
echo "   https://github.com/yourusername/speech-coach/actions"
echo ""
echo "📦 Release will be available at:"
echo "   https://github.com/yourusername/speech-coach/releases/tag/$VERSION"
echo ""
echo "⏱️  Build time: ~5-10 minutes"
