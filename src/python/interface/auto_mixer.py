"""
High-level auto-mixer interface combining C++ performance with Python flexibility.
"""

import numpy as np
from typing import List, Dict, Optional, Union
from pathlib import Path

from ..automixer.pedalboard_processor import PedalboardProcessor
from .audio_file import AudioFile

# Import C++ module when available
try:
    from .. import audio_practice_native as native
    HAS_NATIVE = True
except ImportError:
    HAS_NATIVE = False
    print("Warning: C++ native module not available. Using Python-only mode.")


class AutoMixer:
    """Professional auto-mixing system with intelligent processing."""
    
    def __init__(self, 
                 target_lufs: float = -16.0,
                 use_native: bool = True,
                 sample_rate: int = 48000):
        """
        Initialize AutoMixer.
        
        Args:
            target_lufs: Target loudness in LUFS
            use_native: Use C++ processing when available
            sample_rate: Sample rate for processing
        """
        self.target_lufs = target_lufs
        self.sample_rate = sample_rate
        self.use_native = use_native and HAS_NATIVE
        
        # Initialize processors
        self.pedalboard_processor = PedalboardProcessor(sample_rate)
        
        if self.use_native:
            settings = native.AutoMixerSettings()
            settings.target_lufs = target_lufs
            self.native_mixer = native.AutoMixer(settings)
    
    def process(self, tracks: List[Union[AudioFile, np.ndarray, str]]) -> AudioFile:
        """
        Process multiple tracks and return auto-mixed result.
        
        Args:
            tracks: List of AudioFile objects, numpy arrays, or file paths
            
        Returns:
            AudioFile containing the mixed result
        """
        # Convert all inputs to AudioFile objects
        audio_tracks = []
        for track in tracks:
            if isinstance(track, str) or isinstance(track, Path):
                audio_tracks.append(AudioFile(track))
            elif isinstance(track, np.ndarray):
                af = AudioFile()
                af.set_numpy(track, self.sample_rate)
                audio_tracks.append(af)
            elif isinstance(track, AudioFile):
                audio_tracks.append(track)
            else:
                raise ValueError(f"Unsupported track type: {type(track)}")
        
        # Ensure all tracks have same sample rate
        for track in audio_tracks:
            if track.sample_rate != self.sample_rate:
                track.resample(self.sample_rate)
        
        # Convert to mono for processing
        mono_tracks = [track.to_mono() for track in audio_tracks]
        
        if self.use_native:
            # Use C++ processing
            mixed = self._process_native(mono_tracks)
        else:
            # Use Python processing
            mixed = self._process_python(mono_tracks)
        
        # Create output AudioFile
        result = AudioFile()
        result.set_numpy(mixed, self.sample_rate)
        
        # Convert to stereo
        result.to_stereo()
        
        # Final limiting
        result.normalize(target_db=-0.3)
        
        return result
    
    def _process_native(self, tracks: List[AudioFile]) -> np.ndarray:
        """Process using C++ native mixer."""
        # Convert to native buffers
        native_buffers = []
        for track in tracks:
            audio_data = track.get_numpy()
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(1, -1)
            
            buffer = native.numpy_to_buffer(audio_data)
            native_buffers.append(buffer)
        
        # Process with native mixer
        mixed_buffer = self.native_mixer.process(native_buffers)
        
        # Convert back to numpy
        return native.buffer_to_numpy(mixed_buffer)
    
    def _process_python(self, tracks: List[AudioFile]) -> np.ndarray:
        """Process using Python/Pedalboard."""
        # Create track dictionary for Pedalboard processor
        track_dict = {}
        for i, track in enumerate(tracks):
            audio_data = track.get_numpy()
            if audio_data.ndim > 1:
                audio_data = audio_data[0]  # Take first channel
            track_dict[f"track_{i}"] = audio_data
        
        # Process with Pedalboard
        return self.pedalboard_processor.process_multitrack(track_dict)
    
    def analyze(self, tracks: List[Union[AudioFile, np.ndarray, str]]) -> Dict:
        """
        Analyze tracks and return mixing parameters without processing.
        
        Returns:
            Dictionary containing analysis results
        """
        # Convert inputs
        audio_tracks = []
        for track in tracks:
            if isinstance(track, str) or isinstance(track, Path):
                audio_tracks.append(AudioFile(track))
            elif isinstance(track, np.ndarray):
                af = AudioFile()
                af.set_numpy(track, self.sample_rate)
                audio_tracks.append(af)
            elif isinstance(track, AudioFile):
                audio_tracks.append(track)
        
        analysis = {
            "track_count": len(audio_tracks),
            "track_analyses": []
        }
        
        for i, track in enumerate(audio_tracks):
            track_data = track.get_numpy()
            if track_data.ndim > 1:
                track_data = np.mean(track_data, axis=0)
            
            freq_analysis = self.pedalboard_processor.analyze_frequency_content(track_data)
            
            analysis["track_analyses"].append({
                "index": i,
                "duration": track.duration,
                "channels": track.channels,
                "frequency_analysis": freq_analysis
            })
        
        return analysis
    
    def process_with_settings(self, 
                            tracks: List[Union[AudioFile, np.ndarray, str]],
                            settings: Dict) -> AudioFile:
        """
        Process tracks with custom settings.
        
        Args:
            tracks: Input tracks
            settings: Dictionary of processing settings
            
        Returns:
            Mixed AudioFile
        """
        # Update settings
        if "target_lufs" in settings:
            self.target_lufs = settings["target_lufs"]
            if self.use_native:
                self.native_mixer.settings.target_lufs = settings["target_lufs"]
        
        # Process normally
        return self.process(tracks)
    
    def create_stem_mix(self, 
                       stems: Dict[str, List[Union[AudioFile, np.ndarray, str]]]) -> Dict[str, AudioFile]:
        """
        Create a stem-based mix with separate processing for each stem group.
        
        Args:
            stems: Dictionary mapping stem names to track lists
            
        Returns:
            Dictionary of processed stems
        """
        processed_stems = {}
        
        for stem_name, tracks in stems.items():
            # Process each stem group
            processed = self.process(tracks)
            processed_stems[stem_name] = processed
        
        return processed_stems 