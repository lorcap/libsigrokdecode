##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2018 Lorenzo Cappelletti <lorenzo.cappelletti@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

from .base import *
from .ram import Ram
from .. import datum

class Decoder:
    '''Decoder of commands to/from RAM_CMD.'''

    def __init__ (self, ram):
        self._ram     = ram           # Ram object
        self.warnings = WarningList() # list of warnings

    def decode (self):
        '''Decode a stream of commands.'''
        while self.i < len(sel.data):
            try:
                decode_command()
            except AttributeError:
                w = datum.Warning(self.data[self.i].ss,
                                  self.data[-1].es,
                                  '(unhandled)')
                self.warnings.append(w)
                self.i = len(self.data)
            except IndexError:
                w = datum.Warning(self.data[self.i].ss,
                                  self.data[-1].es,
                                  '(truncated)')
                self.warnings.append(w)
                self.i = len(self.data)


    def decode_command (self):
        '''Decode command for co-processor.'''
        cmd = datum.uint(self._ram[0:4])
        msb = cmd >> 24
        name = 'handle_0x' + (f'{cmd:08x}' if msb == 0xff else f'{msb:02x}')
        attr = getattr(self, name)
        return attr()

    def handle_0x05 (self):
        return handle_xx('BitmapHandle', (4, 0))

    def handle_0x07 (self):
        return handle_xx('BitmapLayout', (23, 19), (18, 9), (8, 0))

    def handle_0x09 (self):
        return handle_xx('AlphaFunc', (10, 8), ( 7, 0))

    def handle_0x1f (self):
        return handle_xx('Begin', (3, 0))

    def handle_xx (self, name, *param):
        attr = getattr(datum.host_memory, name)
        data = self._ram[0:4]
        val  = datum.uint(data)
        par  = (bit(val, start, end) for start, end in param)
        self._ram.next(4)
        return attr(data, *par)

