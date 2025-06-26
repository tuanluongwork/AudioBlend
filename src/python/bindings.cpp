#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "core/audio_buffer.h"
#include "dsp/auto_mixer.h"
#include "effects/compressor.h"
#include "effects/equalizer.h"

namespace py = pybind11;
using namespace audio_practice;

// Convert numpy array to AudioBuffer
AudioBuffer numpy_to_buffer(py::array_t<float> input) {
    auto buf = input.request();
    
    if (buf.ndim != 2) {
        throw std::runtime_error("Input should be 2-D (channels x samples)");
    }
    
    size_t channels = buf.shape[0];
    size_t samples = buf.shape[1];
    
    AudioBuffer buffer(channels, samples);
    float* ptr = static_cast<float*>(buf.ptr);
    
    for (size_t ch = 0; ch < channels; ++ch) {
        float* channelData = buffer.getChannelData(ch);
        for (size_t i = 0; i < samples; ++i) {
            channelData[i] = ptr[ch * samples + i];
        }
    }
    
    return buffer;
}

// Convert AudioBuffer to numpy array
py::array_t<float> buffer_to_numpy(const AudioBuffer& buffer) {
    size_t channels = buffer.getNumChannels();
    size_t samples = buffer.getNumSamples();
    
    py::array_t<float> result({channels, samples});
    auto buf = result.request();
    float* ptr = static_cast<float*>(buf.ptr);
    
    for (size_t ch = 0; ch < channels; ++ch) {
        const float* channelData = buffer.getChannelData(ch);
        for (size_t i = 0; i < samples; ++i) {
            ptr[ch * samples + i] = channelData[i];
        }
    }
    
    return result;
}

PYBIND11_MODULE(audio_practice_native, m) {
    m.doc() = "Audio Practice - C++ Audio Processing Library";

    // AudioBuffer
    py::class_<AudioBuffer>(m, "AudioBuffer")
        .def(py::init<size_t, size_t>())
        .def("apply_gain", &AudioBuffer::applyGain)
        .def("clear", &AudioBuffer::clear)
        .def("get_num_channels", &AudioBuffer::getNumChannels)
        .def("get_num_samples", &AudioBuffer::getNumSamples)
        .def("add_from", &AudioBuffer::addFrom, py::arg("other"), py::arg("gain") = 1.0f);

    // AutoMixerSettings
    py::class_<AutoMixerSettings>(m, "AutoMixerSettings")
        .def(py::init<>())
        .def_readwrite("target_lufs", &AutoMixerSettings::targetLUFS)
        .def_readwrite("max_gain_reduction", &AutoMixerSettings::maxGainReduction)
        .def_readwrite("frequency_separation", &AutoMixerSettings::frequencySeparation)
        .def_readwrite("enable_dynamic_eq", &AutoMixerSettings::enableDynamicEQ)
        .def_readwrite("enable_spatial_processing", &AutoMixerSettings::enableSpatialProcessing)
        .def_readwrite("mix_bus_comp_ratio", &AutoMixerSettings::mixBusCompRatio)
        .def_readwrite("mix_bus_comp_threshold", &AutoMixerSettings::mixBusCompThreshold);

    // AutoMixer
    py::class_<AutoMixer>(m, "AutoMixer")
        .def(py::init<const AutoMixerSettings&>(), py::arg("settings") = AutoMixerSettings())
        .def("process", &AutoMixer::process)
        .def("analyze_tracks", &AutoMixer::analyzeTracks);

    // CompressorSettings
    py::class_<CompressorSettings>(m, "CompressorSettings")
        .def(py::init<>())
        .def_readwrite("threshold", &CompressorSettings::threshold)
        .def_readwrite("ratio", &CompressorSettings::ratio)
        .def_readwrite("attack", &CompressorSettings::attack)
        .def_readwrite("release", &CompressorSettings::release)
        .def_readwrite("knee", &CompressorSettings::knee)
        .def_readwrite("makeup_gain", &CompressorSettings::makeupGain);

    // EQBand
    py::class_<EQBand>(m, "EQBand")
        .def(py::init<>())
        .def_readwrite("frequency", &EQBand::frequency)
        .def_readwrite("gain", &EQBand::gain)
        .def_readwrite("q", &EQBand::q);

    // Conversion functions
    m.def("numpy_to_buffer", &numpy_to_buffer, "Convert numpy array to AudioBuffer");
    m.def("buffer_to_numpy", &buffer_to_numpy, "Convert AudioBuffer to numpy array");
} 