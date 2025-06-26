#pragma once

#include <vector>

namespace audio_practice {

struct EQBand {
    float frequency = 1000.0f;  // Hz
    float gain = 0.0f;          // dB
    float q = 0.7f;             // Q factor
    
    enum Type {
        PEAK,
        HIGH_SHELF,
        LOW_SHELF,
        HIGH_PASS,
        LOW_PASS
    } type = PEAK;
};

class Equalizer {
public:
    Equalizer();
    
    // Add or update an EQ band
    void setBand(size_t index, const EQBand& band);
    
    // Remove all bands
    void clearBands();
    
    // Process audio buffer in-place
    void process(float* data, size_t numSamples);
    
    // Get current bands
    const std::vector<EQBand>& getBands() const { return bands_; }

private:
    std::vector<EQBand> bands_;
    
    struct BiquadCoeffs {
        float a0, a1, a2, b1, b2;
    };
    
    struct BiquadState {
        float x1 = 0, x2 = 0;
        float y1 = 0, y2 = 0;
    };
    
    std::vector<BiquadCoeffs> coeffs_;
    std::vector<BiquadState> states_;
    
    void updateCoefficients(float sampleRate = 48000.0f);
    BiquadCoeffs calculateCoeffs(const EQBand& band, float sampleRate);
};

} // namespace audio_practice 