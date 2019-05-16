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

class RamCmd (Base):
    '''Base class for all commands in RAM_CMD.'''

    def __init__ (self, data_, name_, **param_):
        ann_str = []
        if param:
            par = ('%s: %s' % (k, str(v)) for k,v in param_)
            par = ','.join(par)
            ann_str.append(f'{name_}({par})')
            par = (str(v) for k,v in param_)
            par = ','.join(par)
            ann_str.append(f'{name_}({par})')
        ann_str.append(name_)
        super().__init__(
                start  =data_[0].start,
                end    =data_[-1].end,
                val    =uint(data_),
                ann_id =self._decoder.AnnId.RAM_CMD,
                ann_str=ann_str)

class AlphaFunc (RamCmd):
    def __init__ (self, data_, func_, ref_):
        if   func_ == 0: func_str = 'NEVER'
        elif func_ == 1: func_str = 'LESS'
        elif func_ == 2: func_str = 'LEQUAL'
        elif func_ == 3: func_str = 'GREATER'
        elif func_ == 4: func_str = 'GEQUAL'
        elif func_ == 5: func_str = 'EQUAL'
        elif func_ == 6: func_str = 'NOTEQUAL'
        elif func_ == 7: func_str = 'ALWAYS'
        else           : func_str = '(unknown)'
        super().__init__(data_, 'ALPHA_FUNC',
                         func=func_str, ref=ref_)

class Begin (RamCmd):
    def __init__ (self, data_, prim_):
        if   prim_ == 1: prim_str = 'BITMAPS'
        elif prim_ == 2: prim_str = 'POINTS'
        elif prim_ == 3: prim_str = 'LINES'
        elif prim_ == 4: prim_str = 'LINE_STRIP'
        elif prim_ == 5: prim_str = 'EDGE_STRIP_R'
        elif prim_ == 6: prim_str = 'EDGE_STRIP_L'
        elif prim_ == 7: prim_str = 'EDGE_STRIP_A'
        elif prim_ == 8: prim_str = 'EDGE_STRIP_B'
        elif prim_ == 9: prim_str = 'RECTS'
        else           : prim_str = '(unknown)'
        super().__init__(data_, 'BEGIN', prim=prim_str)

class BitmapHandle (RamCmd):
    def __init__ (self, data_, handle_):
        super().__init__(data_, 'BITMAP_HANDLE',
                         handle=handle_)

class BitmapLayout (RamCmd):
    def __init__ (self, data_, format_, linestride_, height_):
        if   format_ ==  0: format_str = 'ARGB1555'
        elif format_ ==  1: format_str = 'L1'
        elif format_ ==  2: format_str = 'L4'
        elif format_ ==  3: format_str = 'L8'
        elif format_ ==  4: format_str = 'RGB332'
        elif format_ ==  5: format_str = 'ARGB2'
        elif format_ ==  6: format_str = 'ARGB4'
        elif format_ ==  7: format_str = 'RGB565'
        elif format_ ==  9: format_str = 'TEXT8X8'
        elif format_ == 10: format_str = 'TEXTVGA'
        elif format_ == 11: format_str = 'BARGRAPH'
        elif format_ == 14: format_str = 'PALETTED565'
        elif format_ == 15: format_str = 'PALETTED4444'
        elif format_ == 16: format_str = 'PALETTED8'
        elif format_ == 17: format_str = 'L2'
        else              : format_str = '(unknown)'
        super().__init__(data_, 'BITMAP_LAYOUT',
                         format=format_str, linestride=linestride_, height=height_)

