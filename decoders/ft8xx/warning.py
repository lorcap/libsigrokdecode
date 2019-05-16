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

from dataclasses import dataclass
from typing import List
from . import annotation

@dataclass
class Warning (annotation.Warning):
    '''Generic warning with custom message.'''
    text: str   # message text

    @property
    def strings_ (self) -> List[str]:
        return [text]

@dataclass
class InvalidParameterValue (Warning):
    '''Warning for invalid parameter value.'''
    val: int    # raw value
    name: str   # parameter name

    @property
    def strings_ (self) -> List[str]:
        return [f'invalid parameter value: {self.name}={self._int_str(val)}']

@dataclass
class TrailingData (Warning):
    '''Warning for transaction trailing data.'''
    count: int  # trailing byte count

    @property
    def strings_ (self) -> List[str]:
        return [f'trailing data: {self.count}B']

@dataclass
class TruncatedCommand (Warning):

    @property
    def strings_ (self) -> List[str]:
        return ['truncated command']

@dataclass
class UnknownCommand (Warning):
    '''Warning for invalid parameter value.'''
    val: int    # raw value

    @property
    def strings_ (self) -> List[str]:
        val = f'{self.val:02X}' if self.val <= 0xff else f'{self.val:08X}'
        return [f'unknown command: 0x{val} ({self.val})']

