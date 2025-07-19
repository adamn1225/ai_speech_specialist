"""
Dashboard Widget for Speech Coach Application
Shows real-time metrics and historical trends
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette
import numpy as np
from datetime import datetime
from collections import deque
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MetricCard(QFrame):
    """Individual metric display card."""
    
    def __init__(self, title: str, unit: str = ""):
        super().__init__()
        self.title = title
        self.unit = unit
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the metric card UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #484848;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Unit
        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setFont(QFont("Arial", 8))
            unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            unit_label.setStyleSheet("color: #cccccc;")
            layout.addWidget(unit_label)
        
        # Score indicator
        self.score_label = QLabel("Score: --")
        self.score_label.setFont(QFont("Arial", 10))
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score_label)
    
    def update_value(self, value: float, score: Optional[int] = None):
        """Update the metric value and score."""
        if isinstance(value, (int, float)) and not np.isnan(value):
            if isinstance(value, float):
                self.value_label.setText(f"{value:.1f}")
            else:
                self.value_label.setText(str(value))
        else:
            self.value_label.setText("--")
        
        if score is not None:
            self.score_label.setText(f"Score: {score}")
            
            # Color coding
            if score >= 80:
                color = "#4CAF50"  # Green
            elif score >= 60:
                color = "#FF9800"  # Orange
            else:
                color = "#F44336"  # Red
            
            self.score_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        else:
            self.score_label.setText("Score: --")

class AlertsWidget(QGroupBox):
    """Widget for displaying real-time alerts."""
    
    def __init__(self):
        super().__init__("Current Alerts")
        self.alerts = deque(maxlen=10)  # Keep last 10 alerts
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the alerts widget UI."""
        layout = QVBoxLayout(self)
        
        # Scroll area for alerts
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.alerts_widget = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_widget)
        
        scroll_area.setWidget(self.alerts_widget)
        layout.addWidget(scroll_area)
        
        # Clear button
        clear_button = QPushButton("Clear Alerts")
        clear_button.clicked.connect(self.clear_alerts)
        layout.addWidget(clear_button)
    
    def add_alerts(self, alerts: List[str]):
        """Add new alerts."""
        if not alerts:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        for alert in alerts:
            self.alerts.append(f"[{timestamp}] {alert}")
        
        self.update_display()
    
    def update_display(self):
        """Update the alerts display."""
        # Clear existing widgets
        for i in reversed(range(self.alerts_layout.count())):
            item = self.alerts_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
        
        # Add current alerts
        for alert in reversed(self.alerts):  # Show newest first
            alert_label = QLabel(alert)
            alert_label.setWordWrap(True)
            alert_label.setStyleSheet("""
                QLabel {
                    background-color: #5d4e37;
                    color: #ffffff;
                    border: 1px solid #8b7355;
                    border-radius: 4px;
                    padding: 5px;
                    margin: 2px;
                }
            """)
            self.alerts_layout.addWidget(alert_label)
        
        # Add spacer
        self.alerts_layout.addStretch()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        self.update_display()

