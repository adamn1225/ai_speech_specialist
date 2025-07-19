"""
Real-Time Analysis Widget for Speech Coach Application
Provides real-time speech monitoring and feedback
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QProgressBar, QTextEdit,
    QGroupBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AudioLevelMeter(QFrame):
    """Visual audio level indicator."""
    
    def __init__(self):
        super().__init__()
        self.audio_level = 0.0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the audio level meter UI."""
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #484848;
                color: #ffffff;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Level bar
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setTextVisible(False)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4CAF50, stop:0.7 #FF9800, stop:1 #F44336);
                border-radius: 4px;
            }
        """)
        
        audio_label = QLabel("Audio:")
        audio_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(audio_label)
        layout.addWidget(self.level_bar)
    
    def update_level(self, level: float):
        """Update the audio level (0.0 to 1.0)."""
        self.audio_level = max(0.0, min(1.0, level))
        self.level_bar.setValue(int(self.audio_level * 100))

class RealTimeScoreDisplay(QFrame):
    """Real-time score display with color coding."""
    
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.score = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the score display UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(120, 100)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Score
        self.score_label = QLabel("--")
        self.score_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score_label)
        
        self.update_display()
    
    def update_score(self, score: int):
        """Update the score and color coding."""
        self.score = max(0, min(100, score))
        self.update_display()
    
    def update_display(self):
        """Update the visual display."""
        self.score_label.setText(str(self.score))
        
        # Dark theme color coding
        if self.score >= 80:
            bg_color = "#2d4a2d"  # Dark green
            text_color = "#4CAF50"  # Bright green
            border_color = "#4CAF50"
        elif self.score >= 60:
            bg_color = "#4a3a2d"  # Dark orange
            text_color = "#FF9800"  # Bright orange
            border_color = "#FF9800"
        else:
            bg_color = "#4a2d2d"  # Dark red
            text_color = "#F44336"  # Bright red
            border_color = "#F44336"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: #ffffff;
            }}
        """)
        self.score_label.setStyleSheet(f"color: {text_color};")

