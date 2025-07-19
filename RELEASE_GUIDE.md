# 🏷️ Release Process Guide

## What Happens When You Create a Release Tag?

### **Step 1: You Create a Tag**
```bash
# Either manually:
git tag v1.0.0
git push origin v1.0.0

# Or using the script:
./create_release.sh
```

### **Step 2: GitHub Actions Triggers**
The workflow in `.github/workflows/build-releases.yml` automatically:

1. **Detects the new tag** (anything starting with 'v')
2. **Spins up virtual machines**:
   - Windows Server (for .exe build)
   - Ubuntu Linux (for Linux build)

### **Step 3: Automated Building**
**On Windows VM:**
- Installs Python 3.11
- Installs your dependencies
- Runs PyInstaller with Windows spec
- Creates `SpeechCoach.exe`
- Packages as `SpeechCoach-windows.zip`

**On Linux VM:**
- Installs system dependencies
- Installs Python dependencies
- Builds Linux executable
- Creates `SpeechCoach-linux.tar.gz`

### **Step 4: Release Creation**
- Creates GitHub Release page
- Uploads both Windows and Linux packages
- Adds professional release notes
- Makes downloads available to users

## 📅 **Release Versioning**

### **Semantic Versioning (Recommended)**
- `v1.0.0` - Major release (big features)
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

### **Examples**
```bash
v1.0.0    # Initial release
v1.0.1    # Bug fix
v1.1.0    # Added new lesson types
v2.0.0    # Major UI redesign
```

## 🎯 **For Non-Technical Users**

When you create `v1.0.0`, your users will see:

**GitHub Releases Page:**
```
📦 Speech Coach v1.0.0
Latest Release

Assets:
💾 SpeechCoach-windows.zip    (163 MB)
💾 SpeechCoach-linux.tar.gz   (165 MB)
```

**User Experience:**
1. Go to releases page
2. Download their platform's file
3. Extract and run
4. No installation needed!

## 🔧 **Before Your First Release**

1. **Test your app** works completely
2. **Replace placeholder icon** with real icon
3. **Update README.md** with screenshots
4. **Set up GitHub repository**
5. **Run the release script**: `./create_release.sh`

## 🚀 **Quick Start**

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial Speech Coach application"

# Push to GitHub
git remote add origin https://github.com/yourusername/speech-coach.git
git push -u origin main

# Create first release
./create_release.sh
# Enter: v1.0.0

# Wait 5-10 minutes, then check:
# https://github.com/yourusername/speech-coach/releases
```

That's it! 🎉 Your users can now download ready-to-run Windows and Linux versions!
