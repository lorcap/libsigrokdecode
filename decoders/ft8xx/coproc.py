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
from typing import ByteString, List, Tuple
from dataclasses import dataclass
from . import annotation, memmap

OPT_3D          =     0 # 3D effect
OPT_RGB565      =     0 # decode the source image to RGB565 format
OPT_MONO        =     1 # decode the source JPEG image to L8 format, i.e., monochrome
OPT_NODL        =     2 # no display list commands generated
OPT_FLAT        =   256 # no 3D effect
OPT_SIGNED      =   256 # the number is treated as a 32 bit signed integer
OPT_CENTERX     =   512 # horizontally-centred style
OPT_CENTERY     =  1024 # vertically centred style
OPT_CENTER      =  1536 # horizontally and vertically centred style
OPT_RIGHTX      =  2048 # right justified style
OPT_NOBACK      =  4096 # no background drawn
OPT_FLASH       =    64 # fetch the data from flash memory
OPT_FORMAT      =  4096 # flag of string formatting
OPT_NOTICKS     =  8192 # no ticks
OPT_NOHM        = 16384 # no hour and minute hands
OPT_NOPOINTER   = 16384 # no pointer
OPT_NOSECS      = 32768 # no second hands
OPT_NOHANDS     = 49152 # no hands
OPT_NOTEAR      =     4 # synchronize video updates to the display blanking interval, avoiding horizontal “tearing” artefacts
OPT_FULLSCREEN  =     8 # zoom the video so that it fills as much of the screen as possible
OPT_MEDIAFIFO   =    16 # source video data from the defined media FIFO
OPT_SOUND       =    32 # decode the audio data

