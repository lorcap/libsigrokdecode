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

from dataclasses import dataclass
from typing import List
from . import annotation

@dataclass
class Warning (annotation.Annotation):
    '''Base class for warning annotations.'''

    @property
    def id_ (self) -> int:
        return annotation.Id.WARNING

@dataclass
class Message (Warning):
    '''Generic warning with custom message.'''
    text: str   # message text

    @property
    def strings_ (self) -> List[str]:
        return [self.text]

@dataclass
class InvalidParameterValue (Warning):
    '''Warning for invalid parameter value.'''
    val: int    # raw value
    name: str   # parameter name

    @property
    def strings_ (self) -> List[str]:
        return [f'invalid parameter value: {self._par_str(self.name, self.val)}']

@dataclass
class MissingDummy (Warning):
    '''Warning for missing memory write dummy byte.'''

    @property
    def strings_ (self) -> List[str]:
        return ['missing dummy byte']

@dataclass
class TrailingData (Warning):
    '''Warning for transaction trailing data.'''
    count: int  # trailing byte count

    @property
    def strings_ (self) -> List[str]:
        return [f'trailing data: {self.count}B']

@dataclass
class TruncatedCommand (Warning):
    '''Warning for not enough data for making a command.'''

    @property
    def strings_ (self) -> List[str]:
        return ['truncated command']

@dataclass
class UnknownCommand (Warning):
    '''Warning for command not known.'''
    val: int    # raw value

    @property
    def strings_ (self) -> List[str]:
        return [f'unknown command: {self._par_str(self.val)}']

@dataclass
class UnknownRegister (Warning):
    '''Warning for register not known.'''
    val: int    # raw value
    addr: int   # register address

    @property
    def strings_ (self) -> List[str]:
        return [f'unknown register at {self._par_str(self.addr)}']

