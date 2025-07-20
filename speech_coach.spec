# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add src directory to the path for PyInstaller
src_path = str(Path('.').absolute() / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.', 'src'],
    binaries=[
        # Include whisper binary if it exists (optional)
    ],
    datas=[
        # Include any resource files that exist
        ('README.md', '.'),
        ('VERSION', '.'),
        ('assets/*', 'assets'),
        ('src/ui/*.py', 'ui'),
        ('src/audio/*.py', 'audio'),
        ('src/analysis/*.py', 'analysis'),
        ('src/lessons/*.py', 'lessons'),
        ('src/cloud/*.py', 'cloud'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'ui',
        'ui.main_window',
        'ui.dashboard_widget',
        'ui.settings_widget',
        'ui.lessons_widget',
        'ui.real_time_widget',
        'audio',
        'audio.audio_manager',
        'analysis',
        'analysis.speech_analyzer',
        'analysis.metrics',
        'lessons',
        'lessons.lesson_manager',
        'cloud',
        'cloud.api_client',
        'pyaudio',
        'numpy',
        'librosa',
        'parselmouth',
        'pulsectl',
        'openai',
        'requests',
        'collections',
        'datetime',
        'logging',
        'pathlib',
        'typing',
        'scipy',
        'scikit-learn',
        'soundfile',
        'soxr',
        'numba',
        'joblib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpeechCoach',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/speech_coach_icon.ico',  # Windows icon
    manifest='speech_coach.manifest',  # Windows manifest for proper app behavior
    version='version_info.txt',  # Windows version information
)