@dataclass
class Command (annotation.Command):
    '''Command base for all coprocessor commands.'''
    val_: int   # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.COPROC

    @property
    def strings_ (self) -> List[str]:
        '''Generate annotation strings from dataclass' fields.'''
        str_list = list()

        for par in self.parameters():
            try:
                # parameter is represented by '<par>_str'
                val_str = getattr(self, par + '_str')
            except AttributeError:
                # '<par>_str' doesn't exist
                val_str = str(getattr(self, par).val)
            str_list.append(f'{par}={val_str}')

        par_str = '; '.join(str_list)
        return [f'{self.name_}({par_str})']

    @property
    def argb_str (self) -> str:
        (a, r, g, b) = self._argb(c.val)
        return f'argb({a},{r},{g},{b})'

    @property
    def ch_str (self) -> str:
        return self._dec_str(self.ch.val)

    @property
    def dst_str (self) -> str:
        return self._hex_str(self.dst.val)

    @property
    def font_str (self) -> str:
        return str(self.font.val)

    @property
    def h_str (self) -> str:
        return self._px_str(self.h.val)

    @property
    def num_str (self) -> str:
        return self._dec_str(self.num.val)

    @property
    def num4_str (self) -> str:
        if self.num.val % 4 != 0:
            self._warning = warning.Message('not a multiple of 4')
        return Command._num_str(self)

    @property
    def options_str (self) -> str:
        '''Options.'''
        CMD_BCKG_SDTP_S = ('CMD_BUTTON', 'CMD_CLOCK', 'CMD_KEYS', 'CMD_GAUGE',
                           'CMD_SLIDER', 'CMD_DIAL', 'CMD_TOGGLE', 'CMD_PROGRESS',
                           'CMD_SCROLLBAR')
        CMD_KTN =  ('CMD_KEYS', 'CMD_TEXT', 'CMD_NUMBER')
        CMD_CG = ('CMD_CLOCK', 'CMD_GAUGE')
        CMD_ILPV = ('CMD_INFLATE2', 'CMD_LOADIMAGE', 'CMD_PLAYVIDEO', 'CMD_VIDEOSTART')
        CMD_TBT = ('CMD_TEXT', 'CMD_BUTTON', 'CMD_TOGGLE')
        ret = []

        if self.options.val == 0:
            if self.name_ in CMD_BCKG_SDTP_S:
                ret.append('OPT_3D')
            elif self.name_ == 'CMD_LOADIMAGE':
                ret.append('OPT_RGB565')
            else:
                ret.append(str(0))

        bit = 1
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_LOADIMAGE':
                ret.append('OPT_MONO')
            else:
                ret.append(str(bit))

        bit = 2
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_LOADIMAGE':
                ret.append('OPT_NODL')
            else:
                ret.append(str(bit))

        bit = 4
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_PLAYVIDEO':
                ret.append('OPT_NOTEAR')
            else:
                ret.append(str(bit))

        bit = 8
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_PLAYVIDEO':
                ret.append('OPT_FULLSCREEN')
            else:
                ret.append(str(bit))

        bit = 16
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_PLAYVIDEO':
                ret.append('OPT_MEDIAFIFO')
            else:
                ret.append(str(bit))

        bit = 32
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_PLAYVIDEO':
                ret.append('OPT_SOUND')
            else:
                ret.append(str(bit))

        bit = 64
        if self.options.val & bit == bit:
            if self.name_ in CMD_ILPV:
                ret.append('OPT_FLASH')
            else:
                ret.append(str(bit))

        bit = 256
        if self.options.val & bit == bit:
            if self.name_ in CMD_BCKG_SDTP_S:
                ret.append('OPT_FLAT')
            elif self.name_ == 'CMD_NUMBER':
                ret.append('OPT_SIGNED')
            else:
                ret.append(str(bit))

        bit = 512
        if self.options.val & 1536 == bit:
            if self.name_ in CMD_KTN:
                ret.append('OPT_CENTERX')
            else:
                ret.append(str(bit))

        bit = 1024
        if self.options.val & 1536 == bit:
            if self.name_ in CMD_KTN:
                ret.append('OPT_CENTERY')
            else:
                ret.append(str(bit))

        bit = 1536
        if self.options.val & bit == bit:
            if self.name_ in CMD_KTN:
                ret.append('OPT_CENTER')

        bit = 2048
        if self.options.val & bit == bit:
            if self.name_ in CMD_CG:
                ret.append('OPT_NOBACK')
            elif self.name_ in CMD_TBT:
                ret.append('OPT_FORMAT')
            else:
                ret.append(str(bit))

        bit = 8192
        if self.options.val & bit == bit:
            if self.name_ in CMD_CG:
                ret.append('OPT_NOTICKS')
            else:
                ret.append(str(bit))

        bit = 16384
        if self.options.val & 49152 == bit:
            if self.name_ == 'CMD_CLOCK':
                ret.append('OPT_NOHM')
            elif self.name_ == 'CMD_GAUGE':
                ret.append('OPT_NOPOINTER')
            else:
                ret.append(str(bit))

        bit = 32768
        if self.options.val & 49152 == bit:
            if self.name_ == 'CMD_CLOCK':
                ret.append('OPT_NOSECS')
            else:
                ret.append(str(bit))

        bit = 49152
        if self.options.val & bit == bit:
            if self.name_ == 'CMD_CLOCK':
                ret.append('OPT_NOHANDS')

        return '|'.join(ret)

    @property
    def ptr_str (self) -> str:
        return self._hex_str(self.ptr.val)

    @property
    def result_str (self) -> str:
        return f'({self.result.val})'

    @property
    def rgb_str (self) -> str:
        (a, r, g, b) = self._argb(c.val)
        return f'rgb({r},{g},{b})'

    @property
    def size_str (self) -> str:
        return self._size_str(self.size.val)

    @property
    def src_str (self) -> str:
        return self._hex_str(self.src.val)

    @property
    def tx0_str (self) -> str:
        return self._px_str(self.tx0.val)

    @property
    def tx1_str (self) -> str:
        return self._px_str(self.tx1.val)

    @property
    def tx2_str (self) -> str:
        return self._px_str(self.tx2.val)

    @property
    def ty0_str (self) -> str:
        return self._px_str(self.ty0.val)

    @property
    def ty1_str (self) -> str:
        return self._px_str(self.ty1.val)

    @property
    def ty2_str (self) -> str:
        return self._px_str(self.ty2.val)

    @property
    def x_str (self) -> str:
        return self._px_str(self.x.val)

    @property
    def x1_str (self) -> str:
        return self._px_str(self.x1.val)

    @property
    def x2_str (self) -> str:
        return self._px_str(self.x2.val)

    @property
    def y_str (self) -> str:
        return self._px_str(self.y.val)

    @property
    def y1_str (self) -> str:
        return self._px_str(self.y1.val)

    @property
    def y2_str (self) -> str:
        return self._px_str(self.y2.val)

    @property
    def w_str (self) -> str:
        return self._px_str(self.w.val)

    @staticmethod
    def _argb (val: int) -> Tuple[int, int, int, int]:
        a = (self.c.val & 0xff000000) >> 24
        r = (self.c.val & 0x00ff0000) >> 16
        g = (self.c.val & 0x0000ff00) >>  8
        b = (self.c.val & 0x000000ff) >>  0
        return (a, r, g, b)

    @staticmethod
    def _px_str (val: int) -> str:
        return f'{val}px'

