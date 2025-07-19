#!/usr/bin/env python3
"""
Speech Coach Application
Main entry point for the speech improvement desktop application.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('speech_coach.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Starting Speech Coach Application")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Speech Coach")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SpeechCoach")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Set up exception handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # Start application
    logger.info("Application started successfully")
    exit_code = app.exec()
    logger.info(f"Application exited with code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
