"""
Audio Manager for Speech Coach Application
Handles audio capture from system audio sources using PyAudio and PulseAudio
"""

import logging
import threading
import time
import numpy as np
import pyaudio
import pulsectl
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AudioManager(QObject):
    """Manages audio capture and processing."""
    
    # Signals
    audio_data_ready = pyqtSignal(np.ndarray)  # Emits audio chunks
    error_occurred = pyqtSignal(str)  # Emits error messages
    
    def __init__(self):
        super().__init__()
        
        # Audio settings
        self.sample_rate = 16000  # 16kHz for Whisper
        self.channels = 1  # Mono
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # Chunking settings for analysis
        self.analysis_chunk_duration = 3.0  # 3 seconds
        self.overlap_duration = 0.5  # 0.5 second overlap
        
        # Audio buffer
        self.audio_buffer = np.array([], dtype=np.int16)
        self.buffer_lock = threading.Lock()
        
        # PyAudio instance
        self.pyaudio_instance = None
        self.stream = None
        self.is_recording = False
        
        # PulseAudio pulse instance
        self.pulse = None
        
        # Recording thread
        self.recording_thread = None
        
        self.initialize_audio_system()
    
    def initialize_audio_system(self):
        """Initialize PyAudio and PulseAudio systems."""
        try:
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Initialize PulseAudio
            self.pulse = pulsectl.Pulse('speech-coach')
            
            logger.info("Audio system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            raise
    
    def get_available_sources(self) -> Dict[str, Any]:
        """Get available audio sources."""
        sources = {}
        
        try:
            if self.pulse:
                # Get monitor sources (for capturing system audio)
                for source in self.pulse.source_list():
                    if 'monitor' in source.name:
                        sources[source.name] = {
                            'description': source.description,
                            'index': source.index,
                            'type': 'monitor'
                        }
                
                # Get regular input sources
                for source in self.pulse.source_list():
                    if 'monitor' not in source.name:
                        sources[source.name] = {
                            'description': source.description,
                            'index': source.index,
                            'type': 'input'
                        }
            
            logger.info(f"Found {len(sources)} audio sources")
            return sources
            
        except Exception as e:
            logger.error(f"Error getting audio sources: {e}")
            return {}
    
    def get_default_monitor_source(self) -> Optional[str]:
        """Get the default monitor source for system audio capture."""
        try:
            sources = self.get_available_sources()
            
            # Look for common monitor source names
            monitor_names = [
                'auto_null.monitor',
                'alsa_output.pci-0000_00_1f.3.analog-stereo.monitor',
                'alsa_output.platform-snd_aloop.0.analog-stereo.monitor'
            ]
            
            for name in monitor_names:
                if name in sources:
                    logger.info(f"Found default monitor source: {name}")
                    return name
            
            # Fallback to first monitor source found
            for name, info in sources.items():
                if info['type'] == 'monitor':
                    logger.info(f"Using fallback monitor source: {name}")
                    return name
            
            logger.warning("No monitor sources found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting default monitor source: {e}")
            return None
    
    def start_recording(self, source_name: Optional[str] = None):
        """Start recording audio."""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        try:
            # Ensure audio system is initialized
            if self.pyaudio_instance is None or self.pulse is None:
                self.initialize_audio_system()
                if self.pyaudio_instance is None or self.pulse is None:
                    raise Exception("Audio system not initialized properly")
            
            # Use default monitor source if none specified
            if source_name is None:
                source_name = self.get_default_monitor_source()
                if source_name is None:
                    raise Exception("No suitable audio source found")
            
            # Clear buffer
            with self.buffer_lock:
                self.audio_buffer = np.array([], dtype=np.int16)
            
            # Create audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            # Start recording
            self.is_recording = True
            self.stream.start_stream()
            
            # Start processing thread
            self.recording_thread = threading.Thread(target=self._process_audio_buffer)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            logger.info(f"Started recording from source: {source_name}")
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.error_occurred.emit(str(e))
            raise
    
    def stop_recording(self):
        """Stop recording audio."""
        if not self.is_recording:
            logger.warning("Not currently recording")
            return
        
        try:
            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Wait for processing thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=2.0)
            
            logger.info("Stopped recording")
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self.error_occurred.emit(str(e))
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for incoming audio data."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Add to buffer
        with self.buffer_lock:
            self.audio_buffer = np.append(self.audio_buffer, audio_data)
        
        return (None, pyaudio.paContinue)
    
    def _process_audio_buffer(self):
        """Process audio buffer and emit chunks for analysis."""
        analysis_chunk_samples = int(self.analysis_chunk_duration * self.sample_rate)
        overlap_samples = int(self.overlap_duration * self.sample_rate)
        step_samples = analysis_chunk_samples - overlap_samples
        
        last_emit_time = 0
        
        while self.is_recording:
            try:
                with self.buffer_lock:
                    buffer_length = len(self.audio_buffer)
                
                # Check if we have enough data for a chunk
                if buffer_length >= analysis_chunk_samples:
                    with self.buffer_lock:
                        # Extract chunk
                        chunk = self.audio_buffer[:analysis_chunk_samples].copy()
                        
                        # Remove processed samples (keeping overlap)
                        self.audio_buffer = self.audio_buffer[step_samples:]
                    
                    # Emit chunk for analysis
                    current_time = time.time()
                    if current_time - last_emit_time >= 0.1:  # Limit to 10 Hz
                        self.audio_data_ready.emit(chunk)
                        last_emit_time = current_time
                
                # Sleep briefly to prevent busy waiting
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in audio processing: {e}")
                self.error_occurred.emit(str(e))
                break
    
    def is_available(self) -> bool:
        """Check if audio system is available."""
        try:
            return (self.pyaudio_instance is not None and 
                    self.pulse is not None and 
                    len(self.get_available_sources()) > 0)
        except:
            return False
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update audio settings."""
        if 'sample_rate' in settings:
            self.sample_rate = settings['sample_rate']
        
        if 'chunk_duration' in settings:
            self.analysis_chunk_duration = settings['chunk_duration']
        
        if 'overlap_duration' in settings:
            self.overlap_duration = settings['overlap_duration']
        
        logger.info("Audio settings updated")
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            self.stop_recording()
            
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            if self.pulse:
                self.pulse.close()
                self.pulse = None
            
            logger.info("Audio system cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_audio_level(self) -> float:
        """Get current audio level (RMS)."""
        try:
            with self.buffer_lock:
                if len(self.audio_buffer) == 0:
                    return 0.0
                
                # Calculate RMS of recent samples
                recent_samples = self.audio_buffer[-1024:] if len(self.audio_buffer) > 1024 else self.audio_buffer
                rms = np.sqrt(np.mean(recent_samples.astype(np.float64) ** 2))
                
                # Normalize to 0-1 range
                return min(rms / 32767.0, 1.0)
                
        except Exception as e:
            logger.error(f"Error calculating audio level: {e}")
            return 0.0