# ------------------------------------------------------------------------- #

@dataclass
class _Parameter (annotation.Annotation):
    '''Base class for all parameters.'''

    @property
    def id_ (self) -> int:
        return annotation.Id.PARAMETER

    @property
    def strings_ (self) -> List[str]:
        return [f'{self.name_}: {self.val_}']

@dataclass
class DataChunk (_Parameter):
    '''Chunk of data bytes.'''
    val: ByteString # data bytes
    pos: int        # position of first byte in the data stream

    def __len__ (self) -> int:
        return len(self.val)

    @property
    def name_ (self) -> str:
        return f'byte{self.pos}…{self.pos + len(self.val) - 1}'\
               if len(self.val) > 1 else f'byte{self.pos}'

    @property
    def val_ (self) -> str:
        hex = [ self.val[i:i+4].hex() for i in range(0, len(self.val), 4) ]
        return ':'.join(hex)

@dataclass
class DataBytes (_Parameter):
    '''Parameter of type `data byte`.'''
    chunks_: Tuple[DataChunk]
    size: int = dataclasses.field(init=False)

    def __post_init__ (self):
        self.size = 0
        for c in self.chunks_:
            self.size += len(c)

    @property
    def val (self) -> str:
        return (self._size_str(self.size) if self.size else 'none')

    @property
    def name_ (self) -> str:
        return 'byte'

@dataclass
class _Int (_Parameter):
    '''Base class for all integer parameters.'''
    val: int    # raw value

    @property
    def val_ (self) -> str:
        return self._int_str(self.val)

@dataclass
class Int16 (_Int):
    '''Parameter of type `int16_t`.'''

    @property
    def name_ (self) -> str:
        return 'int16_t'

@dataclass
class UInt16 (_Int):
    '''Parameter of type `uint16_t`.'''

    @property
    def name_ (self) -> str:
        return 'uint16_t'

@dataclass
class Int32 (_Int):
    '''Parameter of type `int32_t`.'''

    @property
    def name_ (self) -> str:
        return 'int32_t'

@dataclass
class UInt32 (_Int):
    '''Parameter of type `uint32_t`.'''

    @property
    def name_ (self) -> str:
        return 'uint32_t'

@dataclass
class Padding (_Parameter):
    '''Parameter of data padding.'''

    @property
    def strings_ (self) -> List[str]:
        return ['padding']

@dataclass
class String (_Parameter):
    '''Parameter of null-terminated `const char*`.'''
    val: str    # raw value

    @property
    def name_ (self) -> str:
        return 'const char*'

    @property
    def val_ (self) -> str:
        return self.val

# ------------------------------------------------------------------------- #

@dataclass
class CMD_DLSTART (Command):
    '''Start a new Display List.'''
    pass

