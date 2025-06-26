#include "dsp/spectrum_analyzer.h"
#include <cmath>

namespace audio_practice {

SpectrumAnalyzer::SpectrumAnalyzer(size_t fftSize) 
    : fftSize_(fftSize) {
    window_.resize(fftSize);
    fftBuffer_.resize(fftSize);
    generateWindow();
}

SpectrumAnalyzer::~SpectrumAnalyzer() = default;

void SpectrumAnalyzer::generateWindow() {
    // Hann window
    for (size_t i = 0; i < fftSize_; ++i) {
        window_[i] = 0.5f * (1.0f - std::cos(2.0f * M_PI * i / (fftSize_ - 1)));
    }
}

std::vector<float> SpectrumAnalyzer::analyze(const float* data, size_t numSamples) {
    std::vector<float> magnitude(fftSize_ / 2 + 1, 0.0f);
    
    // Simple placeholder - in real implementation would use FFT library
    for (size_t i = 0; i < magnitude.size(); ++i) {
        magnitude[i] = 0.1f; // Placeholder
    }
    
    return magnitude;
}

size_t SpectrumAnalyzer::getFrequencyBin(float frequency, float sampleRate) const {
    return static_cast<size_t>(frequency * fftSize_ / sampleRate);
}

float SpectrumAnalyzer::getBinFrequency(size_t bin, float sampleRate) const {
    return bin * sampleRate / fftSize_;
}

void SpectrumAnalyzer::performFFT(std::vector<std::complex<float>>& data) {
    // Placeholder - would use FFT library
}

} // namespace audio_practice 