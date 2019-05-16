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

class Ram:
    '''Help class for decoding RAM data streams.'''

    class G:
       '''The general purpose RAM.'''
       start = 0x000000
       end   = 0x0fffff

    class DL:
        '''The display list RAM.'''
        start = 0x300000
        end   = 0x301fff

    class REG:
        '''The register RAM.'''
        start = 0x302000
        end   = 0x302fff

    class CMD:
        '''The co-processor command circular buffer.'''
        start = 0x308000
        end   = 0x308fff

    def __init__ (self, data, start, addr = 0):
        self._data      = data  # MISO/MOSI data stream
        self._start_i   = start # data list start index
        self.start_addr = addr  # data start address
        self._i         = start # current data list index
        self.addr       = addr  # current data address

    @property
    def end_addr (self):
        return self.addr

    def __len__ (self):
        return self._i - self._start_i

    def __getitem__ (self, key):
        if type(key) is int:
            return self._data[self._i + key]
        elif type(key) is slice:
            start = self._i + (key.start if key.start else 0)
            stop  = self._i + (key.stop  if key.stop  else 0)
            return self._data[start:stop]
        else:
            raise IndexError

    def __iter__ (self):
        return self

    def __next__ (self):
        if self._i >= len(self._data):
            raise StopIteration
        self.next(1)
        return self.__getitem__(0)

    def is_ram_g (self):
        '''Check whether address belongs to RAM_G.'''
        return G.start <= self.val <= G.end

    def is_ram_dl (self):
        '''Check whether address belongs to RAM_DL.'''
        return DL.start <= self.val <= DL.end

    def is_ram_reg (self):
        '''Check whether address belongs to RAM_REG.'''
        return REG.start <= self.val <= REG.end

    def is_ram_cmd (self):
        '''Check whether address belongs to RAM_CMD.'''
        return CMD.start <= self.val <= CMD.end

    def copy (self):
        return copy.copy(self)

    def next (self, offset):
        '''Wraps around the address when needed.'''
        self._i += offset
        if self.is_ram_cmd():
            self.addr = (self.addr + offset) & CMD.start
        else:
            self.addr += offset