@dataclass
class CMD_INTERRUPT (Command):
    '''Trigger interrupt INT_CMDFLAG.'''
    ms     : UInt32      # delay before the interrupt triggers, in milliseconds

    @property
    def ms_str (self) -> str:
        ms  = self.ms.val
        s   = int(ms/1000)
        ms -=    (s *1000)
        m   = int(s /  60)
        s  -=    (m *  60)
        h   = int(m /  60)
        m  -=    (h *  60)
        d   = int(h /  24)
        h  -=    (d *  24)
        l = []
        if d:
            l.append(str(d)+'d')
        if h or l:
            l.append(str(h)+'h')
        if m or l:
            l.append(str(m)+'m')
        l.append(f'{s}.{ms}s')
        return ' '.join(l)

@dataclass
class CMD_COLDSTART (Command):
    '''Set coprocessor engine state to default values.'''
    pass

@dataclass
class CMD_SWAP (Command):
    '''Swap the current display list.'''
    pass

@dataclass
class CMD_APPEND (Command):
    '''Append more commands to current display list.'''
    ptr    : UInt32 # starting address of source commands in RAM_G
    num    : UInt32 # number of bytes to copy

    num_str = Command.num4_str

@dataclass
class CMD_REGREAD (Command):
    '''Read a register value.'''
    ptr    : UInt32 # address of the register to be read
    result : UInt32 # the register value to be read at `ptr` address

@dataclass
class CMD_MEMWRITE (Command):
    '''Write bytes into memory.'''
    ptr    : UInt32 # memory address to be written
    num    : UInt32 # number of bytes to be written
    byte_  : DataBytes

@dataclass
class CMD_INFLATE (Command):
    '''Decompress data into memory.'''
    ptr    : UInt32 # destination address in RAM_G
    byte   : DataBytes

@dataclass
class CMD_INFLATE2 (Command):
    '''Decompress data into memory.'''
    ptr    : UInt32 # destination address to put the decompressed data
    options: UInt32 #
    byte   : DataBytes

@dataclass
class CMD_LOADIMAGE (Command):
    '''Load a JPEG or PNG image.'''
    ptr    : UInt32 # destination address
    options: UInt32 #
    byte   : DataBytes

@dataclass
class CMD_MEDIAFIFO (Command):
    '''Set up a streaming media FIFO'''
    ptr    : UInt32 # starting address of memory block
    size   : UInt32 # number of bytes in the source memory block

@dataclass
class CMD_PLAYVIDEO (Command):
    '''Video playback'''
    options: UInt32 #

@dataclass
class CMD_VIDEOSTART (Command):
    '''Initialize video frame decoder.'''
    pass

@dataclass
class CMD_VIDEOFRAME (Command):
    '''Load the next frame of video.'''
    dst    : UInt32 # memory location to load the frame data
    ptr    : UInt32 # complition pointer

@dataclass
class CMD_MEMCRC (Command):
    '''Compute a CRC-32 for memory'''
    ptr    : UInt32 # starting address of the memory block
    num    : UInt32 # number of bytes in the source memory block
    result : UInt32 # output parameter

@dataclass
class CMD_MEMZERO (Command):
    '''Write zero to a block of memory.'''
    ptr    : UInt32 # starting address of the memory block
    num    : UInt32 # number of bytes in the memory block

@dataclass
class CMD_MEMSET (Command):
    '''Fill memory with a byte value.'''
    ptr    : UInt32 # starting address of the memory block
    value  : UInt32 # value to be written to memory
    num    : UInt32 # number of bytes in the memory block

@dataclass
class CMD_MEMCPY (Command):
    '''Copy a block of memory'''
    dst    : UInt32 # address of the destination memory block
    src    : UInt32 # address of the source memory block
    num    : UInt32 # number of bytes to copy

@dataclass
class CMD_BUTTON (Command):
    '''Draw a button with a UTF-8 label.'''
    x      :  Int16 # X-coordinate of button top-left, in pixels
    y      :  Int16 # Y-coordinate of button top-left, in pixels
    w      :  Int16 # width of button, in pixels
    h      :  Int16 # height of button, in pixels
    font   : UInt16 # bitmap handle to specify the font used in the button label
    options: UInt16 #
    s      : String # button label

@dataclass
class CMD_CLOCK (Command):
    '''Draw an analog clock'''
    x      :  Int16 # x-coordinate of clock center, in pixels
    y      :  Int16 # y-coordinate of clock center, in pixels
    r      :  Int16 #
    options: UInt16 #
    h      : UInt16 # hours
    m      : UInt16 # minutes
    s      : UInt16 # seconds
    ms     : UInt16 # milliseconds

