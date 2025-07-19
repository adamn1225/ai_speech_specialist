# Speech Coach - Professional Communication Trainer

A desktop application for Linux that provides AI-powered speech analysis and training for sales professionals. Features real-time feedback, practice lessons, and detailed analytics to improve communication skills.

## Features

### 🎤 Real-Time Analysis
- Live audio capture and analysis
- Immediate feedback on tone, clarity, volume, and fluency
- Visual indicators and alerts
- <500ms latency for local processing

### 📚 Practice Lessons
- Pre-built lesson modules
- Custom lesson creation
- Targeted exercises for specific metrics
- Progress tracking and scoring

### 📊 Detailed Analytics
- Comprehensive speech metrics
- Historical trends and reporting
- Session summaries and insights
- Export capabilities

### 🤖 AI Integration
- Local Whisper.cpp for fast transcription
- OpenAI GPT for advanced analysis
- Hybrid edge/cloud architecture
- Offline capability with cloud fallback

## Installation

### Prerequisites

1. **System Dependencies**
   ```bash
   # Install system packages
   sudo apt update
   sudo apt install -y cmake build-essential python3-dev portaudio19-dev
   ```

2. **Python Environment**
   ```bash
   # Create virtual environment
   python3 -m venv speech_coach_env
   source speech_coach_env/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Whisper.cpp Setup**
   
   The application includes whisper.cpp for local transcription. If you need to rebuild it:
   ```bash
   cd whisper.cpp
   mkdir build && cd build
   cmake -DCMAKE_BUILD_TYPE=Release ..
   make -j$(nproc)
   
   # Download model
   cd .. && bash ./models/download-ggml-model.sh base.en
   ```

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd speech_coach
   
   # Set up environment
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Configure OpenAI API (Optional)**
   - Go to Settings → OpenAI API
   - Enter your API key for cloud features
   - Test the connection

## Usage

### Real-Time Monitoring

1. Go to the "Real-Time Analysis" tab
2. Click "Start Monitoring" 
3. Speak naturally - the app will analyze your speech in real-time
4. View live scores and feedback
5. Check alerts for areas to improve

### Practice Lessons

1. Navigate to "Practice Lessons"
2. Select a lesson from the list
3. Click "Start Lesson"
4. Read the provided text aloud
5. Record each exercise and review feedback
6. Complete all exercises for a final score

### Settings Configuration

- **Audio**: Configure input sources and processing parameters
- **Analysis**: Adjust thresholds and scoring weights
- **OpenAI**: Set up API integration for advanced features
- **General**: Customize appearance and data storage

## Architecture

### Core Components

- **UI Layer**: PyQt6-based desktop interface
- **Audio Manager**: Real-time audio capture via PyAudio/PulseAudio
- **Speech Analyzer**: Local processing using Whisper.cpp, librosa, parselmouth
- **Cloud Integration**: FastAPI service for OpenAI API fallback
- **Lesson Engine**: Structured practice modules and scoring

### Data Flow

1. Audio captured from system or microphone
2. Real-time chunking (3-second segments, 0.5s overlap)
3. Local transcription via Whisper.cpp
4. Feature extraction (tone, clarity, volume, fillers)
5. Scoring and alert generation
6. UI updates and user feedback

### Performance

- **Latency**: <500ms for real-time analysis
- **Accuracy**: Professional-grade speech metrics
- **Efficiency**: Optimized for continuous operation
- **Offline**: Full functionality without internet

## File Structure

```
speech_coach/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── whisper.cpp/           # Local Whisper implementation
├── src/                   # Source code
│   ├── ui/                # User interface
│   ├── audio/             # Audio processing
│   ├── analysis/          # Speech analysis
│   ├── lessons/           # Lesson management
│   └── cloud/             # Cloud integration
├── data/                  # Application data
│   └── lessons/           # Lesson definitions
└── config/                # Configuration files
```

## Configuration

### Audio Settings
- Sample rate: 16kHz (optimized for Whisper)
- Chunk duration: 3 seconds
- Overlap: 0.5 seconds
- Input source: Auto-detect or manual selection

### Analysis Thresholds
- Speaking rate: 150-200 WPM
- Filler words: <5% of total words
- Volume consistency: >80%
- Pitch variance: Natural prosody range

### Scoring Weights
- Tone: 25%
- Clarity: 25%
- Volume: 20%
- Fluency: 30%

## API Integration

### OpenAI Configuration

1. Obtain API key from OpenAI
2. Set in Settings → OpenAI API
3. Configure models:
   - Transcription: whisper-1 (cloud) or local
   - Analysis: gpt-4o-mini (recommended)

### Usage Monitoring

The application tracks API usage and provides estimates. Cloud features are optional - full functionality available offline.

## Troubleshooting

### Audio Issues
- **No audio detected**: Check PulseAudio configuration
- **Permission denied**: Ensure user is in audio group
- **Poor quality**: Adjust input levels and sample rate

### Performance Issues
- **High latency**: Reduce chunk duration or disable cloud features
- **CPU usage**: Close other audio applications
- **Memory usage**: Restart application periodically for long sessions

### Whisper Issues
- **Model not found**: Re-download with provided script
- **Slow transcription**: Check CPU availability and model size
- **Poor accuracy**: Ensure clear audio input and proper microphone

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Code formatting
black src/
isort src/
```

## License

[License information to be added]

## Support

For issues and questions:
- Check the troubleshooting section
- Review system requirements
- Submit issues on GitHub

## Roadmap

- [ ] Advanced lesson customization
- [ ] Team collaboration features
- [ ] Mobile companion app
- [ ] Integration with video conferencing
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
