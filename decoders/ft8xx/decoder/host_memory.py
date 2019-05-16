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

import copy
from .base import *
from . import ram_cmd
from .. import datum

class Decoder (Base):
    '''Common decoders for both _Host Memory Read_ and
    _Host Memory Write_ transactions.'''

    def __init__ (self, data, start):
        self._ram = Ram(data, start)
        self.ram_cmd = None

    def decode_data (self, addr):
        '''Decode payload data as plain bytes.'''
        self._ram.start_addr = addr
        data = []
        for d in self._ram:
            data.append(datum.host_memory_write.Data(d, self._ram.addr))
            if not self.ram_cmd and self._ram.is_ram_cmd():
                self.ram_cmd = self._ram.copy()

        return tuple(data)

