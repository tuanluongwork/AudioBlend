#include "effects/compressor.h"
#include <cmath>
#include <algorithm>

namespace audio_practice {

Compressor::Compressor(const CompressorSettings& settings)
    : settings_(settings), envelope_(0.0f), currentGainReduction_(0.0f) {
    updateCoefficients();
}

void Compressor::setSettings(const CompressorSettings& settings) {
    settings_ = settings;
    updateCoefficients();
}

void Compressor::updateCoefficients(float sampleRate) {
    // Convert ms to samples
    float attackSamples = settings_.attack * sampleRate / 1000.0f;
    float releaseSamples = settings_.release * sampleRate / 1000.0f;
    
    // Calculate coefficients
    attackCoeff_ = std::exp(-1.0f / attackSamples);
    releaseCoeff_ = std::exp(-1.0f / releaseSamples);
}

float Compressor::computeGain(float inputLevel) {
    float inputDb = 20.0f * std::log10(std::max(inputLevel, 1e-10f));
    
    // Soft knee compression
    float kneeStart = settings_.threshold - settings_.knee / 2.0f;
    float kneeEnd = settings_.threshold + settings_.knee / 2.0f;
    
    float gainReduction = 0.0f;
    
    if (inputDb > kneeEnd) {
        // Above knee - full compression
        float excess = inputDb - settings_.threshold;
        gainReduction = excess * (1.0f - 1.0f / settings_.ratio);
    } else if (inputDb > kneeStart) {
        // In knee region - smooth transition
        float kneeProgress = (inputDb - kneeStart) / settings_.knee;
        float excess = inputDb - settings_.threshold;
        gainReduction = excess * (1.0f - 1.0f / settings_.ratio) * kneeProgress * kneeProgress;
    }
    
    return std::pow(10.0f, (-gainReduction + settings_.makeupGain) / 20.0f);
}

void Compressor::process(float* data, size_t numSamples) {
    for (size_t i = 0; i < numSamples; ++i) {
        float inputLevel = std::abs(data[i]);
        
        // Update envelope
        if (inputLevel > envelope_) {
            envelope_ = inputLevel + (envelope_ - inputLevel) * attackCoeff_;
        } else {
            envelope_ = inputLevel + (envelope_ - inputLevel) * releaseCoeff_;
        }
        
        // Compute and apply gain
        float gain = computeGain(envelope_);
        data[i] *= gain;
        
        // Update gain reduction meter
        currentGainReduction_ = 20.0f * std::log10(gain);
    }
}

} // namespace audio_practice 