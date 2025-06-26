"""
Basic unit tests for AudioPractice.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "python"))

from audio_practice import AudioFile, AutoMixer, PedalboardProcessor


class TestAudioFile:
    """Test AudioFile functionality."""
    
    def test_create_empty(self):
        """Test creating empty AudioFile."""
        af = AudioFile()
        assert af.data is None
        assert af.sample_rate is None
        assert af.duration == 0.0
        assert af.channels == 0
    
    def test_set_numpy(self):
        """Test setting numpy data."""
        af = AudioFile()
        data = np.random.randn(2, 48000)  # 2 channels, 1 second
        af.set_numpy(data, 48000)
        
        assert af.channels == 2
        assert af.sample_rate == 48000
        assert af.duration == 1.0
        assert np.array_equal(af.get_numpy(), data)
    
    def test_mono_stereo_conversion(self):
        """Test mono/stereo conversion."""
        # Start with stereo
        af = AudioFile()
        stereo_data = np.random.randn(2, 1000)
        af.set_numpy(stereo_data, 48000)
        
        # Convert to mono
        af.to_mono()
        assert af.channels == 1
        
        # Convert back to stereo
        af.to_stereo()
        assert af.channels == 2
    
    def test_normalize(self):
        """Test normalization."""
        af = AudioFile()
        data = np.array([[0.1, 0.5, -0.3, 0.8, -0.9]])
        af.set_numpy(data, 48000)
        
        af.normalize(target_db=-6.0)
        normalized = af.get_numpy()
        
        # Check that peak is at target level
        peak = np.max(np.abs(normalized))
        target_linear = 10 ** (-6.0 / 20)
        assert abs(peak - target_linear) < 0.01


class TestAutoMixer:
    """Test AutoMixer functionality."""
    
    def test_initialization(self):
        """Test AutoMixer initialization."""
        mixer = AutoMixer(target_lufs=-16.0, use_native=False)
        assert mixer.target_lufs == -16.0
        assert mixer.sample_rate == 48000
    
    def test_process_empty(self):
        """Test processing empty track list."""
        mixer = AutoMixer(use_native=False)
        result = mixer.process([])
        assert isinstance(result, AudioFile)
    
    def test_process_single_track(self):
        """Test processing single track."""
        mixer = AutoMixer(use_native=False)
        
        # Create test track
        track = AudioFile()
        track.set_numpy(np.random.randn(1, 10000), 48000)
        
        result = mixer.process([track])
        assert isinstance(result, AudioFile)
        assert result.channels == 2  # Should be stereo
        assert result.sample_rate == 48000
    
    def test_analyze(self):
        """Test track analysis."""
        mixer = AutoMixer(use_native=False)
        
        # Create test tracks
        tracks = []
        for i in range(3):
            track = AudioFile()
            track.set_numpy(np.random.randn(1, 5000), 48000)
            tracks.append(track)
        
        analysis = mixer.analyze(tracks)
        
        assert analysis["track_count"] == 3
        assert len(analysis["track_analyses"]) == 3
        assert "frequency_analysis" in analysis["track_analyses"][0]


class TestPedalboardProcessor:
    """Test PedalboardProcessor functionality."""
    
    def test_initialization(self):
        """Test processor initialization."""
        processor = PedalboardProcessor(sample_rate=48000)
        assert processor.sample_rate == 48000
    
    def test_create_chains(self):
        """Test effect chain creation."""
        processor = PedalboardProcessor()
        
        vocal_chain = processor.create_vocal_chain()
        assert len(vocal_chain.plugins) > 0
        
        guitar_chain = processor.create_instrument_chain("guitar")
        assert len(guitar_chain.plugins) > 0
    
    def test_frequency_analysis(self):
        """Test frequency content analysis."""
        processor = PedalboardProcessor(sample_rate=48000)
        
        # Create test signal with known frequency content
        t = np.linspace(0, 1, 48000)
        signal = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
        
        analysis = processor.analyze_frequency_content(signal)
        
        assert "spectral_centroid" in analysis
        assert "bass_energy" in analysis
        assert "mid_energy" in analysis
        assert "high_energy" in analysis
    
    def test_auto_mix_tracks(self):
        """Test automatic track mixing."""
        processor = PedalboardProcessor()
        
        # Create test tracks with different levels
        tracks = {
            "quiet": np.random.randn(1000) * 0.1,
            "loud": np.random.randn(1000) * 0.9,
            "medium": np.random.randn(1000) * 0.5
        }
        
        mixed = processor._auto_mix_tracks(tracks)
        
        assert len(mixed) == 1000
        assert np.max(np.abs(mixed)) <= 1.0  # Should not clip


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 