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

import dataclasses
from dataclasses import dataclass
from typing import List
from . import annotation

@dataclass(frozen=True)
class RAM_G:
    begin: int = 0x000000
    end  : int = 0x0fffff

@dataclass(frozen=True)
class ROM_FONT:
    begin: int = 0x1e0000
    end  : int = 0x2ffffb

@dataclass(frozen=True)
class ROM_FONT_ADDR:
    begin: int = 0x2ffffc
    end  : int = 0x2fffff

@dataclass(frozen=True)
class RAM_DL:
    begin: int = 0x300000
    end  : int = 0x301fff

@dataclass(frozen=True)
class RAM_REG:
    begin: int = 0x302000
    end  : int = 0x302fff

@dataclass(frozen=True)
class RAM_CMD:
    begin: int = 0x308000
    end  : int = 0x308fff

@dataclass(frozen=True)
class RAM_ERR_REPORT:
    begin: int = 0x309800
    end  : int = 0x3098ff

@dataclass(frozen=True)
class FLASH:
    begin: int = 0x800000
    end  : int = 0x800000 + 256*2**20 - 1

def space (addr: int) -> str:
    if   RAM_G         .begin <= addr <= RAM_G         .end: return 'RAM_G'
    elif ROM_FONT      .begin <= addr <= ROM_FONT      .end: return 'ROM_FONT'
    elif ROM_FONT_ADDR .begin <= addr <= ROM_FONT_ADDR .end: return 'ROM_FONT_ADDR'
    elif RAM_DL        .begin <= addr <= RAM_DL        .end: return 'RAM_DL'
    elif RAM_REG       .begin <= addr <= RAM_REG       .end: return 'RAM_REG'
    elif RAM_CMD       .begin <= addr <= RAM_CMD       .end: return 'RAM_CMD'
    elif RAM_ERR_REPORT.begin <= addr <= RAM_ERR_REPORT.end: return 'RAM_ERR_REPORT'
    elif FLASH         .begin <= addr <= FLASH         .end: return 'Flash memory'
    else                                                   : return None

def add (addr: int, offset: int) -> int:
    '''Advance in memory.'''
    if   space(addr) == 'RAM_CMD':
        return (self.val + offset) & 0x308fff
    elif addr == 0x302578: # REG_CMDB_WRITE
        return addr
    else:
        return addr + offset

@dataclass
class HostRead (annotation.Annotation):
    '''Host Memory Read.'''
    val_: int   # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.HOST_MEMORY_READ

    @property
    def strings_ (self) -> List[str]:
        return ['Host Memory Read',
                'Memory Read',
                'Read']

@dataclass
class HostWrite (annotation.Annotation):
    '''Host Memory Write.'''
    val_: int   # raw value

    @property
    def strings_ (self) -> List[str]:
        return ['Host Memory Write',
                'Memory Write',
                'Read']

    @property
    def id_ (self) -> int:
        return annotation.Id.HOST_MEMORY_WRITE

@dataclass
class Dummy (annotation.Annotation):
    '''Host Memory Write dummy byte.'''
    val: int    # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.WRITE_DUMMY

    @property
    def strings_ (self) -> List[str]:
        par = self._par_str(self.val)
        return [f'Host Memory Write Dummy byte: {par}',
                f'Dummy: {par}',
                'Dummy']

@dataclass
class Address (annotation.Annotation):
    '''Host Memory Read/Write addresses.'''
    addr: int   # addr value
    line: str   # MISO/MOSI

    @property
    def id_ (self) -> int:
        if self.line == 'miso':
            return annotation.Id.READ_ADDRESS
        elif self.line == 'mosi':
            return annotation.Id.WRITE_ADDRESS
        else:
            assert(False)

    @property
    def addr_str (self):
        addr = space(self.addr)
        return addr if addr else '(unknown)'

    @property
    def strings_ (self) -> List[str]:
        addr_long = self._par_str(self.addr, desc=self.addr_str)
        addr_mid  = self._par_str(self.addr)
        return [f'{self.name_}: {addr_long}',
                f'Addr: {addr_mid}',
                self.addr_str]

#---------------------------------------------------------------------------#

@dataclass
class ReadTransaction (annotation.Transaction):
    '''Memory Read transaction.'''

    @property
    def name_ (self) -> str:
        return 'Memory Read'

@dataclass
class WriteTransaction (annotation.Transaction):
    '''Memory Write transaction.'''

    @property
    def name_ (self) -> str:
        return 'Memory Write'

