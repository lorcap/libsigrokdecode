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

from collections import namedtuple as nt
from . import annotation as ann

CPC = 'Co-Processor Command '

#-- Display List Management ------------------------------------------------#

class CMD_DLSTART\
        (nt('_', ('start', 'end', 'val'))):
    '''Start a new display list.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value.'''

    __slots__ = ()

    ann_id = ann.Id.COMMAND

    @property
    def ann_str (self):
        return [f'{CPC}{self.__class__.__name__}',
                self.__class__.__name__]

class CMD_SWAP\
        (nt('_', ('start', 'end', 'val'))):
    '''Swap the current display list.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value.'''

    __slots__ = ()

    ann_id = ann.Id.COMMAND

    @property
    def ann_str (self):
        return [f'{CPC}{self.__class__.__name__}',
                self.__class__.__name__]


#-- Graphics Objects Drawing -----------------------------------------------#

