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
from . import annotation, memmap

@dataclass
class Command (annotation.Command):
    '''Command base for all display list commands.'''
    val_: int   # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.DISPLIST

    @staticmethod
    def _px_str (val: str) -> str:
        '''Add pixel suffix, consistently.'''
        return val + ' px'

    def _px16_str (self, val: int) -> str:
        '''Convert value to 1/15 pixel.'''
        return self._px_str(str(val/16))

@dataclass
class Branch ():
    '''Class common to branching commands.'''
    dest: int   # offset of the destination address

    def dest_is_valid (self) -> bool:
        return 0 <= self.dest <= 8191

    @property
    def dest_str (self) -> str:
        return self._par_str(memmap.RAM_DL.begin + self.dest)

@dataclass
class Func ():
    '''Class common to function test.'''
    func: int   # test function
    ref: int    # reference value for the function test

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
        else               : return ''

# ------------------------------------------------------------------------- #

@dataclass
class ALPHA_FUNC (Func, Command):
    '''set the alpha test function.'''
    pass

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
        else               : return ''

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
    '''Specify the source bitmap memmap format and layout for the current handle.'''
    format: int     # bitmap pixel format
    linestride: int # bitmap line strides, in bytes
    height: int     # bitmap height, in lines

    @property
    def format_str (self) -> str:
        return Command._format_str(self.format)

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
    '''Specify the source address of bitmap data in BT815/6 graphics memmap RAM_G or flash memmap.'''
    addr: int

    @property
    def addr_str (self) -> str:
        s = memmap.space(self.addr)
        if self.addr & 0x800000:
            return '{0}@{1}'.format(4*(self.addr - 0x800000), s)
        else:
            return self._addr_str(self.addr)

@dataclass
class BITMAP_SWIZZLE (Command):
    '''Set the source for the red, green, blue and alpha channels of a bitmap.'''
    r: int  # red component source channel
    g: int  # green component source channel
    b: int  # blue component source channel
    a: int  # alpha component source channel

    @staticmethod
    def _rgba_str (val: int) -> str:
        if   val == 0: return 'ZERO'
        elif val == 1: return 'ONE'
        elif val == 2: return 'RED'
        elif val == 3: return 'GREEN'
        elif val == 4: return 'BLUE'
        elif val == 5: return 'ALPHA'
        else         : return ''

    @property
    def r_str (self) -> str:
        return self._rgba_str(self.r)

    @property
    def g_str (self) -> str:
        return self._rgba_str(self.g)

    @property
    def b_str (self) -> str:
        return self._rgba_str(self.b)

    @property
    def a_str (self) -> str:
        return self._rgba_str(self.a)

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
        return Command._matrix_abde_str(self.v, self.p)

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
        return Command._matrix_cf_str(self.c)

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
        return Command._matrix_cf_str(self.f)

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
        else         : return ''

    @property
    def src_str (self) -> str:
        return self._val_str('src')

    @property
    def dst_str (self) -> str:
        return self._val_str('dst')

@dataclass
class CALL (Branch, Command):
    '''Execute a sequence of commands at another location in the display list.'''
    pass

@dataclass
class CELL (Command):
    '''Specify the bitmap cell number for the VERTEX2F command.'''
    cell: int   # bitmap cell number

@dataclass
class CLEAR (Command):
    '''Clear buffers to preset values.'''
    c: bool # clear color buffer
    s: bool # clear stencil buffer
    t: bool # clear tag buffer

@dataclass
class CLEAR_COLOR_A (Command):
    '''Specify clear value for the alpha channel.'''
    alpha: int  # alpha value used when the color buffer is cleared

@dataclass
class CLEAR_COLOR_RGB (Command):
    '''Specify clear values for red, green and blue channels.'''
    red: int    # red value used when the color buffer is cleared
    blue: int   # blue value used when the color buffer is cleared
    green: int  # green value used when the color buffer is cleared

@dataclass
class CLEAR_STENCIL (Command):
    '''Specify clear value for the stencil buffer.'''
    s: int  # value used when the stencil buffer is cleared

@dataclass
class CLEAR_TAG (Command):
    '''Specify clear value for the tag buffer.'''
    t: int  # value used when the tag buffer is cleared

@dataclass
class COLOR_A (Command):
    '''Set the current color alpha.'''
    alpha: int  # alpha for the current color

@dataclass
class COLOR_MASK (Command):
    '''Enable or disable writing of color components.'''
    r: bool # enable/disable the red channel update of the color buffer
    g: bool # enable/disable the green channel update of the color buffer
    b: bool # enable/disable the blue channel update of the color buffer
    a: bool # enable/disable the alpha channel update of the color buffer

@dataclass
class COLOR_RGB (Command):
    '''Set the current color red, green and blue.'''
    red: int    # red value for the current color
    green: int  # green value for the current color
    blue: int   # blue value for the current color

@dataclass
class DISPLAY (Command):
    '''End the display list.'''
    pass

@dataclass
class END (Command):
    '''End drawing a graphics primitive.'''
    pass

@dataclass
class JUMP (Branch, Command):
    '''Execute commands at another location in the display list.'''
    pass

