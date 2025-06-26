"""
Audio file handling with automatic format detection and conversion.
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Union, Tuple, Optional


class AudioFile:
    """High-level audio file interface."""
    
    def __init__(self, filepath: Union[str, Path] = None):
        self.filepath = Path(filepath) if filepath else None
        self.data = None
        self.sample_rate = None
        
        if self.filepath and self.filepath.exists():
            self.load()
    
    def load(self, filepath: Union[str, Path] = None) -> 'AudioFile':
        """Load audio from file."""
        if filepath:
            self.filepath = Path(filepath)
        
        if not self.filepath or not self.filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {self.filepath}")
        
        self.data, self.sample_rate = sf.read(str(self.filepath), always_2d=True)
        self.data = self.data.T  # Convert to channels-first format
        
        return self
    
    def save(self, filepath: Union[str, Path], sample_rate: Optional[int] = None) -> None:
        """Save audio to file."""
        if self.data is None:
            raise ValueError("No audio data to save")
        
        filepath = Path(filepath)
        sample_rate = sample_rate or self.sample_rate or 48000
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to samples-first format for soundfile
        data_to_save = self.data.T if self.data.ndim == 2 else self.data
        
        sf.write(str(filepath), data_to_save, sample_rate)
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        if self.data is None or self.sample_rate is None:
            return 0.0
        return self.data.shape[-1] / self.sample_rate
    
    @property
    def channels(self) -> int:
        """Get number of channels."""
        if self.data is None:
            return 0
        return self.data.shape[0] if self.data.ndim == 2 else 1
    
    def to_mono(self) -> 'AudioFile':
        """Convert to mono."""
        if self.data is None:
            return self
        
        if self.channels > 1:
            self.data = np.mean(self.data, axis=0, keepdims=True)
        
        return self
    
    def to_stereo(self) -> 'AudioFile':
        """Convert to stereo."""
        if self.data is None:
            return self
        
        if self.channels == 1:
            self.data = np.repeat(self.data, 2, axis=0)
        elif self.channels > 2:
            self.data = self.data[:2]
        
        return self
    
    def normalize(self, target_db: float = -3.0) -> 'AudioFile':
        """Normalize audio to target dB level."""
        if self.data is None:
            return self
        
        # Calculate current peak
        current_peak = np.max(np.abs(self.data))
        
        if current_peak > 0:
            # Convert dB to linear
            target_linear = 10 ** (target_db / 20)
            
            # Calculate gain
            gain = target_linear / current_peak
            
            # Apply gain
            self.data = self.data * gain
        
        return self
    
    def trim_silence(self, threshold_db: float = -40.0) -> 'AudioFile':
        """Trim silence from beginning and end."""
        if self.data is None:
            return self
        
        # Convert threshold to linear
        threshold = 10 ** (threshold_db / 20)
        
        # Find non-silent samples
        energy = np.max(np.abs(self.data), axis=0)
        non_silent = np.where(energy > threshold)[0]
        
        if len(non_silent) > 0:
            start = non_silent[0]
            end = non_silent[-1] + 1
            self.data = self.data[:, start:end]
        
        return self
    
    def resample(self, target_sr: int) -> 'AudioFile':
        """Resample to target sample rate."""
        if self.data is None or self.sample_rate == target_sr:
            return self
        
        import librosa
        
        # Resample each channel
        resampled_channels = []
        for channel in self.data:
            resampled = librosa.resample(
                channel, 
                orig_sr=self.sample_rate, 
                target_sr=target_sr
            )
            resampled_channels.append(resampled)
        
        self.data = np.array(resampled_channels)
        self.sample_rate = target_sr
        
        return self
    
    def get_numpy(self) -> np.ndarray:
        """Get audio data as numpy array."""
        return self.data.copy() if self.data is not None else np.array([])
    
    def set_numpy(self, data: np.ndarray, sample_rate: int = 48000) -> 'AudioFile':
        """Set audio data from numpy array."""
        self.data = data.copy()
        self.sample_rate = sample_rate
        return self
    
    def __repr__(self) -> str:
        if self.data is None:
            return "AudioFile(empty)"
        return f"AudioFile(channels={self.channels}, duration={self.duration:.2f}s, sr={self.sample_rate})" 