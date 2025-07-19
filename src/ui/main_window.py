"""
Main Window for Speech Coach Application
"""

import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QFrame, QStatusBar,
    QMenuBar, QMenu, QMessageBox, QProgressBar
)
from typing import Optional
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPalette

from .dashboard_widget import DashboardWidget
from .lessons_widget import LessonsWidget
from .settings_widget import SettingsWidget
from .real_time_widget import RealTimeWidget
from audio.audio_manager import AudioManager
from analysis.speech_analyzer import SpeechAnalyzer

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    # Signals
    audio_analysis_updated = pyqtSignal(dict)  # Emits analysis results
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.audio_manager = AudioManager()
        self.speech_analyzer = SpeechAnalyzer()
        
        # UI state
        self.is_recording = False
        
        self.init_ui()
        self.setup_connections()
        self.setup_status_updates()
        
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Speech Coach - Professional Communication Trainer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set application icon (placeholder)
        self.setWindowIcon(QIcon())
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.dashboard_widget = DashboardWidget()
        self.real_time_widget = RealTimeWidget()
        self.lessons_widget = LessonsWidget()
        self.settings_widget = SettingsWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.dashboard_widget, "📊 Dashboard")
        self.tab_widget.addTab(self.real_time_widget, "🎤 Real-Time Analysis")
        self.tab_widget.addTab(self.lessons_widget, "📚 Practice Lessons")
        self.tab_widget.addTab(self.settings_widget, "⚙️ Settings")
        
        # Create status bar
        self.create_status_bar()
        
        # Apply styling
        self.apply_styling()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        if menubar is None:
            logger.warning("Could not create menu bar")
            return
        
        # File menu
        file_menu = menubar.addMenu('File')
        if file_menu is None:
            logger.warning("Could not create File menu")
            return
        
        new_session_action = QAction('New Session', self)
        new_session_action.setShortcut('Ctrl+N')
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        if tools_menu is None:
            logger.warning("Could not create Tools menu")
            return
        
        calibrate_action = QAction('Calibrate Audio', self)
        calibrate_action.triggered.connect(self.calibrate_audio)
        tools_menu.addAction(calibrate_action)
        
        test_whisper_action = QAction('Test Whisper', self)
        test_whisper_action.triggered.connect(self.test_whisper)
        tools_menu.addAction(test_whisper_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        if help_menu is None:
            logger.warning("Could not create Help menu")
            return
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Create the status bar with indicators."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status indicators
        self.audio_status = QLabel("Audio: Ready")
        self.whisper_status = QLabel("Whisper: Ready")
        self.openai_status = QLabel("OpenAI: Disconnected")
        
        # Progress bar for processing
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        
        # Add to status bar
        self.status_bar.addWidget(self.audio_status)
        self.status_bar.addPermanentWidget(self.whisper_status)
        self.status_bar.addPermanentWidget(self.openai_status)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready")
    
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connect audio manager signals
        self.audio_manager.audio_data_ready.connect(self.process_audio_data)
        self.audio_manager.error_occurred.connect(self.handle_audio_error)
        
        # Connect real-time widget signals
        self.real_time_widget.start_recording.connect(self.start_real_time_analysis)
        self.real_time_widget.stop_recording.connect(self.stop_real_time_analysis)
        
        # Connect settings changes
        self.settings_widget.settings_changed.connect(self.update_settings)
    
    def setup_status_updates(self):
        """Set up periodic status updates."""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def apply_styling(self):
        """Apply custom styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #555555;
            }
            QTabBar::tab:selected {
                background-color: #3c3c3c;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QStatusBar {
                background-color: #404040;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
            QWidget {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #505050;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QGroupBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #ffffff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QScrollArea {
                background-color: #3c3c3c;
                border: 1px solid #555555;
            }
        """)
    
    def process_audio_data(self, audio_data):
        """Process incoming audio data."""
        if not self.is_recording:
            return
        
        try:
            # Update progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(25)
            
            # Analyze speech
            analysis_result = self.speech_analyzer.analyze_audio(audio_data)
            
            self.progress_bar.setValue(75)
            
            # Update UI with results
            self.real_time_widget.update_analysis(analysis_result)
            self.dashboard_widget.add_data_point(analysis_result)
            
            # Emit signal for other components
            self.audio_analysis_updated.emit(analysis_result)
            
            self.progress_bar.setValue(100)
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            logger.error(f"Error processing audio data: {e}")
            self.handle_error(f"Audio processing error: {e}")
    
    def start_real_time_analysis(self):
        """Start real-time audio analysis."""
        try:
            self.audio_manager.start_recording()
            self.is_recording = True
            self.status_bar.showMessage("Recording and analyzing...")
            self.audio_status.setText("Audio: Recording")
            logger.info("Started real-time analysis")
            
        except Exception as e:
            logger.error(f"Error starting real-time analysis: {e}")
            self.handle_error(f"Could not start recording: {e}")
    
    def stop_real_time_analysis(self):
        """Stop real-time audio analysis."""
        try:
            self.audio_manager.stop_recording()
            self.is_recording = False
            self.status_bar.showMessage("Ready")
            self.audio_status.setText("Audio: Ready")
            logger.info("Stopped real-time analysis")
            
        except Exception as e:
            logger.error(f"Error stopping real-time analysis: {e}")
            self.handle_error(f"Could not stop recording: {e}")
    
    def update_settings(self, settings):
        """Update application settings."""
        # Update audio manager settings
        self.audio_manager.update_settings(settings.get('audio', {}))
        
        # Update speech analyzer settings
        self.speech_analyzer.update_settings(settings.get('analysis', {}))
        
        logger.info("Settings updated")
    
    def update_status(self):
        """Update status indicators."""
        # Check audio system
        if self.audio_manager.is_available():
            self.audio_status.setText("Audio: Ready")
            self.audio_status.setStyleSheet("color: green")
        else:
            self.audio_status.setText("Audio: Error")
            self.audio_status.setStyleSheet("color: red")
        
        # Check Whisper
        if self.speech_analyzer.is_whisper_available():
            self.whisper_status.setText("Whisper: Ready")
            self.whisper_status.setStyleSheet("color: green")
        else:
            self.whisper_status.setText("Whisper: Error")
            self.whisper_status.setStyleSheet("color: red")
        
        # Check OpenAI connection
        if self.settings_widget.is_openai_connected():
            self.openai_status.setText("OpenAI: Connected")
            self.openai_status.setStyleSheet("color: green")
        else:
            self.openai_status.setText("OpenAI: Disconnected")
            self.openai_status.setStyleSheet("color: orange")
    
    def handle_audio_error(self, error_message):
        """Handle audio system errors."""
        logger.error(f"Audio error: {error_message}")
        self.handle_error(f"Audio system error: {error_message}")
    
    def handle_error(self, message):
        """Handle general errors."""
        QMessageBox.warning(self, "Error", message)
        self.status_bar.showMessage(f"Error: {message}", 5000)
    
    # Menu actions
    def new_session(self):
        """Start a new analysis session."""
        self.dashboard_widget.clear_data()
        self.status_bar.showMessage("New session started", 2000)
    
    def calibrate_audio(self):
        """Calibrate audio input."""
        # TODO: Implement audio calibration
        QMessageBox.information(self, "Calibration", "Audio calibration feature coming soon!")
    
    def test_whisper(self):
        """Test Whisper transcription."""
        try:
            result = self.speech_analyzer.test_whisper()
            QMessageBox.information(self, "Whisper Test", f"Whisper test successful!\n\nResult: {result}")
        except Exception as e:
            QMessageBox.warning(self, "Whisper Test", f"Whisper test failed:\n\n{e}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Speech Coach", 
                         "Speech Coach v1.0.0\n\n"
                         "Professional communication trainer for sales professionals.\n\n"
                         "Features real-time speech analysis, practice lessons, "
                         "and AI-powered feedback using OpenAI Whisper and GPT models.")
    
    def closeEvent(self, event):
        """Handle application closing."""
        # Stop any ongoing recording
        if self.is_recording:
            self.stop_real_time_analysis()
        
        # Clean up resources
        self.audio_manager.cleanup()
        
        logger.info("Application closing")
        event.accept()