@dataclass
class LINE_WIDTH (Command):
    '''Specify the width of lines to be drawn with primitive LINES in 1/16 pixel precision.'''
    width: int  # line width in 1/16 pixel precision

    @property
    def width_str (self) -> str:
        return self._pr16_str(self.width)

@dataclass
class MACRO (Command):
    '''Execute a single command from a macro register.'''
    m: int  # macro registers to read

    @property
    def m_str (self) -> str:
        return f'REG_MACRO_{self.m}'

@dataclass
class NOP (Command):
    '''No operation.'''
    pass

@dataclass
class PALETTE_SOURCE (Command):
    '''Specify the base address of the palette.'''
    addr: int   # address of palette in RAM_G

@dataclass
class POINT_SIZE (Command):
    '''Specify the radius of points.'''
    size: int   # point radius in 1/16 pixel precision

    @property
    def size_str (self) -> str:
        return self._px16_str(self.size)

@dataclass
class RESTORE_CONTEXT (Command):
    '''Restore the current graphics context from the context stack.'''
    pass

@dataclass
class RETURN (Command):
    '''Return from a previous CALL command.'''
    pass

@dataclass
class SAVE_CONTEXT (Command):
    '''Push the current graphics context on the context stack.'''
    pass

@dataclass
class SCISSOR_SIZE (Command):
    '''Specify the size of the scissor clip rectangle.'''
    width: int  # width of the scissor clip rectangle, in pixels
    height: int # height of the scissor clip rectangle, in pixels
    FT80x_width: int
    FT80x_height: int

@dataclass
class SCISSOR_XY (Command):
    '''Specify the top left corner of the scissor clip rectangle.'''
    x: int  # unsigned x coordinate of the scissor clip rectangle, in pixels
    y: int  # unsigned y coordinates of the scissor clip rectangle, in pixels
    FT80x_x: int
    FT80x_y: int

@dataclass
class STENCIL_FUNC (Func, Command):
    '''Set function and reference value for stencil testing.'''
    mask: int   # mask that is ANDed with the reference value and the stored stencil value

@dataclass
class STENCIL_MASK (Command):
    '''Control the writing of individual bits in the stencil planes.'''
    mask: int   # mask used to enable writing stencil bits

@dataclass
class STENCIL_OP (Command):
    '''Set stencil test actions.'''
    sfail: int  # action to take when the stencil test fails
    spass: int  # action to take when the stencil test passes

    @staticmethod
    def _action_str (val) -> str:
        if   val == 0: return 'ZERO'
        elif val == 1: return 'KEEP'
        elif val == 2: return 'REPLACE'
        elif val == 3: return 'INCR'
        elif val == 4: return 'DECR'
        elif val == 5: return 'INVERT'
        else         : return ''

    @property
    def sfail_str (self) -> str:
        return self._action_str(self.sfail)

    @property
    def spass_str (self) -> str:
        return self._action_str(self.spass)

@dataclass
class TAG (Command):
    '''Attach the tag value for the following graphics objects drawn on the screen.'''
    s: int  # tag value

@dataclass
class TAG_MASK (Command):
    '''Control the writing of the tag buffer.'''
    mask: bool  # allow updates to the tag buffer

@dataclass
class VERTEX2F (Command):
    '''Start the operation of graphics primitives at the specified screen coordinate,
    in the pixel precision defined by VERTEX_FORMAT.'''
    x: int  # signed x-coordinate in units
    y: int  # signed y-coordinate in units

    def _coord_str (self, val: int) -> str:
        if val > 2**14 - 1:
            val -= 2**15
        return self._px_str('{0}/{1}/{2}/{3}/{4}'.format(val, *[val/2**i for i in range(1,5)]))

    @property
    def x_str (self) -> str:
        return self._coord_str(self.x)

    @property
    def y_str (self) -> str:
        return self._coord_str(self.y)

@dataclass
class VERTEX2II (Command):
    '''Start the operation of graphics primitive at the specified coordinates in pixel precision.'''
    x: int      # X-coordinate in pixels, unsigned integer
    y: int      # y-coordinate in pixels, unsigned integer
    handle: int # bitmap handle
    cell: int   # cell number

@dataclass
class VERTEX_FORMAT (Command):
    '''Set the precision of VERTEX2F coordinates.'''
    frac: int   # number of fractional bits in X, Y coordinates

    @property
    def frac_str (self) -> str:
        if self.frac == 0:
            return '1 pixel'
        elif 1 <= self.frac <= 4:
            return '1/{0} pixel'.format(2**self.frac)
        else:
            return ''

@dataclass
class VERTEX_TRANSLATE_X (Command):
    '''Specify the vertex transformations X translation component.'''
    x: int  # signed x-coordinate in 1/16 pixel

    @property
    def x_str (self) -> str:
        return self._px16_str(self.x)

@dataclass
class VERTEX_TRANSLATE_Y (Command):
    '''Specify the vertex transformations Y translation component.'''
    y: int  # signed y-coordinate in 1/16 pixel

    @property
    def y_str (self) -> str:
        return self._px16_str(self.y)

