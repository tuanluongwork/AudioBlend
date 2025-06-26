"""
AudioPractice - Advanced Auto-Mixing System
A professional-grade audio processing library combining C++ performance with Python flexibility.
"""

from .interface.audio_file import AudioFile
from .interface.auto_mixer import AutoMixer
from .interface.realtime_mixer import RealtimeMixer
from .automixer.pedalboard_processor import PedalboardProcessor

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = ["AudioFile", "AutoMixer", "RealtimeMixer", "PedalboardProcessor"] 