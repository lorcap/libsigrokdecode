##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2018-2019 Lorenzo Cappelletti <lorenzo.cappelletti@gmail.com>
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
from . import annotation, memmap

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
        return self._addr_str(self.addr)

    @property
    def strings_ (self) -> List[str]:
        return [self._par_str(self.addr, desc=self.addr_str),
                self._par_str(self.addr),
                self._hex_str(self.addr)]

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

