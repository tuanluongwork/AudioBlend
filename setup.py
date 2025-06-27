"""
Setup script for AudioPractice package.
"""

from setuptools import setup, find_packages, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import glob

# Get all C++ source files
cpp_sources = glob.glob("src/cpp/**/*.cpp", recursive=True)
cpp_sources.append("src/python/bindings.cpp")

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "audio_practice.audio_practice_native",
        cpp_sources,
        include_dirs=["src/cpp"],
        cxx_std=17,
        define_macros=[("VERSION_INFO", "1.0.0")],
    ),
]

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read README
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="audio_practice",
    version="1.0.0",
    author="tuanluongworks",
    author_email="your.email@example.com",
    description="Advanced auto-mixing system with C++ and Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AudioPractice",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
    ],
    keywords="audio processing mixing dsp pedalboard",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AudioPractice/issues",
        "Source": "https://github.com/yourusername/AudioPractice",
    },
) 