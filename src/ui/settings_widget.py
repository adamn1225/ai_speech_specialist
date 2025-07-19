"""
Settings Widget for Speech Coach Application
Manages application settings and OpenAI API configuration
"""

import logging
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QSpinBox,
    QGroupBox, QCheckBox, QComboBox, QSlider, QTextEdit,
    QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SettingsWidget(QWidget):
    """Widget for managing application settings."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        # Settings storage
        self.settings = self.load_default_settings()
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings widget UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Settings")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Settings tabs
        self.tab_widget = QTabWidget()
        
        # OpenAI tab
        self.setup_openai_tab()
        self.tab_widget.addTab(self.openai_tab, "OpenAI API")
        
        # Audio tab
        self.setup_audio_tab()
        self.tab_widget.addTab(self.audio_tab, "Audio")
        
        # Analysis tab
        self.setup_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Analysis")
        
        # General tab
        self.setup_general_tab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.test_connection_button = QPushButton("Test OpenAI Connection")
        self.test_connection_button.clicked.connect(self.test_openai_connection)
        buttons_layout.addWidget(self.test_connection_button)
        
        buttons_layout.addStretch()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_openai_tab(self):
        """Setup the OpenAI configuration tab."""
        self.openai_tab = QWidget()
        layout = QVBoxLayout(self.openai_tab)
        
        # API Key section
        api_group = QGroupBox("API Configuration")
        api_layout = QGridLayout(api_group)
        
        # API Key
        api_layout.addWidget(QLabel("API Key:"), 0, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API key...")
        api_layout.addWidget(self.api_key_edit, 0, 1)
        
        # Show/Hide button
        self.show_api_key_button = QPushButton("Show")
        self.show_api_key_button.setMaximumWidth(60)
        self.show_api_key_button.clicked.connect(self.toggle_api_key_visibility)
        api_layout.addWidget(self.show_api_key_button, 0, 2)
        
        # Organization (optional)
        api_layout.addWidget(QLabel("Organization ID:"), 1, 0)
        self.organization_edit = QLineEdit()
        self.organization_edit.setPlaceholderText("Optional: Organization ID")
        api_layout.addWidget(self.organization_edit, 1, 1, 1, 2)
        
        layout.addWidget(api_group)
        
        # Model settings
        model_group = QGroupBox("Model Settings")
        model_layout = QGridLayout(model_group)
        
        # Whisper model
        model_layout.addWidget(QLabel("Whisper Model:"), 0, 0)
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems(["whisper-1", "local (whisper.cpp)"])
        model_layout.addWidget(self.whisper_model_combo, 0, 1)
        
        # GPT model for analysis
        model_layout.addWidget(QLabel("Analysis Model:"), 1, 0)
        self.gpt_model_combo = QComboBox()
        self.gpt_model_combo.addItems([
            "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"
        ])
        model_layout.addWidget(self.gpt_model_combo, 1, 1)
        
        layout.addWidget(model_group)
        
        # Usage settings
        usage_group = QGroupBox("Usage Settings")
        usage_layout = QVBoxLayout(usage_group)
        
        self.enable_cloud_fallback_check = QCheckBox("Enable cloud fallback for transcription")
        self.enable_cloud_fallback_check.setChecked(True)
        usage_layout.addWidget(self.enable_cloud_fallback_check)
        
        self.enable_gpt_analysis_check = QCheckBox("Enable GPT-powered post-call analysis")
        self.enable_gpt_analysis_check.setChecked(True)
        usage_layout.addWidget(self.enable_gpt_analysis_check)
        
        layout.addWidget(usage_group)
        
        # Connection status
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.connection_status_label = QLabel("Status: Not tested")
        status_layout.addWidget(self.connection_status_label)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
    
    def setup_audio_tab(self):
        """Setup the audio configuration tab."""
        self.audio_tab = QWidget()
        layout = QVBoxLayout(self.audio_tab)
        
        # Audio source
        source_group = QGroupBox("Audio Source")
        source_layout = QGridLayout(source_group)
        
        source_layout.addWidget(QLabel("Input Source:"), 0, 0)
        self.audio_source_combo = QComboBox()
        self.audio_source_combo.addItems(["Auto-detect", "System Monitor", "Microphone"])
        source_layout.addWidget(self.audio_source_combo, 0, 1)
        
        self.refresh_sources_button = QPushButton("Refresh")
        self.refresh_sources_button.clicked.connect(self.refresh_audio_sources)
        source_layout.addWidget(self.refresh_sources_button, 0, 2)
        
        layout.addWidget(source_group)
        
        # Audio processing
        processing_group = QGroupBox("Audio Processing")
        processing_layout = QGridLayout(processing_group)
        
        # Sample rate
        processing_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000 Hz", "22050 Hz", "44100 Hz", "48000 Hz"])
        processing_layout.addWidget(self.sample_rate_combo, 0, 1)
        
        # Chunk duration
        processing_layout.addWidget(QLabel("Chunk Duration:"), 1, 0)
        self.chunk_duration_spin = QSpinBox()
        self.chunk_duration_spin.setRange(1, 10)
        self.chunk_duration_spin.setValue(3)
        self.chunk_duration_spin.setSuffix(" seconds")
        processing_layout.addWidget(self.chunk_duration_spin, 1, 1)
        
        # Overlap duration
        processing_layout.addWidget(QLabel("Overlap Duration:"), 2, 0)
        self.overlap_duration_spin = QSpinBox()
        self.overlap_duration_spin.setRange(0, 2)
        self.overlap_duration_spin.setValue(1)
        self.overlap_duration_spin.setSuffix(" seconds")
        processing_layout.addWidget(self.overlap_duration_spin, 2, 1)
        
        layout.addWidget(processing_group)
        
        # Audio levels
        levels_group = QGroupBox("Audio Levels")
        levels_layout = QGridLayout(levels_group)
        
        # Minimum level threshold
        levels_layout.addWidget(QLabel("Min Level Threshold:"), 0, 0)
        self.min_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_level_slider.setRange(0, 100)
        self.min_level_slider.setValue(10)
        levels_layout.addWidget(self.min_level_slider, 0, 1)
        self.min_level_label = QLabel("10%")
        self.min_level_slider.valueChanged.connect(
            lambda v: self.min_level_label.setText(f"{v}%")
        )
        levels_layout.addWidget(self.min_level_label, 0, 2)
        
        layout.addWidget(levels_group)
        layout.addStretch()
    
    def setup_analysis_tab(self):
        """Setup the analysis configuration tab."""
        self.analysis_tab = QWidget()
        layout = QVBoxLayout(self.analysis_tab)
        
        # Analysis thresholds
        thresholds_group = QGroupBox("Analysis Thresholds")
        thresholds_layout = QGridLayout(thresholds_group)
        
        # Speaking rate range
        thresholds_layout.addWidget(QLabel("Speaking Rate (WPM):"), 0, 0)
        rate_layout = QHBoxLayout()
        self.min_rate_spin = QSpinBox()
        self.min_rate_spin.setRange(50, 300)
        self.min_rate_spin.setValue(150)
        rate_layout.addWidget(self.min_rate_spin)
        rate_layout.addWidget(QLabel(" - "))
        self.max_rate_spin = QSpinBox()
        self.max_rate_spin.setRange(50, 300)
        self.max_rate_spin.setValue(200)
        rate_layout.addWidget(self.max_rate_spin)
        thresholds_layout.addLayout(rate_layout, 0, 1)
        
        # Filler words threshold
        thresholds_layout.addWidget(QLabel("Max Filler Words:"), 1, 0)
        self.filler_threshold_spin = QSpinBox()
        self.filler_threshold_spin.setRange(1, 20)
        self.filler_threshold_spin.setValue(5)
        self.filler_threshold_spin.setSuffix("%")
        thresholds_layout.addWidget(self.filler_threshold_spin, 1, 1)
        
        # Volume consistency threshold
        thresholds_layout.addWidget(QLabel("Volume Consistency:"), 2, 0)
        self.volume_consistency_spin = QSpinBox()
        self.volume_consistency_spin.setRange(50, 100)
        self.volume_consistency_spin.setValue(80)
        self.volume_consistency_spin.setSuffix("%")
        thresholds_layout.addWidget(self.volume_consistency_spin, 2, 1)
        
        layout.addWidget(thresholds_group)
        
        # Filler words customization
        fillers_group = QGroupBox("Filler Words")
        fillers_layout = QVBoxLayout(fillers_group)
        
        fillers_layout.addWidget(QLabel("Customize the list of words to detect as fillers:"))
        
        self.filler_words_edit = QTextEdit()
        self.filler_words_edit.setMaximumHeight(100)
        self.filler_words_edit.setPlaceholderText("Enter filler words, one per line...")
        fillers_layout.addWidget(self.filler_words_edit)
        
        layout.addWidget(fillers_group)
        
        # Scoring weights
        weights_group = QGroupBox("Scoring Weights")
        weights_layout = QGridLayout(weights_group)
        
        # Overall score weights
        weights_layout.addWidget(QLabel("Tone Weight:"), 0, 0)
        self.tone_weight_spin = QSpinBox()
        self.tone_weight_spin.setRange(0, 100)
        self.tone_weight_spin.setValue(25)
        self.tone_weight_spin.setSuffix("%")
        weights_layout.addWidget(self.tone_weight_spin, 0, 1)
        
        weights_layout.addWidget(QLabel("Clarity Weight:"), 1, 0)
        self.clarity_weight_spin = QSpinBox()
        self.clarity_weight_spin.setRange(0, 100)
        self.clarity_weight_spin.setValue(25)
        self.clarity_weight_spin.setSuffix("%")
        weights_layout.addWidget(self.clarity_weight_spin, 1, 1)
        
        weights_layout.addWidget(QLabel("Volume Weight:"), 2, 0)
        self.volume_weight_spin = QSpinBox()
        self.volume_weight_spin.setRange(0, 100)
        self.volume_weight_spin.setValue(20)
        self.volume_weight_spin.setSuffix("%")
        weights_layout.addWidget(self.volume_weight_spin, 2, 1)
        
        weights_layout.addWidget(QLabel("Fluency Weight:"), 3, 0)
        self.fluency_weight_spin = QSpinBox()
        self.fluency_weight_spin.setRange(0, 100)
        self.fluency_weight_spin.setValue(30)
        self.fluency_weight_spin.setSuffix("%")
        weights_layout.addWidget(self.fluency_weight_spin, 3, 1)
        
        layout.addWidget(weights_group)
        layout.addStretch()
    
    def setup_general_tab(self):
        """Setup the general settings tab."""
        self.general_tab = QWidget()
        layout = QVBoxLayout(self.general_tab)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QGridLayout(appearance_group)
        
        appearance_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        appearance_layout.addWidget(self.theme_combo, 0, 1)
        
        layout.addWidget(appearance_group)
        
        # Notifications
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.enable_notifications_check = QCheckBox("Enable system notifications")
        self.enable_notifications_check.setChecked(True)
        notifications_layout.addWidget(self.enable_notifications_check)
        
        self.enable_sound_alerts_check = QCheckBox("Enable sound alerts")
        self.enable_sound_alerts_check.setChecked(False)
        notifications_layout.addWidget(self.enable_sound_alerts_check)
        
        layout.addWidget(notifications_group)
        
        # Data and Privacy
        privacy_group = QGroupBox("Data and Privacy")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.save_recordings_check = QCheckBox("Save audio recordings locally")
        self.save_recordings_check.setChecked(False)
        privacy_layout.addWidget(self.save_recordings_check)
        
        self.save_transcripts_check = QCheckBox("Save transcripts locally")
        self.save_transcripts_check.setChecked(True)
        privacy_layout.addWidget(self.save_transcripts_check)
        
        # Data location
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("Data Directory:"))
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setText(str(Path.home() / "speech_coach_data"))
        data_layout.addWidget(self.data_dir_edit)
        
        self.browse_data_dir_button = QPushButton("Browse...")
        self.browse_data_dir_button.clicked.connect(self.browse_data_directory)
        data_layout.addWidget(self.browse_data_dir_button)
        
        privacy_layout.addLayout(data_layout)
        
        layout.addWidget(privacy_group)
        layout.addStretch()
    
    def load_default_settings(self) -> Dict[str, Any]:
        """Load default settings."""
        return {
            'openai': {
                'api_key': '',
                'organization': '',
                'whisper_model': 'local (whisper.cpp)',
                'gpt_model': 'gpt-4o-mini',
                'enable_cloud_fallback': True,
                'enable_gpt_analysis': True
            },
            'audio': {
                'source': 'Auto-detect',
                'sample_rate': 16000,
                'chunk_duration': 3.0,
                'overlap_duration': 0.5,
                'min_level_threshold': 0.1
            },
            'analysis': {
                'speaking_rate_range': [150, 200],
                'filler_threshold': 0.05,
                'volume_consistency': 0.8,
                'filler_words': [
                    'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well',
                    'actually', 'basically', 'literally', 'seriously', 'totally'
                ],
                'weights': {
                    'tone': 0.25,
                    'clarity': 0.25,
                    'volume': 0.2,
                    'fluency': 0.3
                }
            },
            'general': {
                'theme': 'Light',
                'enable_notifications': True,
                'enable_sound_alerts': False,
                'save_recordings': False,
                'save_transcripts': True,
                'data_directory': str(Path.home() / "speech_coach_data")
            }
        }
    
    def load_settings(self):
        """Load settings into UI."""
        try:
            # OpenAI settings
            openai_settings = self.settings.get('openai', {})
            self.api_key_edit.setText(openai_settings.get('api_key', ''))
            self.organization_edit.setText(openai_settings.get('organization', ''))
            
            whisper_model = openai_settings.get('whisper_model', 'local (whisper.cpp)')
            index = self.whisper_model_combo.findText(whisper_model)
            if index >= 0:
                self.whisper_model_combo.setCurrentIndex(index)
            
            gpt_model = openai_settings.get('gpt_model', 'gpt-4o-mini')
            index = self.gpt_model_combo.findText(gpt_model)
            if index >= 0:
                self.gpt_model_combo.setCurrentIndex(index)
            
            self.enable_cloud_fallback_check.setChecked(openai_settings.get('enable_cloud_fallback', True))
            self.enable_gpt_analysis_check.setChecked(openai_settings.get('enable_gpt_analysis', True))
            
            # Audio settings
            audio_settings = self.settings.get('audio', {})
            self.chunk_duration_spin.setValue(int(audio_settings.get('chunk_duration', 3)))
            self.overlap_duration_spin.setValue(int(audio_settings.get('overlap_duration', 0.5)))
            self.min_level_slider.setValue(int(audio_settings.get('min_level_threshold', 0.1) * 100))
            
            # Analysis settings
            analysis_settings = self.settings.get('analysis', {})
            rate_range = analysis_settings.get('speaking_rate_range', [150, 200])
            self.min_rate_spin.setValue(rate_range[0])
            self.max_rate_spin.setValue(rate_range[1])
            
            self.filler_threshold_spin.setValue(int(analysis_settings.get('filler_threshold', 0.05) * 100))
            self.volume_consistency_spin.setValue(int(analysis_settings.get('volume_consistency', 0.8) * 100))
            
            filler_words = analysis_settings.get('filler_words', [])
            self.filler_words_edit.setText('\n'.join(filler_words))
            
            weights = analysis_settings.get('weights', {})
            self.tone_weight_spin.setValue(int(weights.get('tone', 0.25) * 100))
            self.clarity_weight_spin.setValue(int(weights.get('clarity', 0.25) * 100))
            self.volume_weight_spin.setValue(int(weights.get('volume', 0.2) * 100))
            self.fluency_weight_spin.setValue(int(weights.get('fluency', 0.3) * 100))
            
            # General settings
            general_settings = self.settings.get('general', {})
            self.enable_notifications_check.setChecked(general_settings.get('enable_notifications', True))
            self.enable_sound_alerts_check.setChecked(general_settings.get('enable_sound_alerts', False))
            self.save_recordings_check.setChecked(general_settings.get('save_recordings', False))
            self.save_transcripts_check.setChecked(general_settings.get('save_transcripts', True))
            self.data_dir_edit.setText(general_settings.get('data_directory', str(Path.home() / "speech_coach_data")))
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings."""
        try:
            # Collect settings from UI
            self.settings = {
                'openai': {
                    'api_key': self.api_key_edit.text(),
                    'organization': self.organization_edit.text(),
                    'whisper_model': self.whisper_model_combo.currentText(),
                    'gpt_model': self.gpt_model_combo.currentText(),
                    'enable_cloud_fallback': self.enable_cloud_fallback_check.isChecked(),
                    'enable_gpt_analysis': self.enable_gpt_analysis_check.isChecked()
                },
                'audio': {
                    'source': self.audio_source_combo.currentText(),
                    'sample_rate': int(self.sample_rate_combo.currentText().split()[0]),
                    'chunk_duration': self.chunk_duration_spin.value(),
                    'overlap_duration': self.overlap_duration_spin.value(),
                    'min_level_threshold': self.min_level_slider.value() / 100.0
                },
                'analysis': {
                    'speaking_rate_range': [self.min_rate_spin.value(), self.max_rate_spin.value()],
                    'filler_threshold': self.filler_threshold_spin.value() / 100.0,
                    'volume_consistency': self.volume_consistency_spin.value() / 100.0,
                    'filler_words': [word.strip() for word in self.filler_words_edit.toPlainText().split('\n') if word.strip()],
                    'weights': {
                        'tone': self.tone_weight_spin.value() / 100.0,
                        'clarity': self.clarity_weight_spin.value() / 100.0,
                        'volume': self.volume_weight_spin.value() / 100.0,
                        'fluency': self.fluency_weight_spin.value() / 100.0
                    }
                },
                'general': {
                    'theme': self.theme_combo.currentText(),
                    'enable_notifications': self.enable_notifications_check.isChecked(),
                    'enable_sound_alerts': self.enable_sound_alerts_check.isChecked(),
                    'save_recordings': self.save_recordings_check.isChecked(),
                    'save_transcripts': self.save_transcripts_check.isChecked(),
                    'data_directory': self.data_dir_edit.text()
                }
            }
            
            # Save to file
            config_path = Path.home() / ".speech_coach_config.json"
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            # Emit settings changed signal
            self.settings_changed.emit(self.settings)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self.load_default_settings()
            self.load_settings()
            logger.info("Settings reset to defaults")
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_button.setText("Hide")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_key_button.setText("Show")
    
    def test_openai_connection(self):
        """Test OpenAI API connection."""
        api_key = self.api_key_edit.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter your OpenAI API key first.")
            return
        
        try:
            # TODO: Implement actual OpenAI API test
            self.connection_status_label.setText("Status: Testing connection...")
            self.connection_status_label.setStyleSheet("color: orange;")
            
            # Simulate connection test
            QMessageBox.information(self, "Connection Test", "OpenAI connection test feature will be implemented with the cloud integration.")
            
            self.connection_status_label.setText("Status: Test completed")
            self.connection_status_label.setStyleSheet("color: blue;")
            
        except Exception as e:
            self.connection_status_label.setText("Status: Connection failed")
            self.connection_status_label.setStyleSheet("color: red;")
            QMessageBox.warning(self, "Connection Test Failed", f"Failed to connect to OpenAI API:\n\n{e}")
    
    def refresh_audio_sources(self):
        """Refresh available audio sources."""
        # TODO: Implement audio source detection
        QMessageBox.information(self, "Audio Sources", "Audio source detection will be implemented with the audio manager integration.")
    
    def browse_data_directory(self):
        """Browse for data directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", self.data_dir_edit.text()
        )
        
        if directory:
            self.data_dir_edit.setText(directory)
    
    def is_openai_connected(self) -> bool:
        """Check if OpenAI is configured and connected."""
        return bool(self.settings.get('openai', {}).get('api_key', '').strip())
