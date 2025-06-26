#include "effects/equalizer.h"
#include <cmath>

namespace audio_practice {

Equalizer::Equalizer() {
    // Initialize empty
}

void Equalizer::setBand(size_t index, const EQBand& band) {
    if (index >= bands_.size()) {
        bands_.resize(index + 1);
        coeffs_.resize(index + 1);
        states_.resize(index + 1);
    }
    
    bands_[index] = band;
    updateCoefficients();
}

void Equalizer::clearBands() {
    bands_.clear();
    coeffs_.clear();
    states_.clear();
}

void Equalizer::updateCoefficients(float sampleRate) {
    for (size_t i = 0; i < bands_.size(); ++i) {
        coeffs_[i] = calculateCoeffs(bands_[i], sampleRate);
    }
}

Equalizer::BiquadCoeffs Equalizer::calculateCoeffs(const EQBand& band, float sampleRate) {
    BiquadCoeffs coeffs;
    
    float omega = 2.0f * M_PI * band.frequency / sampleRate;
    float sin_omega = std::sin(omega);
    float cos_omega = std::cos(omega);
    float alpha = sin_omega / (2.0f * band.q);
    float A = std::pow(10.0f, band.gain / 40.0f);
    
    switch (band.type) {
        case EQBand::PEAK: {
            float b0 = 1.0f + alpha * A;
            float b1 = -2.0f * cos_omega;
            float b2 = 1.0f - alpha * A;
            float a0 = 1.0f + alpha / A;
            float a1 = -2.0f * cos_omega;
            float a2 = 1.0f - alpha / A;
            
            // Normalize
            coeffs.a0 = b0 / a0;
            coeffs.a1 = b1 / a0;
            coeffs.a2 = b2 / a0;
            coeffs.b1 = a1 / a0;
            coeffs.b2 = a2 / a0;
            break;
        }
        default:
            // Passthrough for unimplemented types
            coeffs.a0 = 1.0f;
            coeffs.a1 = 0.0f;
            coeffs.a2 = 0.0f;
            coeffs.b1 = 0.0f;
            coeffs.b2 = 0.0f;
            break;
    }
    
    return coeffs;
}

void Equalizer::process(float* data, size_t numSamples) {
    for (size_t band = 0; band < bands_.size(); ++band) {
        auto& coeffs = coeffs_[band];
        auto& state = states_[band];
        
        for (size_t i = 0; i < numSamples; ++i) {
            float input = data[i];
            
            // Biquad filter equation
            float output = coeffs.a0 * input + coeffs.a1 * state.x1 + coeffs.a2 * state.x2
                         - coeffs.b1 * state.y1 - coeffs.b2 * state.y2;
            
            // Update state
            state.x2 = state.x1;
            state.x1 = input;
            state.y2 = state.y1;
            state.y1 = output;
            
            data[i] = output;
        }
    }
}

} // namespace audio_practice 