@dataclass
class CMD_FGCOLOR (Command):
    '''Set the foreground color.'''
    c      : UInt32 # new foreground color, as a 24-bit RGB number

    c_str = Command.rgb_str

@dataclass
class CMD_BGCOLOR (Command):
    '''Set the background color'''
    c      : UInt32 # new background color, as a 24-bit RGB number

    c_str = Command.rgb_str

@dataclass
class CMD_GRADCOLOR (Command):
    '''Set the 3D button highlight color.'''
    c      : UInt32 # new highlight gradient color, as a 24-bit RGB number

    c_str = Command.rgb_str

@dataclass
class CMD_GAUGE (Command):
    '''Draw a gauge.'''
    x      :  Int16 # X-coordinate of gauge center, in pixels
    y      :  Int16 # Y-coordinate of gauge center, in pixels
    r      :  Int16 # radius of the gauge
    options: UInt16 #
    major  : UInt16 # number of major subdivisions on the dial
    minor  : UInt16 # number of minor subdivisions on the dial
    val    : UInt16 # gauge indicated value
    range  : UInt16 # maximum value

@dataclass
class CMD_GRADIENT (Command):
    '''Draw a smooth color gradient.'''
    x0     :  Int16 # x-coordinate of point 0, in pixels
    y0     :  Int16 # y-coordinate of point 0, in pixels
    rgb0   : UInt32 # color of point 0, as a 24-bit RGB number
    x1     :  Int16 # x-coordinate of point 1, in pixels
    y1     :  Int16 # y-coordinate of point 1, in pixels
    rgb1   : UInt32 # color of point 1

    rgb0_str = Command.rgb_str
    rgb1_str = Command.rgb_str

@dataclass
class CMD_GRADIENTA (Command):
    '''Draw a smooth color gradient with transparency.'''
    x0     :  Int16 # x-coordinate of point 0, in pixels
    y0     :  Int16 # y-coordinate of point 0, in pixels
    argb0  : UInt32 # color of point 0, as a 32-bit ARGB number
    x1     :  Int16 # x-coordinate of point 1, in pixels
    y1     :  Int16 # y-coordinate of point 1, in pixels
    argb1  : UInt32 # color of point 1

    rgb0_str = Command.argb_str
    rgb1_str = Command.argb_str

@dataclass
class CMD_KEYS (Command):
    '''Draw a row of keys.'''
    x      :  Int16 # x-coordinate of keys top-left, in pixels
    y      :  Int16 # y-coordinate of keys top-left, in pixels
    w      :  Int16 # the width of the keys
    h      :  Int16 # the height of the keys
    font   :  Int16 # bitmap handle to specify the font used in key label
    options: UInt16 #
    s      : String # key labels, one character per key

@dataclass
class CMD_PROGRESS (Command):
    '''Draw a progress bar.'''
    x      :  Int16 # x-coordinate of progress bar top-left, in pixels
    y      :  Int16 # y-coordinate of progress bar top-left, in pixels
    w      :  Int16 # width of progress bar, in pixels
    h      :  Int16 # height of progress bar, in pixels
    options: UInt16 #
    val    : UInt16 # displayed value of progress bar
    range  : UInt16 # maximum value

@dataclass
class CMD_SCROLLBAR (Command):
    '''Draw a scroll bar.'''
    x      :  Int16 # x-coordinate of scroll bar top-left, in pixels
    y      :  Int16 # y-coordinate of scroll bar top-left, in pixels
    w      :  Int16 # width of scroll bar, in pixels
    h      :  Int16 # height of scroll bar, in pixels
    options: UInt16 #
    val    : UInt16 # displayed value of scroll bar
    size   : UInt16 #
    range  : UInt16 # maximum value

