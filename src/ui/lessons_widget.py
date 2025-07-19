"""
Lessons Widget for Speech Coach Application
Manages practice lessons and exercises
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QListWidget, QTextEdit,
    QGroupBox, QProgressBar, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class LessonsWidget(QWidget):
    """Widget for managing and running practice lessons."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_sample_lessons()
    
    def setup_ui(self):
        """Setup the lessons widget UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Practice Lessons")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left side - Lesson list
        lessons_group = QGroupBox("Available Lessons")
        lessons_layout = QVBoxLayout(lessons_group)
        
        self.lessons_list = QListWidget()
        self.lessons_list.itemClicked.connect(self.select_lesson)
        lessons_layout.addWidget(self.lessons_list)
        
        # Lesson controls
        controls_layout = QHBoxLayout()
        
        self.start_lesson_button = QPushButton("Start Lesson")
        self.start_lesson_button.clicked.connect(self.start_lesson)
        self.start_lesson_button.setEnabled(False)
        controls_layout.addWidget(self.start_lesson_button)
        
        self.create_lesson_button = QPushButton("Create Custom")
        self.create_lesson_button.clicked.connect(self.create_custom_lesson)
        controls_layout.addWidget(self.create_lesson_button)
        
        lessons_layout.addLayout(controls_layout)
        content_layout.addWidget(lessons_group, 1)
        
        # Right side - Lesson details and practice
        right_panel = QVBoxLayout()
        
        # Lesson details
        details_group = QGroupBox("Lesson Details")
        details_layout = QVBoxLayout(details_group)
        
        self.lesson_title_label = QLabel("Select a lesson to view details")
        self.lesson_title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_layout.addWidget(self.lesson_title_label)
        
        self.lesson_description_label = QLabel("")
        self.lesson_description_label.setWordWrap(True)
        details_layout.addWidget(self.lesson_description_label)
        
        self.lesson_objectives_label = QLabel("")
        self.lesson_objectives_label.setWordWrap(True)
        details_layout.addWidget(self.lesson_objectives_label)
        
        right_panel.addWidget(details_group)
        
        # Practice area
        practice_group = QGroupBox("Practice Area")
        practice_layout = QVBoxLayout(practice_group)
        
        # Practice text
        self.practice_text = QTextEdit()
        self.practice_text.setMaximumHeight(120)
        self.practice_text.setReadOnly(True)
        self.practice_text.setPlaceholderText("Practice text will appear here when you start a lesson...")
        practice_layout.addWidget(self.practice_text)
        
        # Progress
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        practice_layout.addLayout(progress_layout)
        
        # Practice controls
        practice_controls_layout = QHBoxLayout()
        
        self.record_practice_button = QPushButton("Start Recording")
        self.record_practice_button.clicked.connect(self.toggle_practice_recording)
        self.record_practice_button.setEnabled(False)
        practice_controls_layout.addWidget(self.record_practice_button)
        
        self.next_exercise_button = QPushButton("Next Exercise")
        self.next_exercise_button.clicked.connect(self.next_exercise)
        self.next_exercise_button.setEnabled(False)
        practice_controls_layout.addWidget(self.next_exercise_button)
        
        self.finish_lesson_button = QPushButton("Finish Lesson")
        self.finish_lesson_button.clicked.connect(self.finish_lesson)
        self.finish_lesson_button.setEnabled(False)
        practice_controls_layout.addWidget(self.finish_lesson_button)
        
        practice_layout.addLayout(practice_controls_layout)
        
        right_panel.addWidget(practice_group)
        
        # Results area
        results_group = QGroupBox("Lesson Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(100)
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here after completing exercises...")
        results_layout.addWidget(self.results_text)
        
        right_panel.addWidget(results_group)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        content_layout.addWidget(right_widget, 2)
        
        layout.addLayout(content_layout)
        
        # State variables
        self.current_lesson = None
        self.current_exercise_index = 0
        self.is_recording_practice = False
        self.lesson_results = []
    
    def load_sample_lessons(self):
        """Load sample lessons into the list."""
        sample_lessons = [
            {
                'title': 'Clarity and Articulation',
                'description': 'Practice clear pronunciation and articulation of difficult words and phrases.',
                'objectives': 'Improve clarity score to 85+, reduce mumbling, enhance consonant pronunciation.',
                'exercises': [
                    "The quick brown fox jumps over the lazy dog.",
                    "Red leather, yellow leather, red leather, yellow leather.",
                    "She sells seashells by the seashore.",
                    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
                    "Peter Piper picked a peck of pickled peppers."
                ]
            },
            {
                'title': 'Tone and Prosody',
                'description': 'Work on varying your pitch and intonation for more engaging speech.',
                'objectives': 'Increase pitch variance, improve prosody score to 80+, sound more natural.',
                'exercises': [
                    "Hello, how are you today? I'm doing well, thank you for asking!",
                    "This is fantastic news! We've exceeded our quarterly targets.",
                    "I understand your concern, and I'd like to help resolve this issue.",
                    "Would you be interested in learning more about our premium services?",
                    "Thank you for your time today. I look forward to our next meeting."
                ]
            },
            {
                'title': 'Pace and Rhythm',
                'description': 'Practice speaking at an optimal pace with good rhythm and pausing.',
                'objectives': 'Maintain 150-200 WPM, reduce rushing, improve natural pausing.',
                'exercises': [
                    "Good morning, team. Today we'll be discussing our quarterly results and planning for the next quarter.",
                    "Let me walk you through the key features of our product, step by step, so you can see the value it provides.",
                    "Our customer satisfaction rates have improved significantly this year, thanks to your dedicated efforts.",
                    "I'd like to take a moment to address the concerns raised in yesterday's meeting about project timelines.",
                    "Before we conclude today's presentation, let me summarize the three main points we've covered."
                ]
            },
            {
                'title': 'Filler Word Reduction',
                'description': 'Eliminate unnecessary filler words like "um", "uh", and "like".',
                'objectives': 'Reduce filler words to less than 2% of speech, improve fluency score.',
                'exercises': [
                    "I believe this solution will provide significant value to our customers and improve their overall experience.",
                    "The data shows a clear trend toward increased adoption of our new features among enterprise clients.",
                    "We need to focus on three key areas: customer acquisition, retention, and satisfaction metrics.",
                    "Our team has been working diligently to address the technical challenges and deliver a robust solution.",
                    "The market research indicates strong demand for innovative products in this particular segment."
                ]
            },
            {
                'title': 'Volume and Projection',
                'description': 'Practice maintaining consistent volume and proper voice projection.',
                'objectives': 'Improve volume consistency score to 85+, maintain energy throughout speech.',
                'exercises': [
                    "Welcome everyone to today's important presentation on our company's future direction.",
                    "I'm excited to share these remarkable results with all of you here today.",
                    "Let me make sure everyone can hear this critical information clearly.",
                    "Your attention to detail and commitment to excellence has made this success possible.",
                    "Together, we can achieve even greater heights in the coming year."
                ]
            }
        ]
        
        for lesson in sample_lessons:
            item = QListWidgetItem(lesson['title'])
            item.setData(Qt.ItemDataRole.UserRole, lesson)
            self.lessons_list.addItem(item)
    
    def select_lesson(self, item: QListWidgetItem):
        """Handle lesson selection."""
        lesson_data = item.data(Qt.ItemDataRole.UserRole)
        if lesson_data:
            self.lesson_title_label.setText(lesson_data['title'])
            self.lesson_description_label.setText(f"Description: {lesson_data['description']}")
            self.lesson_objectives_label.setText(f"Objectives: {lesson_data['objectives']}")
            self.start_lesson_button.setEnabled(True)
    
    def start_lesson(self):
        """Start the selected lesson."""
        current_item = self.lessons_list.currentItem()
        if not current_item:
            return
        
        self.current_lesson = current_item.data(Qt.ItemDataRole.UserRole)
        self.current_exercise_index = 0
        self.lesson_results = []
        
        # Update UI state
        self.start_lesson_button.setEnabled(False)
        self.record_practice_button.setEnabled(True)
        self.next_exercise_button.setEnabled(False)
        self.finish_lesson_button.setEnabled(True)
        
        # Load first exercise
        self.load_current_exercise()
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.results_text.clear()
        
        logger.info(f"Started lesson: {self.current_lesson['title']}")
    
    def load_current_exercise(self):
        """Load the current exercise text."""
        if not self.current_lesson or self.current_exercise_index >= len(self.current_lesson['exercises']):
            return
        
        exercise_text = self.current_lesson['exercises'][self.current_exercise_index]
        self.practice_text.setText(exercise_text)
        
        # Update progress
        progress = int(((self.current_exercise_index + 1) / len(self.current_lesson['exercises'])) * 100)
        self.progress_bar.setValue(progress)
    
    def toggle_practice_recording(self):
        """Toggle practice recording."""
        if self.is_recording_practice:
            self.stop_practice_recording()
        else:
            self.start_practice_recording()
    
    def start_practice_recording(self):
        """Start recording practice."""
        self.is_recording_practice = True
        self.record_practice_button.setText("Stop Recording")
        self.record_practice_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        
        # TODO: Connect to actual audio recording system
        logger.info(f"Started recording exercise {self.current_exercise_index + 1}")
    
    def stop_practice_recording(self):
        """Stop recording practice."""
        self.is_recording_practice = False
        self.record_practice_button.setText("Start Recording")
        self.record_practice_button.setStyleSheet("")
        
        # Enable next exercise button
        self.next_exercise_button.setEnabled(True)
        
        # Simulate analysis results
        self.add_exercise_result(f"Exercise {self.current_exercise_index + 1} completed successfully!")
        
        logger.info(f"Stopped recording exercise {self.current_exercise_index + 1}")
    
    def next_exercise(self):
        """Move to the next exercise."""
        if not self.current_lesson:
            return
        
        self.current_exercise_index += 1
        
        if self.current_exercise_index < len(self.current_lesson['exercises']):
            # Load next exercise
            self.load_current_exercise()
            self.record_practice_button.setEnabled(True)
            self.next_exercise_button.setEnabled(False)
        else:
            # All exercises completed
            self.record_practice_button.setEnabled(False)
            self.next_exercise_button.setEnabled(False)
            self.add_exercise_result("All exercises completed! Click 'Finish Lesson' to see final results.")
    
    def finish_lesson(self):
        """Finish the current lesson."""
        if not self.current_lesson:
            return
        
        # Generate lesson summary
        summary = f"Lesson '{self.current_lesson['title']}' completed!\n\n"
        summary += f"Exercises completed: {min(self.current_exercise_index + 1, len(self.current_lesson['exercises']))}\n"
        summary += f"Total exercises: {len(self.current_lesson['exercises'])}\n\n"
        summary += "Individual exercise results:\n"
        
        for i, result in enumerate(self.lesson_results):
            summary += f"{i + 1}. {result}\n"
        
        # Show results
        QMessageBox.information(self, "Lesson Complete", summary)
        
        # Reset UI state
        self.reset_lesson_state()
        
        logger.info(f"Finished lesson: {self.current_lesson['title']}")
    
    def add_exercise_result(self, result: str):
        """Add a result from an exercise."""
        self.lesson_results.append(result)
        
        # Update results display
        results_text = "\n".join([f"{i + 1}. {result}" for i, result in enumerate(self.lesson_results)])
        self.results_text.setText(results_text)
    
    def reset_lesson_state(self):
        """Reset the lesson UI state."""
        self.current_lesson = None
        self.current_exercise_index = 0
        self.lesson_results = []
        self.is_recording_practice = False
        
        # Reset UI
        self.practice_text.clear()
        self.results_text.clear()
        self.progress_bar.setValue(0)
        
        # Reset button states
        self.start_lesson_button.setEnabled(True)
        self.record_practice_button.setEnabled(False)
        self.record_practice_button.setText("Start Recording")
        self.record_practice_button.setStyleSheet("")
        self.next_exercise_button.setEnabled(False)
        self.finish_lesson_button.setEnabled(False)
    
    def create_custom_lesson(self):
        """Create a custom lesson."""
        QMessageBox.information(self, "Custom Lessons", 
                               "Custom lesson creation feature coming soon!\n\n"
                               "You'll be able to:\n"
                               "• Create custom practice texts\n"
                               "• Set specific objectives\n"
                               "• Define target metrics\n"
                               "• Save and share lessons")
