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
from .  import host_memory
from .. import datum

class Decoder (host_memory.Decoder):
    '''Decoder for _Host Memory Write_ transactions.'''

    def __init__ (self, mosi):
        super().__init__(mosi, 3)
        self._decoder.mem_read = False

    def decode (self):
        '''Decode an _Host Memory Write_ transaction.'''
        addr = datum.host_memory.Address(self.data[0:3])
        data = self.decode_data(addr.val)
        dset = datum.host_memory.DataSet(data)
        if RAM_CMD.start <= addr.val <= RAM_CMD.end:
            ram_cmd = self.decode_ram_cmd()
        return datum.host_memory_write.Transaction(addr, dset)