@dataclass
class CMD_SLIDER (Command):
    '''Draw a slider.'''
    x      :  Int16 # x-coordinate of slider top-left, in pixels
    y      :  Int16 # y-coordinate of slider top-left, in pixels
    w      :  Int16 # width of slider, in pixels
    h      :  Int16 # height of slider, in pixels
    options: UInt16 #
    val    : UInt16 # displayed value of slider
    range  : UInt16 # maximum value

@dataclass
class CMD_DIAL (Command):
    '''Draw a rotary dial control.'''
    x      :  Int16 # x-coordinate of dial center, in pixels
    y      :  Int16 # y-coordinate of dial center, in pixels
    r      :  Int16 # radius of dial, in pixels
    options: UInt16 #
    val    : UInt16 # specify the position of dial points

@dataclass
class CMD_TOGGLE (Command):
    '''Draw a toggle switch with UTF-8 labels.'''
    x      :  Int16 # x-coordinate of top-left of toggle, in pixels
    y      :  Int16 # y-coordinate of top-left of toggle, in pixels
    w      :  Int16 # width of toggle, in pixels
    font   :  Int16 # font to use for text
    options: UInt16 #
    state  : UInt16 # state of the toggle
    s      : String # string labels for toggle,UTF-8 encoding

@dataclass
class CMD_FILLWIDTH (Command):
    '''Set the text fill width.'''
    s      : UInt32 # line fill width, in pixels

    s_str = Command._px_str

@dataclass
class CMD_TEXT (Command):
    '''Draw a UTF-8 text string.'''
    x      :  Int16 # x-coordinate of text base, in pixels
    y      :  Int16 # y-coordinate of text base, in pixels
    font   :  Int16 # font to use for text
    options: UInt16 #
    s      : String # text string, UTF-8 encoding

@dataclass
class CMD_SETBASE (Command):
    '''Set the base for number output.'''
    b      : UInt32 # numeric base

@dataclass
class CMD_NUMBER (Command):
    '''Draw a number.'''
    x      :  Int16 # x-coordinate of text base, in pixels
    y      :  Int16 # y-coordinate of text base, in pixels
    font   :  Int16 # font to use for text
    options: UInt16 #
    n      :  Int32 # the number to display

@dataclass
class CMD_LOADIDENTIY (Command):
    '''Set the current matrix to the identity matrix.'''
    pass

@dataclass
class CMD_SETMATRIX (Command):
    '''Write the current matrix to the display list.'''
    pass

@dataclass
class CMD_GETMATRIX (Command):
    '''Retrieves the current matrix coefficient.'''
    a      :  Int32 # output parameter; written with matrix coefficient a
    b      :  Int32 # output parameter; written with matrix coefficient b
    c      :  Int32 # output parameter; written with matrix coefficient c
    d      :  Int32 # output parameter; written with matrix coefficient d
    e      :  Int32 # output parameter; written with matrix coefficient e
    f      :  Int32 # output parameter; written with matrix coefficient f

@dataclass
class CMD_GETPTR (Command):
    '''Get the end memory address of data inflated by CMD_INFLATE.'''
    result : UInt32 # the end address of decompressed data

@dataclass
class CMD_GETPROPS (Command):
    '''Get the image properties decompressed by CMD_LOADIMAGE.'''
    ptr    : UInt32 # the address of the image in RAM_G
    width  : UInt32 # the width of the image
    height : UInt32 # the height of the image

@dataclass
class CMD_SCALE (Command):
    '''Apply a scale to the current matrix.'''
    sx     :  Int32 # x scale factor
    sy     :  Int32 # y scale factor

@dataclass
class CMD_ROTATE (Command):
    '''Apply a rotation to the current matrix.'''
    a      :  Int32 # clockwise rotation angle

@dataclass
class CMD_ROTATEAROUND (Command):
    '''Apply a rotation and scale around a specified coordinate.'''
    x      :  Int32 # center of rotation/scaling, x-coordinate
    y      :  Int32 # center of rotation/scaling, x-coordinate
    a      :  Int32 # clockwise rotation angle
    s      :  Int32 # scale factor

@dataclass
class CMD_TRANSLATE (Command):
    '''Apply a translation to the current matrix.'''
    tx     :  Int32 # x translate factor
    ty     :  Int32 # y translate factor

