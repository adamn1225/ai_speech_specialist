#!/usr/bin/env python3
"""
Simple Speech Coach - Minimal version for testing distribution
"""

import sys
import os
from pathlib import Path

# Try to import PyQt6, fall back to basic message if not available
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

def create_simple_gui():
    """Create a simple GUI application"""
    if not PYQT_AVAILABLE:
        print("❌ PyQt6 not available")
        return None
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("🎤 Speech Coach")
    window.setGeometry(100, 100, 600, 400)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Layout
    layout = QVBoxLayout(central_widget)
    
    # Title
    title = QLabel("🎤 Speech Coach")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("""
        QLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px;
        }
    """)
    layout.addWidget(title)
    
    # Subtitle
    subtitle = QLabel("Professional Communication Trainer")
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet("""
        QLabel {
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
    """)
    layout.addWidget(subtitle)
    
    # Status
    status = QLabel("✅ Application loaded successfully!")
    status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #27ae60;
            background-color: #d5f4e6;
            padding: 10px;
            border-radius: 5px;
            margin: 20px;
        }
    """)
    layout.addWidget(status)
    
    # Instructions
    instructions = QLabel("""
    This is a test build of Speech Coach.
    
    The full version includes:
    • Real-time speech analysis
    • Professional communication scoring
    • Practice lessons and exercises
    • AI-powered feedback
    """)
    instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
    instructions.setStyleSheet("""
        QLabel {
            font-size: 12px;
            color: #34495e;
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            margin: 20px;
        }
    """)
    layout.addWidget(instructions)
    
    # Close button
    close_btn = QPushButton("Close Application")
    close_btn.clicked.connect(window.close)
    close_btn.setStyleSheet("""
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
    """)
    layout.addWidget(close_btn)
    
    return app, window

def main():
    """Main entry point"""
    print("🚀 Starting Speech Coach...")
    print(f"📍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    if PYQT_AVAILABLE:
        print("✅ PyQt6 available - Starting GUI...")
        gui_result = create_simple_gui()
        if gui_result:
            app, window = gui_result
            window.show()
            return app.exec()
    else:
        print("❌ PyQt6 not available")
        print("📦 This is a minimal console version")
        print("\n🎤 Speech Coach - Console Mode")
        print("=" * 40)
        print("✅ Application loaded successfully!")
        print("\nFeatures (when full version is available):")
        print("• Real-time speech analysis")
        print("• Professional communication scoring") 
        print("• Practice lessons and exercises")
        print("• AI-powered feedback")
        print("\nPress Enter to exit...")
        input()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
