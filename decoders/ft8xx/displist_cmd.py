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

DLC = 'Display List Command '

class ALPHA_FUNC\
        (nt('_', ('start', 'end', 'val', 'func', 'ref'))):
    '''Alpha test function.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value

    func: int
        test function, one of NEVER, LESS, LEQUAL, GREATER, GEQUAL, EQUAL,
        NOTEQUAL, or ALWAYS

    ref: int
        reference value for the alpha test.'''

    __slots__ = ()

    ann_id = ann.Id.COMMAND

    @property
    def func_str (self):
        if   self.func == 0: return 'NEVER'
        elif self.func == 1: return 'LESS'
        elif self.func == 2: return 'LEQUAL'
        elif self.func == 3: return 'GREATER'
        elif self.func == 4: return 'GEQUAL'
        elif self.func == 5: return 'EQUAL'
        elif self.func == 6: return 'NOTEQUAL'
        elif self.func == 7: return 'ALWAYS'
        else               : return '(invalid)'

    @property
    def ann_str (self):
        return [f'{DLC}{self.__class__.__name__}: func={self.func_str}, ref={self.ref}',
                f'{self.__class__.__name__}({self.func_str}, {self.ref})',
                self.__class__.__name__]

class BEGIN\
        (nt('_', ('start', 'end', 'val', 'prim'))):
    '''Start drawing a graphics primitive.

    start: int
        start sample

    end: int
        end sample

    val: int
        raw value

    prim: int
        graphics primitive.'''

    __slots__ = ()

    ann_id = ann.Id.COMMAND

    @property
    def prim_str (self):
        if   self.prim == 1: return 'BITMAPS'
        elif self.prim == 2: return 'POINTS'
        elif self.prim == 3: return 'LINES'
        elif self.prim == 4: return 'LINE_STRIP'
        elif self.prim == 5: return 'EDGE_STRIP_R'
        elif self.prim == 6: return 'EDGE_STRIP_L'
        elif self.prim == 7: return 'EDGE_STRIP_A'
        elif self.prim == 8: return 'EDGE_STRIP_B'
        elif self.prim == 9: return 'RECTS'
        else               : return '(invalid)'

    @property
    def ann_str (self):
        return [f'{DLC}{self.__class__.__name__}: prim={self.prim_str}',
                f'{self.__class__.__name__}({self.prim_str})',
                self.__class__.__name__]

