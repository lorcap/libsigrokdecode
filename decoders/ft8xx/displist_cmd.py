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
from . import annotation, memory

@dataclass
class Command (annotation.Command):
    '''Command base for all display list commands.'''

    @property
    def id_ (self) -> int:
        return annotation.Id.DISPLAY_LIST

    @property
    def format_str (self) -> str:
        if   self.format ==     0: return 'ARGB1555'
        elif self.format ==     1: return 'L1'
        elif self.format ==     2: return 'L4'
        elif self.format ==     3: return 'L8'
        elif self.format ==     4: return 'RGB322'
        elif self.format ==     5: return 'ARGB2'
        elif self.format ==     6: return 'ARGB4'
        elif self.format ==     7: return 'RGB565'
        elif self.format ==     9: return 'TEXT8X8'
        elif self.format ==    10: return 'TEXTVGA'
        elif self.format ==    11: return 'BARGRAPH'
        elif self.format ==    14: return 'PALETTED565'
        elif self.format ==    15: return 'PALETTED4444'
        elif self.format ==    16: return 'PALETTED8'
        elif self.format ==    17: return 'L2'
        elif self.format ==    31: return 'GLFORMAT'
        elif self.format == 37808: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 4,  4)
        elif self.format == 37809: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 5,  4)
        elif self.format == 37810: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 5,  5)
        elif self.format == 37811: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 6,  5)
        elif self.format == 37812: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 6,  6)
        elif self.format == 37813: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  5)
        elif self.format == 37814: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  6)
        elif self.format == 37815: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  8)
        elif self.format == 37816: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  5)
        elif self.format == 37817: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  6)
        elif self.format == 37818: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  8)
        elif self.format == 37819: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10, 10)
        elif self.format == 37820: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(12, 10)
        elif self.format == 37821: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(12, 12)
        else:
            self._warning(warning.InvalidParameterValue, self.format, 'format')
            return ''

@dataclass
class ALPHA_FUNC (Command):
    '''set the alpha test function.'''
    func: int   # test function
    ref: int    # reference value for the alpha test

    @property
    def func_str (self) -> str:
        if   self.func == 0: return 'NEVER'
        elif self.func == 1: return 'LESS'
        elif self.func == 2: return 'LEQUAL'
        elif self.func == 3: return 'GREATER'
        elif self.func == 4: return 'GEQUAL'
        elif self.func == 5: return 'EQUAL'
        elif self.func == 6: return 'NOTEQUAL'
        elif self.func == 7: return 'ALWAYS'
        else:
            self._warning(warning.InvalidParameterValue, self.func, 'func')
            return ''

@dataclass
class BEGIN (Command):
    '''Start drawing a graphics primitive.'''
    prim: int   # graphics primitive

    @property
    def prim_str (self) -> str:
        if   self.prim == 1: return 'BITMAPS'
        elif self.prim == 2: return 'POINTS'
        elif self.prim == 3: return 'LINES'
        elif self.prim == 4: return 'LINE_STRIP'
        elif self.prim == 5: return 'EDGE_STRIP_R'
        elif self.prim == 6: return 'EDGE_STRIP_L'
        elif self.prim == 7: return 'EDGE_STRIP_A'
        elif self.prim == 8: return 'EDGE_STRIP_B'
        elif self.prim == 9: return 'RECTS'
        else:
            self._warning(warning.InvalidParameterValue, self.prim, 'prim')
            return ''

@dataclass
class BITMAP_EXT_FORMAT (Command):
    '''Specify the extended format of the bitmap.'''
    format: int # bitmap pixel format

@dataclass
class BITMAP_HANDLE (Command):
    '''Specify the bitmap handle.'''
    handle: int # bitmap handle

@dataclass
class BITMAP_LAYOUT (Command):
    '''Specify the source bitmap memory format and layout for the current handle.'''
    format: int     # bitmap pixel format
    linestride: int # bitmap line strides, in bytes
    height: int     # bitmap height, in lines

@dataclass
class BITMAP_LAYOUT_H (Command):
    '''Specify the 2 most significant bits for BITMAP_LAYOUT_H.'''
    linestride: int # bitmap line strides
    height: int     # bitmap height

@dataclass
class BITMAP_SIZE (Command):
    '''Specify the screen drawing of bitmaps for the current handle.'''
    filter: bool    # bitmap filtering mode
    wrapx: bool     # bitmap x wrap mode
    wrapy: bool     # bitmap y wrap mode
    width: int      # drawn bitmap width, in pixels
    height: int     # drawn bitmap height, in pixels

    @property
    def filter_str (self) -> str:
        return 'BILINEAR' if self.filter else 'NEAREST'

    @property
    def wrapx_str (self) -> str:
        return 'REPEAT' if self.wrapx else 'BORDER'

    @property
    def wrapy_str (self) -> str:
        return 'REPEAT' if self.wrapy else 'BORDER'