class DashboardWidget(QWidget):
    """Main dashboard widget showing real-time metrics."""
    
    def __init__(self):
        super().__init__()
        
        # Data storage
        self.data_history = deque(maxlen=100)  # Keep last 100 data points
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Speech Analysis Dashboard")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side - Metrics grid
        metrics_group = QGroupBox("Current Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        # Create metric cards
        self.overall_score_card = MetricCard("Overall Score", "/100")
        self.tone_card = MetricCard("Tone Score", "/100")
        self.clarity_card = MetricCard("Clarity Score", "/100")
        self.volume_card = MetricCard("Volume Score", "/100")
        self.fluency_card = MetricCard("Fluency Score", "/100")
        self.speaking_rate_card = MetricCard("Speaking Rate", "WPM")
        self.pitch_card = MetricCard("Pitch Mean", "Hz")
        self.filler_ratio_card = MetricCard("Filler Words", "%")
        
        # Add cards to grid
        metrics_layout.addWidget(self.overall_score_card, 0, 0)
        metrics_layout.addWidget(self.tone_card, 0, 1)
        metrics_layout.addWidget(self.clarity_card, 0, 2)
        metrics_layout.addWidget(self.volume_card, 1, 0)
        metrics_layout.addWidget(self.fluency_card, 1, 1)
        metrics_layout.addWidget(self.speaking_rate_card, 1, 2)
        metrics_layout.addWidget(self.pitch_card, 2, 0)
        metrics_layout.addWidget(self.filler_ratio_card, 2, 1)
        
        content_layout.addWidget(metrics_group, 2)
        
        # Right side - Alerts and summary
        right_panel = QVBoxLayout()
        
        # Alerts
        self.alerts_widget = AlertsWidget()
        right_panel.addWidget(self.alerts_widget)
        
        # Session summary
        summary_group = QGroupBox("Session Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.session_duration_label = QLabel("Duration: 0:00:00")
        self.session_words_label = QLabel("Total Words: 0")
        self.session_avg_score_label = QLabel("Average Score: --")
        
        summary_layout.addWidget(self.session_duration_label)
        summary_layout.addWidget(self.session_words_label)
        summary_layout.addWidget(self.session_avg_score_label)
        
        # Action buttons
        self.export_button = QPushButton("Export Session Data")
        self.export_button.clicked.connect(self.export_session_data)
        summary_layout.addWidget(self.export_button)
        
        right_panel.addWidget(summary_group)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        content_layout.addWidget(right_widget, 1)
        
        layout.addLayout(content_layout)
        
        # Session tracking
        self.session_start_time = datetime.now()
        self.total_words = 0
        self.score_history = []
    
    def add_data_point(self, analysis_result: Dict[str, Any]):
        """Add a new analysis result to the dashboard."""
        try:
            # Store data
            self.data_history.append({
                'timestamp': datetime.now(),
                'result': analysis_result
            })
            
            # Update session statistics
            self.update_session_stats(analysis_result)
            
            # Update metrics display
            self.update_metrics_display(analysis_result)
            
            # Add alerts
            alerts = analysis_result.get('alerts', [])
            if alerts:
                self.alerts_widget.add_alerts(alerts)
            
            logger.debug("Dashboard updated with new data point")
            
        except Exception as e:
            logger.error(f"Error adding data point to dashboard: {e}")
    
    def update_metrics_display(self, result: Dict[str, Any]):
        """Update the metric cards with new data."""
        try:
            scores = result.get('scores', {})
            metrics = result.get('metrics', {})
            
            # Update score cards
            self.overall_score_card.update_value(scores.get('overall', 0), scores.get('overall', 0))
            self.tone_card.update_value(scores.get('tone', 0), scores.get('tone', 0))
            self.clarity_card.update_value(scores.get('clarity', 0), scores.get('clarity', 0))
            self.volume_card.update_value(scores.get('volume', 0), scores.get('volume', 0))
            self.fluency_card.update_value(scores.get('fluency', 0), scores.get('fluency', 0))
            
            # Update specific metrics
            tone_metrics = metrics.get('tone', {})
            if 'pitch_mean' in tone_metrics:
                self.pitch_card.update_value(tone_metrics['pitch_mean'])
            
            rate_metrics = metrics.get('rate', {})
            if 'words_per_minute' in rate_metrics:
                self.speaking_rate_card.update_value(
                    rate_metrics['words_per_minute'], 
                    rate_metrics.get('score', 0)
                )
            
            filler_metrics = metrics.get('fillers', {})
            if 'ratio' in filler_metrics:
                self.filler_ratio_card.update_value(
                    filler_metrics['ratio'] * 100,  # Convert to percentage
                    filler_metrics.get('score', 0)
                )
            
        except Exception as e:
            logger.error(f"Error updating metrics display: {e}")
    
    def update_session_stats(self, result: Dict[str, Any]):
        """Update session statistics."""
        try:
            # Add words to total
            rate_metrics = result.get('metrics', {}).get('rate', {})
            word_count = rate_metrics.get('word_count', 0)
            if word_count > 0:
                self.total_words += word_count
            
            # Add score to history
            overall_score = result.get('scores', {}).get('overall', 0)
            if overall_score > 0:
                self.score_history.append(overall_score)
            
        except Exception as e:
            logger.error(f"Error updating session stats: {e}")
    
    def update_display(self):
        """Update time-dependent displays."""
        try:
            # Update session duration
            duration = datetime.now() - self.session_start_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.session_duration_label.setText(f"Duration: {duration_str}")
            
            # Update total words
            self.session_words_label.setText(f"Total Words: {self.total_words}")
            
            # Update average score
            if self.score_history:
                avg_score = np.mean(self.score_history)
                self.session_avg_score_label.setText(f"Average Score: {avg_score:.1f}")
            else:
                self.session_avg_score_label.setText("Average Score: --")
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def clear_data(self):
        """Clear all dashboard data."""
        self.data_history.clear()
        self.score_history.clear()
        self.total_words = 0
        self.session_start_time = datetime.now()
        
        # Reset all metric cards
        for card in [self.overall_score_card, self.tone_card, self.clarity_card,
                     self.volume_card, self.fluency_card, self.speaking_rate_card,
                     self.pitch_card, self.filler_ratio_card]:
            card.update_value(0, 0)
        
        # Clear alerts
        self.alerts_widget.clear_alerts()
        
        logger.info("Dashboard data cleared")
    
    def export_session_data(self):
        """Export session data to file."""
        try:
            # TODO: Implement data export functionality
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Export", "Session data export feature coming soon!")
            
        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
