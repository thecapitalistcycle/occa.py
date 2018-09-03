#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2018 David Medina
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#

from setuptools.command import build_ext
from setuptools import setup, find_packages, Extension
import numpy as np


class OccaInstaller(build_ext.build_ext):
    '''Compile occa.git'''

    def run(self):
        self.spawn([
            'make', '-C', 'occa.git', '-j4',
        ])
        build_ext.build_ext.run(self)


def get_ext_module(name):
    return Extension(
        name='occa.c.{}'.format(name),
        sources=['occa/c/{}.c'.format(name)],
        include_dirs=[
            'occa/c',
            'occa.git/include',
            np.get_include(),
        ],
        libraries=['occa'],
        library_dirs=['occa.git/lib'],
        extra_compile_args=['-Wno-strict-prototypes'],
    )


ext_modules = [
    get_ext_module(mod)
    for mod in ['base', 'device', 'kernel', 'memory', 'uva']
]


long_description = ('''
In a nutshell, OCCA (like oca-rina) is an open-source library which aims to:

- Make it easy to program different types of devices (e.g. CPU, GPU, FPGA)

- Provide a unified API for interacting with backend device APIs (e.g. OpenMP, CUDA, OpenCL)

- Use just-in-time compilation to build backend kernels

- Provide a kernel language, a minor extension to C, to abstract programming for each backend
''')


setup(
    name='occa',
    version='0.2.0',
    description='Portable Approach for Parallel Architectures',
    long_description=long_description,
    cmdclass={
        'build_ext': OccaInstaller,
    },
    packages=find_packages(),
    ext_modules=ext_modules,
    url='https://libocca.org',
    author='David Medina'
)