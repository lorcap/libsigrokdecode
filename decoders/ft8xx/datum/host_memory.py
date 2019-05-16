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

class Address (Base):
    '''Data type for Host Memory Read/Write's address.'''

    def __init__ (self, data):
        addr = uint(data) & 0x3fffff
        super().__init__(
                start  =data[0].ss,
                end    =data[2].es,
                val    =addr,
                ann_id =self._decoder.AnnId.READ_ADDRESS if self._decoder.mem_read else
                        self._decoder.AnnId.WRITE_ADDRESS,
                ann_str=[f'Address: 0x{addr:06X}',
                         f'Addr: {addr:X}',
                         f'{addr:X}'])

class Data (Base):
    '''Type for Host Memory Read/Write's plain data.'''

    def __init__ (self, data, addr):
        super().__init__(
                start  =data.ss,
                end    =data.es,
                val    =data.val,
                ann_id =self._decoder.AnnId.READ_DATA if self._decoder.mem_read else
                        self._decoder.AnnId.WRITE_DATA,
                ann_str=[f'0x{data.val:02X} @ 0x{addr:06X}',
                         f'{data.val:X}@{addr:X}',
                         f'{data.val:X}'])

class DataSet (Base):
    '''Type for Host Memory Read/Write's data set.'''

    def __init__ (self, data):
        self.data = data # list of data
        super().__init__(
                start=data[ 0].start,
                end  =data[-1].end,
                val  =len(data))

    def put_ann (self):
        for d in self.data:
            d.put_ann()

