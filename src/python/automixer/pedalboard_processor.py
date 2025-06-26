"""
Pedalboard-based audio processor for auto-mixing applications.
Demonstrates integration with Spotify's Pedalboard library.
"""

import numpy as np
from pedalboard import (
    Pedalboard, Compressor, Gain, HighpassFilter, 
    LowpassFilter, PeakFilter, Reverb, Limiter,
    NoiseGate, Chorus, Delay
)
from pedalboard.io import AudioFile
import librosa
from typing import List, Dict, Tuple, Optional


class PedalboardProcessor:
    """Advanced audio processor using Pedalboard for auto-mixing."""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        self.board = Pedalboard()
        
    def create_vocal_chain(self) -> Pedalboard:
        """Create an effects chain optimized for vocals."""
        return Pedalboard([
            NoiseGate(threshold_db=-45, ratio=10, attack_ms=1, release_ms=100),
            HighpassFilter(cutoff_frequency_hz=80),
            Compressor(threshold_db=-18, ratio=3, attack_ms=5, release_ms=50),
            PeakFilter(frequency_hz=3000, gain_db=2, q=0.7),  # Presence boost
            PeakFilter(frequency_hz=200, gain_db=-2, q=0.5),  # Reduce muddiness
            Reverb(room_size=0.15, damping=0.7, wet_level=0.15),
            Limiter(threshold_db=-1, release_ms=50)
        ])
    
    def create_instrument_chain(self, instrument_type: str) -> Pedalboard:
        """Create effects chains for different instruments."""
        chains = {
            "guitar": Pedalboard([
                NoiseGate(threshold_db=-40),
                Compressor(threshold_db=-12, ratio=2.5),
                PeakFilter(frequency_hz=2500, gain_db=1.5, q=0.7),
                Chorus(rate_hz=1.5, depth=0.25, mix=0.3)
            ]),
            "bass": Pedalboard([
                HighpassFilter(cutoff_frequency_hz=30),
                Compressor(threshold_db=-15, ratio=4, attack_ms=10),
                PeakFilter(frequency_hz=100, gain_db=2, q=0.5),
                LowpassFilter(cutoff_frequency_hz=5000)
            ]),
            "drums": Pedalboard([
                Compressor(threshold_db=-10, ratio=3, attack_ms=1, release_ms=100),
                PeakFilter(frequency_hz=60, gain_db=3, q=0.7),  # Kick punch
                PeakFilter(frequency_hz=5000, gain_db=2, q=0.5),  # Snap
                Limiter(threshold_db=-3)
            ])
        }
        return chains.get(instrument_type, Pedalboard())
    
    def analyze_frequency_content(self, audio: np.ndarray) -> Dict[str, float]:
        """Analyze frequency content of audio signal."""
        # Compute spectral features
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio, sr=self.sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, sr=self.sample_rate)[0]
        
        # Compute energy in different frequency bands
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        
        # Define frequency bands
        bass_mask = (freqs >= 20) & (freqs <= 250)
        mid_mask = (freqs > 250) & (freqs <= 2000)
        high_mask = (freqs > 2000) & (freqs <= 8000)
        
        bass_energy = np.mean(magnitude[bass_mask, :])
        mid_energy = np.mean(magnitude[mid_mask, :])
        high_energy = np.mean(magnitude[high_mask, :])
        
        return {
            "spectral_centroid": np.mean(spectral_centroid),
            "spectral_rolloff": np.mean(spectral_rolloff),
            "bass_energy": bass_energy,
            "mid_energy": mid_energy,
            "high_energy": high_energy
        }
    
    def auto_eq(self, audio: np.ndarray, target_curve: Optional[Dict] = None) -> Pedalboard:
        """Create automatic EQ based on frequency analysis."""
        analysis = self.analyze_frequency_content(audio)
        
        # Default target curve (can be customized)
        if target_curve is None:
            target_curve = {
                "bass_energy": 0.3,
                "mid_energy": 0.5,
                "high_energy": 0.2
            }
        
        eq_chain = []
        
        # Adjust bass
        bass_diff = analysis["bass_energy"] - target_curve["bass_energy"]
        if abs(bass_diff) > 0.1:
            gain = -10 * bass_diff  # Convert to dB
            eq_chain.append(PeakFilter(frequency_hz=100, gain_db=gain, q=0.7))
        
        # Adjust mids
        mid_diff = analysis["mid_energy"] - target_curve["mid_energy"]
        if abs(mid_diff) > 0.1:
            gain = -8 * mid_diff
            eq_chain.append(PeakFilter(frequency_hz=1000, gain_db=gain, q=0.7))
        
        # Adjust highs
        high_diff = analysis["high_energy"] - target_curve["high_energy"]
        if abs(high_diff) > 0.1:
            gain = -6 * high_diff
            eq_chain.append(PeakFilter(frequency_hz=5000, gain_db=gain, q=0.7))
        
        return Pedalboard(eq_chain)
    
    def process_multitrack(self, tracks: Dict[str, np.ndarray]) -> np.ndarray:
        """Process multiple tracks with automatic mixing."""
        processed_tracks = {}
        
        # Process each track with appropriate chain
        for track_name, audio in tracks.items():
            if "vocal" in track_name.lower():
                chain = self.create_vocal_chain()
            elif "guitar" in track_name.lower():
                chain = self.create_instrument_chain("guitar")
            elif "bass" in track_name.lower():
                chain = self.create_instrument_chain("bass")
            elif "drum" in track_name.lower():
                chain = self.create_instrument_chain("drums")
            else:
                chain = Pedalboard()
            
            # Apply auto-EQ
            auto_eq_chain = self.auto_eq(audio)
            combined_chain = Pedalboard(chain.plugins + auto_eq_chain.plugins)
            
            # Process the audio
            processed = combined_chain(audio, self.sample_rate)
            processed_tracks[track_name] = processed
        
        # Mix tracks with automatic leveling
        mixed = self._auto_mix_tracks(processed_tracks)
        
        # Apply mix bus processing
        mix_bus_chain = Pedalboard([
            Compressor(threshold_db=-6, ratio=2, attack_ms=10, release_ms=100),
            Limiter(threshold_db=-0.3, release_ms=50)
        ])
        
        return mix_bus_chain(mixed, self.sample_rate)
    
    def _auto_mix_tracks(self, tracks: Dict[str, np.ndarray]) -> np.ndarray:
        """Automatically mix tracks with intelligent leveling."""
        if not tracks:
            return np.array([])
        
        # Calculate RMS levels
        rms_levels = {}
        for name, audio in tracks.items():
            rms = np.sqrt(np.mean(audio ** 2))
            rms_levels[name] = rms
        
        # Target RMS level (average of all tracks)
        target_rms = np.mean(list(rms_levels.values()))
        
        # Mix with adjusted levels
        max_length = max(len(audio) for audio in tracks.values())
        mixed = np.zeros(max_length)
        
        for name, audio in tracks.items():
            # Calculate gain to reach target RMS
            current_rms = rms_levels[name]
            if current_rms > 0:
                gain = target_rms / current_rms
                # Limit gain adjustment
                gain = np.clip(gain, 0.1, 10.0)
            else:
                gain = 1.0
            
            # Apply gain and add to mix
            adjusted = audio * gain
            mixed[:len(adjusted)] += adjusted
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 0.95:
            mixed = mixed * (0.95 / max_val)
        
        return mixed
    
    def create_spatial_mix(self, tracks: Dict[str, np.ndarray]) -> np.ndarray:
        """Create a spatial stereo mix from mono tracks."""
        if not tracks:
            return np.array([[], []])
        
        max_length = max(len(audio) for audio in tracks.values())
        stereo_mix = np.zeros((2, max_length))
        
        # Distribute tracks across stereo field
        num_tracks = len(tracks)
        positions = np.linspace(-0.8, 0.8, num_tracks)
        
        for (name, audio), pan in zip(tracks.items(), positions):
            # Convert mono to stereo with panning
            left_gain = np.sqrt(0.5 * (1.0 - pan))
            right_gain = np.sqrt(0.5 * (1.0 + pan))
            
            stereo_mix[0, :len(audio)] += audio * left_gain
            stereo_mix[1, :len(audio)] += audio * right_gain
        
        return stereo_mix 