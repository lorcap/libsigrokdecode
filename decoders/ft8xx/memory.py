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

from collections import namedtuple as nt
from . import annotation as ann

def ram_str (addr):
    if   0x000000 <= addr <= 0x0fffff: return 'RAM_G'
    elif 0x300000 <= addr <= 0x301fff: return 'RAM_DL'
    elif 0x302000 <= addr <= 0x302fff: return 'RAM_REG'
    elif 0x308000 <= addr <= 0x308fff: return 'RAM_CMD'
    else                             : return None

class Address\
        (nt('Address', ('start', 'end', 'val', 'ann_id'))):
    '''Host Memory Read/Write address.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value'''

    __slots__ = ()

    @property
    def ram_str (self):
        ram = ram_str(self.val)
        return ram if ram else '(unknown)'

    @property
    def ann_str (self):
        return [f'Write Address: 0x{self.val:06X} ({self.ram_str})',
                f'Addr: {self.ram_str}',
                self.ram_str]

class Dummy\
        (nt('Dummy', ('start', 'end', 'val'))):
    '''Host Memory Write dummy byte.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value'''

    __slots__ = ()

    ann_id = ann.Id.DUMMY

    @property
    def ann_str (self):
        return [f'Dummy: 0x{self.val:02X}',
                f'D: {self.val:02X}',
                'D']

class Transaction\
        (nt('Transaction', ('start', 'end', 'miso_size', 'mosi_size'))):
    '''Host Memory Read/Write transaction.

    miso_size: int
        number of bytes read from MISO line

    mosi_size: int
        number of bytes written to MOSI line.'''

    __slots__ = ()

    ann_id = ann.Id.TRANSACTION

    @property
    def ann_str (self):
        return [f'Host Command transaction: out: {self.mosi_size}B, in: {self.miso_size}',
                f'Host Cmd: {self.mosi_size}B',
                'Host',
                'H']


