#pragma once

namespace audio_practice {

struct CompressorSettings {
    float threshold = -12.0f;  // dB
    float ratio = 4.0f;        // compression ratio
    float attack = 10.0f;      // ms
    float release = 100.0f;    // ms
    float knee = 2.0f;         // dB
    float makeupGain = 0.0f;   // dB
};

class Compressor {
public:
    explicit Compressor(const CompressorSettings& settings = {});
    
    void setSettings(const CompressorSettings& settings);
    const CompressorSettings& getSettings() const { return settings_; }
    
    // Process audio buffer in-place
    void process(float* data, size_t numSamples);
    
    // Get current gain reduction in dB
    float getGainReduction() const { return currentGainReduction_; }

private:
    CompressorSettings settings_;
    float envelope_;
    float currentGainReduction_;
    
    float attackCoeff_;
    float releaseCoeff_;
    
    void updateCoefficients(float sampleRate = 48000.0f);
    float computeGain(float inputLevel);
};

} // namespace audio_practice 