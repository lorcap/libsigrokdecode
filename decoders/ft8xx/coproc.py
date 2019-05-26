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

from typing import List
from dataclasses import dataclass
from . import annotation

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
    def options_str (self) -> str:
        '''Options.'''
        return 'Fix me!'

@dataclass
class Parameter (annotation.Annotation):
    '''Parameter of type uint32_t.'''
    val: int    # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.PARAMETER

    @property
    def strings_ (self) -> List[str]:
        return [self.name_.lower() + '_t: ' + self._int_str(self.val)]

@dataclass
class Int16 (Parameter):
    '''Parameter of type `int16_t`.'''
    pass

@dataclass
class UInt16 (Parameter):
    '''Parameter of type `uint16_t`.'''

@dataclass
class UInt32 (Parameter):
    '''Parameter of type `uint32_t`.'''

@dataclass
class String (Parameter):
    '''Parameter of null-terminated `const char*`.'''

    @property
    def strings_ (self) -> List[str]:
        return ['const char*: ' + self.val]

# ------------------------------------------------------------------------- #

@dataclass
class CMD_DLSTART (Command):
    '''Start a new Display List.'''
    pass

@dataclass
class CMD_INTERRUPT (Command):
    '''Trigger interrupt INT_CMDFLAG.'''
    ms: UInt32      # delay before the interrupt triggers, in milliseconds

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

@dataclass
class CMD_INFLATE (Command):
    '''Decompress data into memory.'''
    ptr    : UInt32 # destination address in RAM_G
    data   : int

@dataclass
class CMD_INFLATE2 (Command):
    '''Decompress data into memory.'''
    ptr    : UInt32 # destination address to put the decompressed data
    options: UInt32 #
    data   : int

@dataclass
class CMD_LOADIMAGE (Command):
    '''Load a JPEG or PNG image.'''
    ptr    : UInt32 # destination address
    options: UInt32 #
    data   : int

@dataclass
class CMD_MEDIAFIFO (Command):
    '''Set up a streaming media FIFO'''
    ptr    : UInt32 # starting address of memory block
    size   : UInt32    # number of bytes in the source memory block

@dataclass
class CMD_PLAYVIDEO (Command):
    '''Video playback'''
    opts   : UInt32 #
    data   : int

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
    dest   : UInt32 # address of the destination memory block
    src    : UInt32 # address of the source memory block
    num    : UInt32 # number of bytes to copy

@dataclass
class CMD_BUTTON (Command):
    '''Draw a button with a UTF-8 label.'''
    x      :  Int16 # X-coordinate of button top-left, in pixels
    y      :  Int16 # Y-coordinate of button top-left, in pixels
    w      :  Int16 # width of button, in pixels
    h      :  Int16 # height of button, in pixels
    font   :  Int16 # bitmap handle to specify the font used in the button label
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

@dataclass
class CMD_BGCOLOR (Command):
    '''Set the background color'''
    c      : UInt32 # new background color, as a 24-bit RGB number

@dataclass
class CMD_GRADCOLOR (Command):
    '''Set the 3D button highlight color.'''
    c      : UInt32 # new highlight gradient color, as a 24-bit RGB number

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

@dataclass
class CMD_GRADIENTA (Command):
    '''Draw a smooth color gradient with transparency.'''
    x0     :  Int16 # x-coordinate of point 0, in pixels
    y0     :  Int16 # y-coordinate of point 0, in pixels
    argb0  : UInt32 # color of point 0, as a 32-bit ARGB number
    x1     :  Int16 # x-coordinate of point 1, in pixels
    y1     :  Int16 # y-coordinate of point 1, in pixels
    argb1  : UInt32 # color of point 1

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

@dataclass
class CMD_TEXT (Command):
    '''Draw a UTF-8 text string.'''
    x      :  Int16 # x-coordinate of text base, in pixels
    y      :  Int16 # y-coordinate of text base, in pixels
    font   :  Int16 # font to use for text
    options: UInt16 #
    s      : String # text string, UTF-8 encoding

