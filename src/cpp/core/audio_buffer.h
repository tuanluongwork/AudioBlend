#pragma once

#include <vector>
#include <memory>
#include <cstring>
#include <algorithm>
#include <immintrin.h>

namespace audio_practice {

class AudioBuffer {
public:
    AudioBuffer(size_t channels, size_t samples)
        : channels_(channels), samples_(samples) {
        data_.resize(channels);
        for (auto& channel : data_) {
            channel.resize(samples, 0.0f);
        }
    }

    // Get raw pointer to channel data
    float* getChannelData(size_t channel) {
        return data_[channel].data();
    }

    const float* getChannelData(size_t channel) const {
        return data_[channel].data();
    }

    // SIMD-optimized operations
    void applyGain(float gain) {
        const __m256 gain_vec = _mm256_set1_ps(gain);
        
        for (auto& channel : data_) {
            size_t i = 0;
            for (; i + 8 <= channel.size(); i += 8) {
                __m256 samples = _mm256_loadu_ps(&channel[i]);
                samples = _mm256_mul_ps(samples, gain_vec);
                _mm256_storeu_ps(&channel[i], samples);
            }
            
            // Handle remaining samples
            for (; i < channel.size(); ++i) {
                channel[i] *= gain;
            }
        }
    }

    void clear() {
        for (auto& channel : data_) {
            std::fill(channel.begin(), channel.end(), 0.0f);
        }
    }

    size_t getNumChannels() const { return channels_; }
    size_t getNumSamples() const { return samples_; }

    // Mix another buffer into this one
    void addFrom(const AudioBuffer& other, float gain = 1.0f) {
        const size_t numChannels = std::min(channels_, other.channels_);
        const size_t numSamples = std::min(samples_, other.samples_);
        
        const __m256 gain_vec = _mm256_set1_ps(gain);
        
        for (size_t ch = 0; ch < numChannels; ++ch) {
            float* dst = getChannelData(ch);
            const float* src = other.getChannelData(ch);
            
            size_t i = 0;
            for (; i + 8 <= numSamples; i += 8) {
                __m256 dst_samples = _mm256_loadu_ps(&dst[i]);
                __m256 src_samples = _mm256_loadu_ps(&src[i]);
                src_samples = _mm256_mul_ps(src_samples, gain_vec);
                dst_samples = _mm256_add_ps(dst_samples, src_samples);
                _mm256_storeu_ps(&dst[i], dst_samples);
            }
            
            for (; i < numSamples; ++i) {
                dst[i] += src[i] * gain;
            }
        }
    }

private:
    size_t channels_;
    size_t samples_;
    std::vector<std::vector<float>> data_;
};

} // namespace audio_practice 