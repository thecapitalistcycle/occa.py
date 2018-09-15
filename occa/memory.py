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
import json
import numpy as np

from . import c, utils
from .exceptions import UninitializedError


class Memory:
    def __init__(self, c_memory=None, dtype=None):
        if c_memory:
            utils.assert_c_memory(c_memory)
            utils.assert_valid_dtype(dtype)
            self._c = c_memory
            self.dtype = np.dtype(dtype)
        else:
            self._c = None

    def _assert_initialized(self):
        if not self.is_initialized:
            raise UninitializedError('occa.Memory is not initialized')

    def _to_occa_kernel_arg(self):
        return self._c

    @property
    def is_initialized(self):
        '''Return if the memory has been initialized'''
        return (self._c is not None and
                self._c.is_initialized())

    def free(self):
        self._assert_initialized()
        self._c.free()

    @property
    def device(self):
        from .device import Device

        self._assert_initialized()
        return Device(self._c.get_device())

    @property
    def mode(self):
        self._assert_initialized()
        return self._c.mode()

    @property
    def bytes(self):
        self._assert_initialized()
        return self._c.size()

    @property
    def properties(self):
        self._assert_initialized()
        return json.loads(self._c.properties())

    def __getitem__(self, key):
        self._assert_initialized()
        if (not isinstance(key, slice) or
            key.step != 1):
            raise KeyError('Only accepts slices with step of 1(e.g. mem[:-10])')
        return Memory(
            self._c.slice(offset=key.start,
                          bytes=(key.end - key.start))
        )

    def copy_to(self, dest,
                entries=None,
                src_offset=0,
                dest_offset=0,
                src_buffer=None,
                dest_buffer=None,
                props=None):
        from .base import memcpy

        self._assert_initialized()
        memcpy(dest=dest,
               src=self,
               entries=entries,
               src_offset=src_offset,
               dest_offset=dest_offset,
               src_buffer=src_buffer,
               dest_buffer=dest_buffer,
               props=props)

    def copy_from(self, src,
                  entries=None,
                  src_offset=0,
                  dest_offset=0,
                  src_buffer=None,
                  dest_buffer=None,
                  props=None):
        from .base import memcpy

        self._assert_initialized()
        memcpy(dest=self,
               src=src,
               entries=entries,
               src_offset=src_offset,
               dest_offset=dest_offset,
               src_buffer=src_buffer,
               dest_buffer=dest_buffer,
               props=props)

    def clone(self):
        self._assert_initialized()
        return Memory(self._c.clone())

    def to_ndarray(self):
        array = np.zeros(len(self), dtype=self.dtype)
        self.copy_to(array)
        return array

    def __bool__(self):
        return self.is_initialized

    def __len__(self):
        self._assert_initialized()
        return int(self._c.size() / self.dtype.itemsize)

    def __eq__(self, other):
        self._assert_initialized()
        if not isinstance(other, Memory):
            return False
        return hash(self) == hash(other)

    def __hash__(self):
        self._assert_initialized()
        return self._c.ptr_as_long()
