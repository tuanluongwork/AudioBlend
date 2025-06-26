#pragma once

#include <vector>
#include <complex>
#include <memory>

namespace audio_practice {

class SpectrumAnalyzer {
public:
    explicit SpectrumAnalyzer(size_t fftSize = 2048);
    ~SpectrumAnalyzer();

    // Analyze audio buffer and return magnitude spectrum
    std::vector<float> analyze(const float* data, size_t numSamples);
    
    // Get frequency bin for a given frequency
    size_t getFrequencyBin(float frequency, float sampleRate) const;
    
    // Get frequency for a given bin
    float getBinFrequency(size_t bin, float sampleRate) const;

    size_t getFFTSize() const { return fftSize_; }

private:
    size_t fftSize_;
    std::vector<float> window_;
    std::vector<std::complex<float>> fftBuffer_;
    
    void generateWindow();
    void performFFT(std::vector<std::complex<float>>& data);
};

} // namespace audio_practice 