@dataclass
class BITMAP_SIZE_H (Command):
    '''Specify the 2 most significant bits for BITMAP_SIZE.'''
    width: int  # bitmap width
    height: int # bitmap height

@dataclass
class BITMAP_SOURCE (Command):
    '''Specify the source address of bitmap data in BT815/6 graphics memory
       RAM_G or flash memory.'''
    addr: int

    @property
    def addr_str (self) -> str:
        s = memory.space(self.addr)
        if self.addr & 0x800000:
            return '{0}@{1}'.format(4*(self.addr - 0x800000), s)
        else:
            return s

@dataclass
class BITMAP_SWIZZLE (Command):
    '''Set the source for the red, green, blue and alpha channels of a bitmap.'''
    r: int  # red component source channel
    g: int  # green component source channel
    b: int  # blue component source channel
    a: int  # alpha component source channel

    def _val_str (self, name: str) -> str:
        val = getattr(self, name)
        if   val == 0: return 'ZERO'
        elif val == 1: return 'ONE'
        elif val == 2: return 'RED'
        elif val == 3: return 'GREEN'
        elif val == 4: return 'BLUE'
        elif val == 5: return 'ALPHA'
        else:
            self._warning(warning.InvalidParameterValue, val, name)
            return ''

    @property
    def r_str (self) -> str:
        return self._val_str('r')

    @property
    def g_str (self) -> str:
        return self._val_str('g')

    @property
    def b_str (self) -> str:
        return self._val_str('b')

    @property
    def a_str (self) -> str:
        return self._val_str('a')

@dataclass
class BITMAP_TRANSFORM_A (Command):
    '''Specify the A coefficient of the bitmap transform matrix.'''
    p: int  # precision control
    v: int  # component of the bitmap transform matrix

    @property
    def p_str (self) -> str:
        if   self.p == 0: return '8.8'
        elif self.p == 1: return '1.15'

    @property
    def v_str (self) -> str:
        if self.p == 0:
            i = (self.v & 0xff00) >> 8
            d = (self.v & 0x00ff) >> 0
        elif self.p == 1:
            i = (self.v & 0x8000) >> 15
            d = (self.v & 0x7fff) >> 0
        return f'{i}.{d}'

@dataclass
class BITMAP_TRANSFORM_B (BITMAP_TRANSFORM_A):
    '''Specify the B coefficient of the bitmap transform matrix.'''
    pass

@dataclass
class BITMAP_TRANSFORM_C (Command):
    '''Specify the c coefficient of the bitmap transform matrix.'''
    c: int  # coefficient c of the bitmap transform matrix

    @property
    def c_str (self) -> str:
        i = (self.c & 0xffff00) >> 8
        d = (self.c & 0x0000ff) >> 0
        return f'{i}.{d}'

@dataclass
class BITMAP_TRANSFORM_D (BITMAP_TRANSFORM_A):
    '''Specify the D coefficient of the bitmap transform matrix.'''
    pass

@dataclass
class BITMAP_TRANSFORM_E (BITMAP_TRANSFORM_A):
    '''Specify the E coefficient of the bitmap transform matrix.'''
    pass

@dataclass
class BITMAP_TRANSFORM_F (Command):
    '''Specify the f coefficient of the bitmap transform matrix.'''
    f: int  # coefficient f of the bitmap transform matrix

    @property
    def f_str (self) -> str:
        i = (self.f & 0xffff00) >> 8
        d = (self.f & 0x0000ff) >> 0
        return f'{i}.{d}'

@dataclass
class BLEND_FUNC (Command):
    '''Specify pixel arithmetic.'''
    src: int    # specifies how the source blending factor is computed.
    dst: int    # specifies how the destination blending factor is computed

    def _val_str (self, name: str) -> str:
        val = getattr(self, name)
        if   val == 0: return 'ZERO'
        elif val == 1: return 'ONE'
        elif val == 2: return 'SRC_ALPHA'
        elif val == 3: return 'DST_ALPHA'
        elif val == 4: return 'ONE_MINUS_SRC_ALPHA'
        elif val == 5: return 'ONE_MINUS_DST_ALPHA'
        else:
            self._warning(warning.InvalidParameterValue, val, name)
            return ''

    @property
    def src_str (self) -> str:
        return self._val_str('src')

    @property
    def dst_str (self) -> str:
        return self._val_str('dst')


@dataclass
class COLOR_RGB (Command):
    '''Set the current color red, green and blue.'''
    red: int    # red value for the current color
    green: int  # green value for the current color
    blue: int   # blue value for the current color