@dataclass
class CMD_CALIBRATE (Command):
    '''Execute the touch screen calibration routine.'''
    result : UInt32 # output parameter; written with 0 on failure of calibration

@dataclass
class CMD_SETROTATE (Command):
    '''Rotate the screen.'''
    r      : UInt32 # same definition as the value in REG_ROTATE

@dataclass
class CMD_SPINNER (Command):
    '''Start an animated spinner.'''
    x      :  Int16 # the X coordinate of top left of spinner
    y      :  Int16 # the Y coordinate of top left of spinner
    style  : UInt16 # the style of spinner
    scale  : UInt16 # the scaling coefficient of spinner

@dataclass
class CMD_SCREENSAVER (Command):
    '''Start an animated screensaver.'''
    pass

@dataclass
class CMD_SKETCH (Command):
    '''Start a continuous sketch update.'''
    x      :  Int16 # x-coordinate of sketch area top-left, in pixels
    y      :  Int16 # y-coordinate of sketch area top-left, in pixels
    w      : UInt16 # width of sketch area, in pixels
    h      : UInt16 # height of sketch area, in pixels
    ptr    : UInt32 # base address of sketch bitmap
    format : UInt16 # format of sketch bitmap

@dataclass
class CMD_STOP (Command):
    '''Stop any of spinner, screensaver or sketch.'''
    pass

@dataclass
class CMD_SETFONT (Command):
    '''Set up a custom font.'''
    font   : UInt32 # the bitmap handle
    ptr    : UInt32 # the metrics block address in RAM_G

@dataclass
class CMD_SETFONT2 (Command):
    '''Set up a custom font.'''
    font     : UInt32 # the bitmap handle
    ptr      : UInt32 # 32 bit aligned memory address in RAM_G of font metrics block
    firstchar: UInt32 # the ASCII value of first character in the font

@dataclass
class CMD_SETSCRATCH (Command):
    '''Set the scratch bitmap for widget use.'''
    handle : UInt32 # bitmap handle number

@dataclass
class CMD_ROMFONT (Command):
    '''Load a ROM font into bitmap handle.'''
    font   : UInt32 # bitmap handle number
    romslot: UInt32 # ROM font number

@dataclass
class CMD_RESETFONTS (Command):
    '''Reset ROM fonts to default bitmap handle.'''
    pass

@dataclass
class CMD_TRACK (Command):
    '''Track touches for a graphics object.'''
    x      :  Int16 # x-coordinate of track area
    y      :  Int16 # y-coordinate of track area
    w      :  Int16 # width of track area
    h      :  Int16 # height of track area
    tag    :  Int16 # tag of the graphics object to be tracked

@dataclass
class CMD_SNAPSHOT (Command):
    '''Take a snapshot of the current screen.'''
    ptr    : UInt32 # snapshot destination address, in RAM_G

@dataclass
class CMD_SNAPSHOT2 (Command):
    '''Take a snapshot of part of the current screen.'''
    fmt    : UInt32 # output bitmap format
    ptr    : UInt32 # snapshot destination address, in RAM_G
    x      :  Int16 # x-coordinate of snapshot area
    y      :  Int16 # y-coordinate of snapshot area
    w      :  Int16 # width of snapshot area
    h      :  Int16 # height of snapshot area

@dataclass
class CMD_SETBITMAP (Command):
    '''Set up display list for bitmap.'''
    source : UInt32 # source address for bitmap
    fmt    : UInt16 # bitmap format
    width  : UInt16 # bitmap width, in pixels
    height : UInt16 # bitmap height, in pixels

@dataclass
class CMD_LOGO (Command):
    '''Play Bridgetek logo animation.'''
    pass

@dataclass
class CMD_FLASHERASE (Command):
    '''Erase all of FLASH.'''
    pass

@dataclass
class CMD_FLASHWRITE (Command):
    '''Write data to FLASH.'''
    ptr    : UInt32 # destination address in flash memory
    num    : UInt32 # number of bytes to write