class TranscriptionDisplay(QGroupBox):
    """Live transcription display."""
    
    def __init__(self):
        super().__init__("Live Transcription")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the transcription display UI."""
        layout = QVBoxLayout(self)
        
        # Transcription text area
        self.text_area = QTextEdit()
        self.text_area.setMaximumHeight(100)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_area)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_text)
        controls_layout.addWidget(self.clear_button)
        
        controls_layout.addStretch()
        
        # Word count
        self.word_count_label = QLabel("Words: 0")
        controls_layout.addWidget(self.word_count_label)
        
        layout.addLayout(controls_layout)
    
    def add_transcription(self, text: str):
        """Add new transcription text."""
        if text.strip():
            self.text_area.append(text.strip())
            
            # Update word count
            all_text = self.text_area.toPlainText()
            word_count = len(all_text.split()) if all_text.strip() else 0
            self.word_count_label.setText(f"Words: {word_count}")
            
            # Auto-scroll to bottom
            cursor = self.text_area.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_area.setTextCursor(cursor)
    
    def clear_text(self):
        """Clear the transcription text."""
        self.text_area.clear()
        self.word_count_label.setText("Words: 0")

class RealTimeWidget(QWidget):
    """Real-time speech analysis widget."""
    
    # Signals
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.is_recording = False
        self.setup_ui()
        
        # Update timer for visual effects
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_visuals)
        self.update_timer.start(100)  # 10 FPS
    
    def setup_ui(self):
        """Setup the real-time analysis UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("Real-Time Speech Analysis")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Recording controls
        self.record_button = QPushButton("Start Monitoring")
        self.record_button.setFixedSize(150, 40)
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        header_layout.addWidget(self.record_button)
        
        layout.addLayout(header_layout)
        
        # Status and audio level
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.status_label)
        
        # Audio level meter
        self.audio_meter = AudioLevelMeter()
        status_layout.addWidget(self.audio_meter)
        
        layout.addWidget(QFrame())  # Separator
        layout.addLayout(status_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side - Real-time scores
        scores_group = QGroupBox("Real-Time Scores")
        scores_layout = QGridLayout(scores_group)
        
        self.overall_score = RealTimeScoreDisplay("Overall")
        self.tone_score = RealTimeScoreDisplay("Tone")
        self.clarity_score = RealTimeScoreDisplay("Clarity")
        self.volume_score = RealTimeScoreDisplay("Volume")
        self.fluency_score = RealTimeScoreDisplay("Fluency")
        
        scores_layout.addWidget(self.overall_score, 0, 0)
        scores_layout.addWidget(self.tone_score, 0, 1)
        scores_layout.addWidget(self.clarity_score, 0, 2)
        scores_layout.addWidget(self.volume_score, 1, 0)
        scores_layout.addWidget(self.fluency_score, 1, 1)
        
        content_layout.addWidget(scores_group)
        
        # Right side - Settings and feedback
        right_panel = QVBoxLayout()
        
        # Analysis settings
        settings_group = QGroupBox("Analysis Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Sensitivity slider
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_label = QLabel("5")
        sensitivity_layout.addWidget(self.sensitivity_label)
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(str(v))
        )
        settings_layout.addLayout(sensitivity_layout)
        
        # Alert settings
        self.enable_alerts_checkbox = QCheckBox("Enable Audio Alerts")
        self.enable_alerts_checkbox.setChecked(True)
        settings_layout.addWidget(self.enable_alerts_checkbox)
        
        self.enable_visual_feedback_checkbox = QCheckBox("Enable Visual Feedback")
        self.enable_visual_feedback_checkbox.setChecked(True)
        settings_layout.addWidget(self.enable_visual_feedback_checkbox)
        
        right_panel.addWidget(settings_group)
        
        # Current feedback
        feedback_group = QGroupBox("Current Feedback")
        feedback_layout = QVBoxLayout(feedback_group)
        
        self.feedback_label = QLabel("No feedback available")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("""
            QLabel {
                background-color: #484848;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 4px;
                padding: 10px;
                min-height: 80px;
            }
        """)
        feedback_layout.addWidget(self.feedback_label)
        
        right_panel.addWidget(feedback_group)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setMaximumWidth(300)
        content_layout.addWidget(right_widget)
        
        layout.addLayout(content_layout)
        
        # Bottom - Transcription
        self.transcription_display = TranscriptionDisplay()
        layout.addWidget(self.transcription_display)
        
        # Current analysis data
        self.current_analysis = None
    
    def toggle_recording(self):
        """Toggle recording state."""
        if self.is_recording:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        try:
            self.is_recording = True
            
            # Update UI
            self.record_button.setText("Stop Monitoring")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
                QPushButton:pressed {
                    background-color: #c1150a;
                }
            """)
            
            self.status_label.setText("Status: Monitoring...")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            # Clear previous data
            self.transcription_display.clear_text()
            
            # Emit signal to start recording
            self.start_recording.emit()
            
            logger.info("Started real-time monitoring")
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        try:
            self.is_recording = False
            
            # Update UI
            self.record_button.setText("Start Monitoring")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)
            
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("color: #666;")
            
            # Reset audio meter
            self.audio_meter.update_level(0.0)
            
            # Emit signal to stop recording
            self.stop_recording.emit()
            
            logger.info("Stopped real-time monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    def update_analysis(self, analysis_result: Dict[str, Any]):
        """Update the display with new analysis results."""
        try:
            self.current_analysis = analysis_result
            
            # Update scores
            scores = analysis_result.get('scores', {})
            self.overall_score.update_score(scores.get('overall', 0))
            self.tone_score.update_score(scores.get('tone', 0))
            self.clarity_score.update_score(scores.get('clarity', 0))
            self.volume_score.update_score(scores.get('volume', 0))
            self.fluency_score.update_score(scores.get('fluency', 0))
            
            # Update transcription
            transcription = analysis_result.get('transcription', '')
            if transcription:
                self.transcription_display.add_transcription(transcription)
            
            # Update feedback
            alerts = analysis_result.get('alerts', [])
            if alerts:
                feedback_text = "⚠️ " + "\n⚠️ ".join(alerts)
                self.feedback_label.setText(feedback_text)
                self.feedback_label.setStyleSheet("""
                    QLabel {
                        background-color: #5d4e37;
                        border: 1px solid #8b7355;
                        border-radius: 4px;
                        padding: 10px;
                        min-height: 80px;
                        color: #ffffff;
                    }
                """)
            else:
                if scores.get('overall', 0) >= 80:
                    self.feedback_label.setText("✅ Excellent! Keep up the great work!")
                    self.feedback_label.setStyleSheet("""
                        QLabel {
                            background-color: #2d4a2d;
                            border: 1px solid #4CAF50;
                            border-radius: 4px;
                            padding: 10px;
                            min-height: 80px;
                            color: #ffffff;
                        }
                    """)
                else:
                    self.feedback_label.setText("📊 Continue speaking for more feedback...")
                    self.feedback_label.setStyleSheet("""
                        QLabel {
                            background-color: #484848;
                            border: 1px solid #666666;
                            border-radius: 4px;
                            padding: 10px;
                            min-height: 80px;
                            color: #ffffff;
                        }
                    """)
            
        except Exception as e:
            logger.error(f"Error updating analysis display: {e}")
    
    def update_audio_level(self, level: float):
        """Update the audio level meter."""
        self.audio_meter.update_level(level)
    
    def update_visuals(self):
        """Update visual elements periodically."""
        if self.is_recording:
            # Simulate audio level updates (replace with actual audio level)
            # This would be connected to the actual audio manager
            import random
            level = random.random() * 0.5 + 0.1  # Simulate some audio activity
            self.update_audio_level(level)
