"""
AudioPractice Auto-Mixing Demo
Demonstrates the capabilities of the auto-mixing system.
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "python"))

from audio_practice import AudioFile, AutoMixer, PedalboardProcessor


def generate_test_audio(duration=5.0, sample_rate=48000):
    """Generate test audio tracks for demonstration."""
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    # Generate different test signals
    tracks = {
        "vocals": {
            "audio": np.sin(2 * np.pi * 440 * t) * 0.5 * np.exp(-t/2),  # A4 with decay
            "description": "Simulated vocal (440Hz sine with envelope)"
        },
        "guitar": {
            "audio": (np.sin(2 * np.pi * 220 * t) + 
                     0.3 * np.sin(2 * np.pi * 440 * t) + 
                     0.1 * np.sin(2 * np.pi * 880 * t)) * 0.3,
            "description": "Simulated guitar (harmonic series)"
        },
        "bass": {
            "audio": np.sin(2 * np.pi * 110 * t) * 0.6,  # A2
            "description": "Simulated bass (110Hz sine)"
        },
        "drums": {
            "audio": np.random.normal(0, 0.1, len(t)) * (np.sin(2 * np.pi * 2 * t) > 0),
            "description": "Simulated drums (gated noise)"
        }
    }
    
    return tracks, sample_rate


def demo_basic_mixing():
    """Demonstrate basic auto-mixing functionality."""
    print("=== Basic Auto-Mixing Demo ===\n")
    
    # Generate test tracks
    tracks_data, sr = generate_test_audio()
    
    # Create AudioFile objects
    audio_files = []
    for name, data in tracks_data.items():
        af = AudioFile()
        af.set_numpy(data["audio"].reshape(1, -1), sr)
        audio_files.append(af)
        print(f"Created track: {name} - {data['description']}")
    
    # Initialize auto-mixer
    mixer = AutoMixer(target_lufs=-16.0, use_native=False, sample_rate=sr)
    
    print("\nProcessing tracks...")
    
    # Process tracks
    mixed = mixer.process(audio_files)
    
    print(f"\nMixed result: {mixed}")
    
    # Save result
    output_path = Path("examples/output/basic_mix.wav")
    output_path.parent.mkdir(exist_ok=True)
    mixed.save(output_path)
    print(f"Saved to: {output_path}")


def demo_pedalboard_processing():
    """Demonstrate Pedalboard integration."""
    print("\n=== Pedalboard Processing Demo ===\n")
    
    # Generate test tracks
    tracks_data, sr = generate_test_audio()
    
    # Initialize processor
    processor = PedalboardProcessor(sample_rate=sr)
    
    # Convert to format expected by processor
    track_dict = {name: data["audio"] for name, data in tracks_data.items()}
    
    print("Processing with Pedalboard effects chains...")
    
    # Process
    mixed = processor.process_multitrack(track_dict)
    
    # Create stereo mix
    stereo = processor.create_spatial_mix(track_dict)
    
    # Save results
    output_mono = Path("examples/output/pedalboard_mono.wav")
    output_stereo = Path("examples/output/pedalboard_stereo.wav")
    
    af_mono = AudioFile()
    af_mono.set_numpy(mixed.reshape(1, -1), sr)
    af_mono.save(output_mono)
    
    af_stereo = AudioFile()
    af_stereo.set_numpy(stereo, sr)
    af_stereo.save(output_stereo)
    
    print(f"Saved mono mix to: {output_mono}")
    print(f"Saved stereo mix to: {output_stereo}")


def demo_analysis():
    """Demonstrate track analysis capabilities."""
    print("\n=== Track Analysis Demo ===\n")
    
    # Generate test tracks
    tracks_data, sr = generate_test_audio()
    
    # Create AudioFile objects
    audio_files = []
    track_names = []
    for name, data in tracks_data.items():
        af = AudioFile()
        af.set_numpy(data["audio"].reshape(1, -1), sr)
        audio_files.append(af)
        track_names.append(name)
    
    # Initialize mixer
    mixer = AutoMixer(sample_rate=sr, use_native=False)
    
    # Analyze tracks
    analysis = mixer.analyze(audio_files)
    
    print("Track Analysis Results:")
    print(f"Total tracks: {analysis['track_count']}")
    
    for i, track_analysis in enumerate(analysis['track_analyses']):
        print(f"\n{track_names[i]}:")
        print(f"  Duration: {track_analysis['duration']:.2f}s")
        print(f"  Frequency Analysis:")
        for key, value in track_analysis['frequency_analysis'].items():
            print(f"    {key}: {value:.4f}")


def demo_stem_mixing():
    """Demonstrate stem-based mixing."""
    print("\n=== Stem-Based Mixing Demo ===\n")
    
    # Generate test tracks
    tracks_data, sr = generate_test_audio(duration=3.0)
    
    # Create stems
    stems = {
        "rhythm": ["guitar", "bass"],
        "lead": ["vocals"],
        "percussion": ["drums"]
    }
    
    # Create AudioFile objects organized by stem
    stem_tracks = {}
    for stem_name, track_names in stems.items():
        stem_tracks[stem_name] = []
        for track_name in track_names:
            if track_name in tracks_data:
                af = AudioFile()
                af.set_numpy(tracks_data[track_name]["audio"].reshape(1, -1), sr)
                stem_tracks[stem_name].append(af)
    
    # Initialize mixer
    mixer = AutoMixer(sample_rate=sr, use_native=False)
    
    print("Processing stems separately...")
    
    # Process stems
    processed_stems = mixer.create_stem_mix(stem_tracks)
    
    # Save each stem
    for stem_name, stem_audio in processed_stems.items():
        output_path = Path(f"examples/output/stem_{stem_name}.wav")
        stem_audio.save(output_path)
        print(f"Saved {stem_name} stem to: {output_path}")
    
    # Create final mix from stems
    print("\nMixing stems together...")
    final_mix = mixer.process(list(processed_stems.values()))
    final_path = Path("examples/output/stem_final_mix.wav")
    final_mix.save(final_path)
    print(f"Saved final mix to: {final_path}")


def demo_custom_effects():
    """Demonstrate custom effect chains."""
    print("\n=== Custom Effects Demo ===\n")
    
    from pedalboard import Pedalboard, Reverb, Delay, Chorus, Phaser
    
    # Generate a simple melody
    sr = 48000
    duration = 4.0
    t = np.linspace(0, duration, int(duration * sr))
    
    # Create a simple melody (C major arpeggio)
    notes = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C
    melody = np.zeros_like(t)
    
    for i, note in enumerate(notes):
        start = int(i * sr)
        end = int((i + 1) * sr)
        melody[start:end] = np.sin(2 * np.pi * note * t[start:end]) * 0.5
    
    # Create custom effect chain
    effects = Pedalboard([
        Chorus(rate_hz=1.0, depth=0.25, mix=0.5),
        Delay(delay_seconds=0.25, feedback=0.3, mix=0.3),
        Reverb(room_size=0.5, damping=0.5, wet_level=0.3),
        Phaser(rate_hz=0.5, depth=0.5, mix=0.5)
    ])
    
    # Process
    processed = effects(melody, sr)
    
    # Save
    af = AudioFile()
    af.set_numpy(processed.reshape(1, -1), sr)
    output_path = Path("examples/output/custom_effects.wav")
    af.save(output_path)
    print(f"Saved custom effects demo to: {output_path}")


def main():
    """Run all demos."""
    print("AudioPractice - Auto-Mixing System Demo")
    print("=" * 50)
    
    # Create output directory
    Path("examples/output").mkdir(exist_ok=True)
    
    # Run demos
    demo_basic_mixing()
    demo_pedalboard_processing()
    demo_analysis()
    demo_stem_mixing()
    demo_custom_effects()
    
    print("\n" + "=" * 50)
    print("All demos completed! Check the examples/output directory for results.")


if __name__ == "__main__":
    main() 