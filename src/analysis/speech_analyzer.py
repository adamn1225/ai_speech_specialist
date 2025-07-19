"""
Speech Analyzer for Speech Coach Application
Handles transcription, tone analysis, clarity scoring, and other speech metrics
"""

import logging
import os
import tempfile
import subprocess
import numpy as np
import librosa
import parselmouth
from typing import Dict, Any, Optional, List
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class SpeechAnalyzer:
    """Analyzes speech for various metrics including tone, clarity, and fillers."""
    
    def __init__(self):
        # Whisper.cpp paths
        self.whisper_model_path = None
        self.whisper_cli_path = None
        
        # Analysis thresholds
        self.thresholds = {
            'pitch_variance_good': (50, 150),  # Hz
            'speaking_rate_good': (150, 200),  # words per minute
            'volume_consistency_good': 0.8,    # ratio
            'filler_words_threshold': 0.05,    # 5% of words
        }
        
        # Filler words to detect
        self.filler_words = [
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well',
            'actually', 'basically', 'literally', 'seriously', 'totally'
        ]
        
        self.initialize_whisper()
    
    def initialize_whisper(self):
        """Initialize Whisper.cpp paths."""
        try:
            # Look for whisper.cpp in the project directory
            project_root = Path(__file__).parent.parent.parent
            whisper_dir = project_root / "whisper.cpp"
            
            if whisper_dir.exists():
                # CLI path
                cli_path = whisper_dir / "build" / "bin" / "whisper-cli"
                if cli_path.exists():
                    self.whisper_cli_path = str(cli_path)
                    logger.info(f"Found whisper CLI at: {self.whisper_cli_path}")
                
                # Model path
                model_path = whisper_dir / "models" / "ggml-base.en.bin"
                if model_path.exists():
                    self.whisper_model_path = str(model_path)
                    logger.info(f"Found whisper model at: {self.whisper_model_path}")
            
            if not self.whisper_cli_path or not self.whisper_model_path:
                logger.warning("Whisper.cpp not fully configured")
                
        except Exception as e:
            logger.error(f"Error initializing Whisper: {e}")
    
    def analyze_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Perform comprehensive speech analysis on audio data.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of audio data
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Convert to float for analysis
            audio_float = audio_data.astype(np.float32) / 32767.0
            
            # Initialize results
            results = {
                'timestamp': np.datetime64('now'),
                'duration': len(audio_data) / sample_rate,
                'transcription': '',
                'metrics': {
                    'tone': {},
                    'clarity': {},
                    'volume': {},
                    'fillers': {},
                    'rate': {}
                },
                'scores': {
                    'overall': 0,
                    'tone': 0,
                    'clarity': 0,
                    'volume': 0,
                    'fluency': 0
                },
                'alerts': []
            }
            
            # Only analyze if audio has sufficient content
            if self._has_speech(audio_float):
                # Transcribe audio
                results['transcription'] = self._transcribe_audio(audio_data, sample_rate)
                
                # Analyze tone/prosody
                results['metrics']['tone'] = self._analyze_tone(audio_float, sample_rate)
                
                # Analyze clarity
                results['metrics']['clarity'] = self._analyze_clarity(audio_float, sample_rate)
                
                # Analyze volume consistency
                results['metrics']['volume'] = self._analyze_volume(audio_float)
                
                # Analyze fillers and rate
                if results['transcription']:
                    results['metrics']['fillers'] = self._analyze_fillers(results['transcription'])
                    results['metrics']['rate'] = self._analyze_speaking_rate(
                        results['transcription'], results['duration']
                    )
                
                # Calculate scores
                results['scores'] = self._calculate_scores(results['metrics'])
                
                # Generate alerts
                results['alerts'] = self._generate_alerts(results['metrics'], results['scores'])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in speech analysis: {e}")
            return self._empty_result(str(e))
    
    def _transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio using Whisper.cpp."""
        if not self.whisper_cli_path or not self.whisper_model_path:
            logger.warning("Whisper not available, skipping transcription")
            return ""
        
        try:
            # Save audio to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                # Convert to 16-bit PCM WAV
                import wave
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                
                wav_path = tmp_file.name
            
            # Run Whisper.cpp
            cmd = [
                self.whisper_cli_path,
                '-m', self.whisper_model_path,
                '-f', wav_path,
                '--no-timestamps',
                '--output-txt'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            # Clean up temporary file
            os.unlink(wav_path)
            
            if result.returncode == 0:
                # Extract text from output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and not line.startswith('[') and not line.startswith('whisper_'):
                        return line.strip()
                return ""
            else:
                logger.error(f"Whisper error: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return ""
    
    def _analyze_tone(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze tone and prosodic features."""
        try:
            # Use Parselmouth for pitch analysis
            sound = parselmouth.Sound(audio, sampling_frequency=sample_rate)
            
            # Extract pitch
            pitch = sound.to_pitch(time_step=0.01)
            pitch_values = pitch.selected_array['frequency']
            
            # Remove undefined values (0 Hz)
            valid_pitch = pitch_values[pitch_values > 0]
            
            if len(valid_pitch) == 0:
                return {'pitch_mean': 0, 'pitch_std': 0, 'pitch_range': 0, 'score': 0}
            
            # Calculate pitch statistics
            pitch_mean = np.mean(valid_pitch)
            pitch_std = np.std(valid_pitch)
            pitch_range = np.max(valid_pitch) - np.min(valid_pitch)
            
            # Score based on pitch variance (good range indicates natural prosody)
            variance_score = 100
            if pitch_std < self.thresholds['pitch_variance_good'][0]:
                variance_score = 50  # Too monotone
            elif pitch_std > self.thresholds['pitch_variance_good'][1]:
                variance_score = 70  # Too varied
            
            return {
                'pitch_mean': float(pitch_mean),
                'pitch_std': float(pitch_std),
                'pitch_range': float(pitch_range),
                'score': variance_score
            }
            
        except Exception as e:
            logger.error(f"Error in tone analysis: {e}")
            return {'pitch_mean': 0, 'pitch_std': 0, 'pitch_range': 0, 'score': 0}
    
    def _analyze_clarity(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze speech clarity using spectral features."""
        try:
            # Calculate spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Calculate MFCCs
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            
            # Clarity metrics
            clarity_metrics = {
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                'mfcc_variance': float(np.mean(np.var(mfccs, axis=1)))
            }
            
            # Simple clarity score based on spectral features
            # Higher spectral centroid and moderate variance suggest clearer speech
            centroid_norm = min(clarity_metrics['spectral_centroid_mean'] / 2000, 1.0)
            variance_norm = min(clarity_metrics['mfcc_variance'] / 100, 1.0)
            
            clarity_score = int((centroid_norm * 0.6 + variance_norm * 0.4) * 100)
            clarity_metrics['score'] = clarity_score
            
            return clarity_metrics
            
        except Exception as e:
            logger.error(f"Error in clarity analysis: {e}")
            return {'spectral_centroid_mean': 0, 'score': 0}
    
    def _analyze_volume(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze volume consistency."""
        try:
            # Calculate RMS energy in sliding windows
            window_size = 1024
            hop_length = 512
            
            rms_values = []
            for i in range(0, len(audio) - window_size, hop_length):
                window = audio[i:i + window_size]
                rms = np.sqrt(np.mean(window ** 2))
                rms_values.append(rms)
            
            rms_values = np.array(rms_values)
            
            if len(rms_values) == 0:
                return {'rms_mean': 0, 'rms_std': 0, 'consistency': 0, 'score': 0}
            
            # Volume statistics
            rms_mean = float(np.mean(rms_values))
            rms_std = float(np.std(rms_values))
            
            # Consistency score (lower std relative to mean is better)
            if rms_mean > 0:
                consistency = 1.0 - min(rms_std / rms_mean, 1.0)
            else:
                consistency = 0.0
            
            # Score based on consistency
            volume_score = int(consistency * 100)
            
            return {
                'rms_mean': rms_mean,
                'rms_std': rms_std,
                'consistency': float(consistency),
                'score': volume_score
            }
            
        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return {'rms_mean': 0, 'rms_std': 0, 'consistency': 0, 'score': 0}
    
    def _analyze_fillers(self, transcription: str) -> Dict[str, Any]:
        """Analyze filler words in transcription."""
        try:
            if not transcription:
                return {'count': 0, 'ratio': 0, 'types': [], 'score': 100}
            
            # Tokenize and clean
            words = re.findall(r'\b\w+\b', transcription.lower())
            total_words = len(words)
            
            if total_words == 0:
                return {'count': 0, 'ratio': 0, 'types': [], 'score': 100}
            
            # Count filler words
            filler_count = 0
            found_fillers = set()
            
            for word in words:
                if word in self.filler_words:
                    filler_count += 1
                    found_fillers.add(word)
            
            # Calculate ratio
            filler_ratio = filler_count / total_words
            
            # Score (lower filler ratio is better)
            if filler_ratio <= self.thresholds['filler_words_threshold']:
                score = 100
            else:
                score = max(0, int(100 - (filler_ratio * 1000)))
            
            return {
                'count': filler_count,
                'ratio': float(filler_ratio),
                'types': list(found_fillers),
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error in filler analysis: {e}")
            return {'count': 0, 'ratio': 0, 'types': [], 'score': 0}
    
    def _analyze_speaking_rate(self, transcription: str, duration: float) -> Dict[str, Any]:
        """Analyze speaking rate."""
        try:
            if not transcription or duration <= 0:
                return {'words_per_minute': 0, 'score': 0}
            
            # Count words
            words = re.findall(r'\b\w+\b', transcription)
            word_count = len(words)
            
            # Calculate WPM
            words_per_minute = (word_count / duration) * 60
            
            # Score based on ideal speaking rate range
            if (self.thresholds['speaking_rate_good'][0] <= 
                words_per_minute <= 
                self.thresholds['speaking_rate_good'][1]):
                score = 100
            elif words_per_minute < self.thresholds['speaking_rate_good'][0]:
                # Too slow
                score = max(0, int((words_per_minute / self.thresholds['speaking_rate_good'][0]) * 100))
            else:
                # Too fast
                score = max(0, int(100 - ((words_per_minute - self.thresholds['speaking_rate_good'][1]) / 2)))
            
            return {
                'words_per_minute': float(words_per_minute),
                'word_count': word_count,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error in speaking rate analysis: {e}")
            return {'words_per_minute': 0, 'word_count': 0, 'score': 0}
    
    def _calculate_scores(self, metrics: Dict[str, Any]) -> Dict[str, int]:
        """Calculate overall scores from metrics."""
        scores = {
            'tone': metrics.get('tone', {}).get('score', 0),
            'clarity': metrics.get('clarity', {}).get('score', 0),
            'volume': metrics.get('volume', {}).get('score', 0),
            'fluency': (metrics.get('fillers', {}).get('score', 0) + 
                       metrics.get('rate', {}).get('score', 0)) // 2
        }
        
        # Overall score is weighted average
        scores['overall'] = int(
            scores['tone'] * 0.25 +
            scores['clarity'] * 0.25 +
            scores['volume'] * 0.2 +
            scores['fluency'] * 0.3
        )
        
        return scores
    
    def _generate_alerts(self, metrics: Dict[str, Any], scores: Dict[str, int]) -> List[str]:
        """Generate alerts for problematic areas."""
        alerts = []
        
        # Tone alerts
        if scores['tone'] < 70:
            alerts.append("Consider varying your pitch more for natural prosody")
        
        # Clarity alerts
        if scores['clarity'] < 70:
            alerts.append("Focus on clear articulation and enunciation")
        
        # Volume alerts
        if scores['volume'] < 70:
            alerts.append("Try to maintain consistent volume levels")
        
        # Filler word alerts
        filler_ratio = metrics.get('fillers', {}).get('ratio', 0)
        if filler_ratio > self.thresholds['filler_words_threshold']:
            alerts.append(f"Reduce filler words ({filler_ratio:.1%} of speech)")
        
        # Speaking rate alerts
        wpm = metrics.get('rate', {}).get('words_per_minute', 0)
        if wpm > 0:
            if wpm < self.thresholds['speaking_rate_good'][0]:
                alerts.append("Consider speaking a bit faster for better engagement")
            elif wpm > self.thresholds['speaking_rate_good'][1]:
                alerts.append("Consider slowing down for better clarity")
        
        return alerts
    
    def _has_speech(self, audio: np.ndarray, threshold: float = 0.01) -> bool:
        """Check if audio contains speech (basic energy threshold)."""
        rms = np.sqrt(np.mean(audio ** 2))
        return rms > threshold
    
    def _empty_result(self, error: str = "") -> Dict[str, Any]:
        """Return empty analysis result."""
        return {
            'timestamp': np.datetime64('now'),
            'duration': 0,
            'transcription': '',
            'metrics': {},
            'scores': {'overall': 0, 'tone': 0, 'clarity': 0, 'volume': 0, 'fluency': 0},
            'alerts': [f"Analysis error: {error}"] if error else [],
            'error': error
        }
    
    def is_whisper_available(self) -> bool:
        """Check if Whisper.cpp is available."""
        return (self.whisper_cli_path is not None and 
                self.whisper_model_path is not None and
                os.path.exists(self.whisper_cli_path) and
                os.path.exists(self.whisper_model_path))
    
    def test_whisper(self) -> str:
        """Test Whisper transcription with sample audio."""
        try:
            if not self.is_whisper_available():
                return "Whisper not available"
            
            # Find sample audio
            project_root = Path(__file__).parent.parent.parent
            sample_path = project_root / "whisper.cpp" / "samples" / "jfk.wav"
            
            if not sample_path.exists():
                return "Sample audio not found"
            
            # Run transcription
            cmd = [
                self.whisper_cli_path,
                '-m', self.whisper_model_path,
                '-f', str(sample_path),
                '--no-timestamps'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                return "Whisper test successful"
            else:
                return f"Whisper test failed: {result.stderr}"
                
        except Exception as e:
            return f"Whisper test error: {e}"
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update analysis settings."""
        if 'thresholds' in settings:
            self.thresholds.update(settings['thresholds'])
        
        if 'filler_words' in settings:
            self.filler_words = settings['filler_words']
        
        logger.info("Speech analyzer settings updated")
