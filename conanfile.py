#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class PrometheuscppConan(ConanFile):
    name = "prometheus-cpp"
    version = "0.7.0"
    description = "Prometheus Client Library for Modern C++"
    topics = ("conan", "prometheuscpp")
    url = "https://github.com/zinnion/conan-prometheus-cpp"
    homepage = "https://github.com/jupp0r/prometheus-cpp"
    author = "Zinnion <mauro@zinnion.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    short_paths = True
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'enable_pull': [True, False],
        'enable_push': [True, False],
        'enable_compression': [True, False],
        'override_cxx_standard_flags': [True, False],
        }
    default_options = {
        'shared': False,
        'fPIC': True,
        'enable_pull': True,
        'enable_push': True,
        'enable_compression': True,
        'override_cxx_standard_flags': True,
        }

    def source(self):
        self.run("git clone https://github.com/jupp0r/prometheus-cpp.git source_subfolder")
        self.run("cd source_subfolder && git checkout -b e14ba41")

    def requirements(self):
        self.requires.add('zlib/1.2.11@zinnion/stable')
        if self.options.enable_push:
            self.requires.add('libcurl/7.64.1@zinnion/stable')
            if self.options.enable_pull:
                # required to resolve version mismatch between civetweb and libcurl
                self.requires('OpenSSL/1.1.1b@zinnion/stable')

    def configure(self):
        del self.settings.compiler.libcxx

    def configure_cmake(self):
        cmake = CMake(self)

        opts = dict()
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['ENABLE_PULL'] = self.options.enable_pull
        cmake.definitions['ENABLE_PUSH'] = self.options.enable_push
        cmake.definitions['ENABLE_COMPRESSION'] = self.options.enable_compression
        cmake.definitions['OVERRIDE_CXX_STANDARD_FLAGS'] = self.options.override_cxx_standard_flags
        cmake.configure(defs=opts, source_folder=self.source_subfolder, build_folder=self.build_subfolder)
        return cmake

    def build(self):
        self.run("cd source_subfolder && git submodule init")
        self.run("cd source_subfolder && git submodule update")
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        cmake = self.configure_cmake()
        self.copy(pattern="LICENSE.txt", dst="license", src=self.source_subfolder)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.append("prometheus-cpp-core")
        if self.options.enable_pull:
            self.cpp_info.libs.append('prometheus-cpp-pull')
        if self.options.enable_push:
            self.cpp_info.libs.append('prometheus-cpp-push')
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
            self.cpp_info.libs.append('rt')
            if self.options.shared:
                self.cpp_info.libs.append('dl')
        # gcc's atomic library not linked automatically on clang
        if self.settings.compiler == 'clang':
            self.cpp_info.libs.append('atomic')