@dataclass
class CMD_FLASHREAD (Command):
    '''Read data from FLASH to main memory.'''
    dest   : UInt32 # destination address in RAM_G
    src    : UInt32 # source address in flash memory
    num    : UInt32 # number of bytes to write

@dataclass
class CMD_APPENDF (Command):
    '''Append FLASH Data to RAM_DL.'''
    ptr    : UInt32 # start of source commands in flash memory
    num    : UInt32 # number of bytes to copy

@dataclass
class CMD_FLASHUPDATE (Command):
    '''Write data to FLASH, erasing if necessary.'''
    dest   : UInt32 # destination address in flash memory
    src    : UInt32 # source address in main memory RAM_G
    num    : UInt32 # number of bytes to write

@dataclass
class CMD_FLASHDETACH (Command):
    '''Detach from FLASH.'''
    pass

@dataclass
class CMD_FLASHATTACH (Command):
    '''Attach to FLASH.'''
    pass

@dataclass
class CMD_FLASHFAST (Command):
    '''Enter full-speed mode.'''
    result : UInt32 # written with the result code

@dataclass
class CMD_FLASHSPIDESEL (Command):
    '''SPI bus: deselect device.'''
    pass

@dataclass
class CMD_FLASHSPITX (Command):
    '''SPI bus: write bytes.'''
    num    : UInt32 # number of bytes to transmit

@dataclass
class CMD_FLASHSPIRX (Command):
    '''SPI bus: read bytes.'''
    ptr    : UInt32 # destination address in RAM_G
    num    : UInt32 # number of bytes to receive

@dataclass
class CMD_CLEARCACHE (Command):
    '''Clear the FLASH cache.'''
    pass

@dataclass
class CMD_FLASHSOURCE (Command):
    '''Specify the FLASH source address.'''
    ptr    : UInt32 # flash address

@dataclass
class CMD_VIDEOSTARTF (Command):
    '''Initialize video frame decoder.'''
    pass

@dataclass
class CMD_ANIMSTART (Command):
    '''Start an animation.'''
    ch     :  Int32 # animation channel
    aoptr  : UInt32 # the address of the animation object in flash memory
    loop   : UInt32 # loop flag

@dataclass
class CMD_ANIMSTOP (Command):
    '''Stop an animation.'''
    ch     :  Int32 # animation channel

@dataclass
class CMD_ANIMXY (Command):
    '''Set the coordinates of an animation.'''
    ch     :  Int32 # animation channel
    x      :  Int16 # x screen coordinate for the animation center, in pixels
    y      :  Int16 # y screen coordinate for the animation center, in pixels

@dataclass
class CMD_ANIMDRAW (Command):
    '''Draw active animations.'''
    ch     :  Int32 # animation channel

@dataclass
class CMD_ANIMFRAME (Command):
    '''Render one frame of an animation.'''
    x      :  Int16 # x screen coordinate for the animation center, in pixels
    y      :  Int16 # y screen coordinate for the animation center, in pixels
    aoptr  : UInt32 # the address of the animation object in flash memory
    frame  : UInt32 # frame number to draw

@dataclass
class CMD_SYNC (Command):
    '''Synchronize with video blanking.'''
    pass

@dataclass
class CMD_BITMAP_TRANSFORM (Command):
    '''Compute a bitmap transform matrix.'''
    x0     :  Int32 # point 0 screen coordinate, in pixels
    y0     :  Int32 # point 0 screen coordinate, in pixels
    x1     :  Int32 # point 1 screen coordinate, in pixels
    y1     :  Int32 # point 1 screen coordinate, in pixels
    x2     :  Int32 # point 2 screen coordinate, in pixels
    y2     :  Int32 # point 2 screen coordinate, in pixels
    tx0    :  Int32 # point 0 bitmap coordinate, in pixels
    ty0    :  Int32 # point 0 bitmap coordinate, in pixels
    tx1    :  Int32 # point 1 bitmap coordinate, in pixels
    ty1    :  Int32 # point 1 bitmap coordinate, in pixels
    tx2    :  Int32 # point 2 bitmap coordinate, in pixels
    ty2    :  Int32 # point 2 bitmap coordinate, in pixels
    result : UInt16 # result return

