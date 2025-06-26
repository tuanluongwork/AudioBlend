#pragma once

#include "core/audio_buffer.h"
#include "dsp/spectrum_analyzer.h"
#include "effects/compressor.h"
#include "effects/equalizer.h"
#include <vector>
#include <memory>

namespace audio_practice {

struct AutoMixerSettings {
    float targetLUFS = -16.0f;          // Target loudness
    float maxGainReduction = 12.0f;    // Maximum gain reduction in dB
    float frequencySeparation = 3.0f;   // Minimum frequency separation in dB
    bool enableDynamicEQ = true;        // Enable dynamic EQ adjustments
    bool enableSpatialProcessing = true; // Enable auto-panning
    float mixBusCompRatio = 2.0f;      // Mix bus compression ratio
    float mixBusCompThreshold = -6.0f; // Mix bus compression threshold
};

class AutoMixer {
public:
    explicit AutoMixer(const AutoMixerSettings& settings = {})
        : settings_(settings) {
        initializeProcessors();
    }

    // Process multiple tracks and return mixed result
    AudioBuffer process(const std::vector<AudioBuffer>& tracks);

    // Analyze tracks and compute optimal mixing parameters
    struct MixParameters {
        std::vector<float> trackGains;
        std::vector<std::vector<EQBand>> trackEQs;
        std::vector<float> panPositions;
        CompressorSettings mixBusCompressor;
    };

    MixParameters analyzeTracks(const std::vector<AudioBuffer>& tracks);

private:
    AutoMixerSettings settings_;
    std::unique_ptr<SpectrumAnalyzer> analyzer_;
    std::unique_ptr<Compressor> mixBusCompressor_;
    std::vector<std::unique_ptr<Equalizer>> trackEQs_;

    void initializeProcessors();
    
    // Level balancing using LUFS measurement
    std::vector<float> calculateOptimalLevels(
        const std::vector<AudioBuffer>& tracks);
    
    // Frequency conflict resolution
    void resolveFrequencyConflicts(
        const std::vector<AudioBuffer>& tracks,
        std::vector<std::vector<EQBand>>& eqSettings);
    
    // Automatic spatial positioning
    std::vector<float> calculatePanPositions(
        const std::vector<AudioBuffer>& tracks);
    
    // Apply processing to individual track
    void processTrack(AudioBuffer& track, 
                     float gain,
                     const std::vector<EQBand>& eqBands,
                     float pan);
    
    // LUFS measurement
    float measureLUFS(const AudioBuffer& buffer);
    
    // Spectral centroid for pan positioning
    float calculateSpectralCentroid(const AudioBuffer& buffer);
};

} // namespace audio_practice 