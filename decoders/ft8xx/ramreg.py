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
from . import annotation, warning

@dataclass
class Reg (annotation.Command):
    '''Base class for all register annotations.'''

    @property
    def val (self):
        return self.val_

    @property
    def id_ (self) -> int:
        return annotation.Id.RAMREG

    #--- private ---#

    def _field_names (self) -> List[str]:
        return ['val_']

@dataclass(frozen=True)
class Sound:
    effect: str
    continuous: str
    pitch_adjust: str

sound = {
        0x00: Sound('silence'      , True , False),
        0x01: Sound('square wave'  , True , True ),
        0x02: Sound('sine wave'    , True , True ),
        0x03: Sound('sawtooth wave', True , True ),
        0x04: Sound('triangle wave', True , True ),
        0x05: Sound('beeping'      , True , True ),
        0x06: Sound('alarm'        , True , True ),
        0x07: Sound('warble'       , True , True ),
        0x08: Sound('carousel'     , True , True ),
        0x10: Sound('1 short pip'  , False, True ),
        0x11: Sound('2 short pips' , False, True ),
        0x12: Sound('3 short pips' , False, True ),
        0x13: Sound('4 short pips' , False, True ),
        0x14: Sound('5 short pips' , False, True ),
        0x15: Sound('6 short pips' , False, True ),
        0x16: Sound('7 short pips' , False, True ),
        0x17: Sound('8 short pips' , False, True ),
        0x18: Sound('9 short pips' , False, True ),
        0x19: Sound('10 short pips', False, True ),
        0x1a: Sound('11 short pips', False, True ),
        0x1b: Sound('12 short pips', False, True ),
        0x1c: Sound('13 short pips', False, True ),
        0x1d: Sound('14 short pips', False, True ),
        0x1e: Sound('15 short pips', False, True ),
        0x1f: Sound('16 short pips', False, True ),
        0x23: Sound('DTMF #'       , True , False),
        0x2c: Sound('DTMF *'       , True , False),
        0x30: Sound('DTMF 0'       , True , False),
        0x31: Sound('DTMF 1'       , True , False),
        0x32: Sound('DTMF 2'       , True , False),
        0x33: Sound('DTMF 3'       , True , False),
        0x34: Sound('DTMF 4'       , True , False),
        0x35: Sound('DTMF 5'       , True , False),
        0x36: Sound('DTMF 6'       , True , False),
        0x37: Sound('DTMF 7'       , True , False),
        0x38: Sound('DTMF 8'       , True , False),
        0x39: Sound('DTMF 9'       , True , False),
        0x40: Sound('harp'         , False, True ),
        0x41: Sound('xylophone'    , False, True ),
        0x42: Sound('tuba'         , False, True ),
        0x43: Sound('glockenspiel' , False, True ),
        0x44: Sound('organ'        , False, True ),
        0x45: Sound('trumpet'      , False, True ),
        0x46: Sound('piano'        , False, True ),
        0x47: Sound('chimes'       , False, True ),
        0x48: Sound('music box'    , False, True ),
        0x49: Sound('bell'         , False, True ),
        0x50: Sound('click'        , False, False),
        0x51: Sound('switch'       , False, False),
        0x52: Sound('cowbell'      , False, False),
        0x53: Sound('notch'        , False, False),
        0x54: Sound('hihat'        , False, False),
        0x55: Sound('kickdrum'     , False, False),
        0x56: Sound('pop'          , False, False),
        0x57: Sound('clack'        , False, False),
        0x58: Sound('chack'        , False, False),
        0x60: Sound('mute'         , False, False),
        0x61: Sound('unmute'       , False, False),
}

note = {    24: 'C1' , 36: 'C2' , 48: 'C3' , 60: 'C4' , 72: 'C5' , 84: 'C6' ,  96: 'C7' , 108: 'C8',\
            25: 'Cs1', 37: 'Cs2', 49: 'Cs3', 61: 'Cs4', 73: 'Cs5', 85: 'Cs6',  97: 'Cs7',           \
            26: 'D1' , 38: 'D2' , 50: 'D3' , 62: 'D4' , 74: 'D5' , 86: 'D6' ,  98: 'D7' ,           \
            27: 'Ds1', 39: 'Ds2', 51: 'Ds3', 63: 'Ds4', 75: 'Ds5', 87: 'Ds6',  99: 'Ds7',           \
            28: 'E1' , 40: 'E2' , 52: 'E3' , 64: 'E4' , 76: 'E5' , 88: 'E6' , 100: 'E7' ,           \
            29: 'F1' , 41: 'F2' , 53: 'F3' , 65: 'F4' , 77: 'F5' , 89: 'F6' , 101: 'F7' ,           \
            30: 'Fs1', 42: 'Fs2', 54: 'Fs3', 66: 'Fs4', 78: 'Fs5', 90: 'Fs6', 102: 'Fs7',           \
            31: 'G1' , 43: 'G2' , 55: 'G3' , 67: 'G4' , 79: 'G5' , 91: 'G6' , 103: 'G7' ,           \
            32: 'Gs1', 44: 'Gs2', 56: 'Gs3', 68: 'Gs4', 80: 'Gs5', 92: 'Gs6', 104: 'Gs7',           \
21: 'A0' ,  33: 'A1' , 45: 'A2' , 57: 'A3' , 69: 'A4' , 81: 'A5' , 93: 'A6' , 105: 'A7' ,           \
22: 'As0',  34: 'As1', 46: 'As2', 58: 'As3', 70: 'As4', 82: 'As5', 94: 'As6', 106: 'As7',           \
23: 'B0' ,  35: 'B1' , 47: 'B2' , 59: 'B3' , 71: 'B4' , 83: 'B5' , 95: 'B6' , 107: 'B7' ,           }

# ------------------------------------------------------------------------- #

@dataclass
class REG_ID (Reg):
    '''Identification register.'''
    pass

@dataclass
class REG_FRAMES (Reg):
    '''Frame counter, since reset.'''
    pass

@dataclass
class REG_CLOCK (Reg):
    '''Clock cycles, since reset.'''
    pass

@dataclass
class REG_FREQUENCY (Reg):
    '''Main clock frequency (Hz).'''

    @property
    def val_str (self) -> str:
        if   self.val >= 10**6: return str(self.val/10**6) + 'MHz'
        elif self.val >= 10**3: return str(self.val/10**3) + 'kHz'
        else                  : return str(self.val      ) + 'Hz'

@dataclass
class REG_RENDERMODE (Reg):
    '''Rendering mode.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'normal'
        elif self.val == 1: return 'single-line'
        else              : return ''

@dataclass
class REG_SNAPY (Reg):
    '''Scanline select for RENDERMODE 1.'''
    pass

@dataclass
class REG_SNAPSHOT (Reg):
    '''Trigger for RENDERMODE 1'''
    pass

@dataclass
class REG_SNAPFORMAT (Reg):
    '''Pixel format for scanline readout.'''
    pass

@dataclass
class REG_CPURESET (Reg):
    '''Graphics, audio and touch engines reset control.'''

    @property
    def val_str (self) -> str:
        ret = list()
        if self.val & 0b100: ret.append('audio')
        if self.val & 0b010: ret.append('touch')
        if self.val & 0b001: ret.append('graphics')
        if ret:
            return ','.join(ret)
        else:
            return '(none)'

@dataclass
class REG_TAP_CRC (Reg):
    '''Live video tap CRC.'''
    pass

@dataclass
class REG_TAP_MASK (Reg):
    '''Live video tap mask.'''
    pass

@dataclass
class REG_HCYCLE (Reg):
    '''Horizontal total cycle count.'''
    pass

@dataclass
class REG_HOFFSET (Reg):
    '''Horizontal display start offset.'''
    pass

@dataclass
class REG_HSIZE (Reg):
    '''Horizontal display pixel count.'''
    pass

@dataclass
class REG_HSYNC0 (Reg):
    '''Horizontal sync fall offset.'''
    pass

@dataclass
class REG_HSYNC1 (Reg):
    '''Horizontal sync rise offset.'''
    pass

@dataclass
class REG_VCYCLE (Reg):
    '''Vertical total cycle count.'''
    pass

@dataclass
class REG_VOFFSET (Reg):
    '''Vertical display start offset.'''
    pass

@dataclass
class REG_VSIZE (Reg):
    '''Vertical display line count.'''
    pass

@dataclass
class REG_VSYNC0 (Reg):
    '''Vertical sync fall offset.'''
    pass

@dataclass
class REG_VSYNC1 (Reg):
    '''Vertical sync rise offset.'''
    pass

@dataclass
class REG_DLSWAP (Reg):
    '''Display list swap control.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0b00: return 'ready'
        elif self.val == 0b01: return 'line'
        elif self.val == 0b10: return 'frame'
        else             : return ''

@dataclass
class REG_ROTATE (Reg):
    '''Screen rotation control.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0b000: return 'landscape'
        elif self.val == 0b001: return 'inverted landscape'
        elif self.val == 0b010: return 'potrait'
        elif self.val == 0b011: return 'inverted potrait'
        elif self.val == 0b100: return 'mirrored landscape'
        elif self.val == 0b101: return 'mirrored inverted landscape'
        elif self.val == 0b110: return 'mirrored potrait'
        elif self.val == 0b111: return 'mirrored inverted potrait'
        else                  : return ''

@dataclass
class REG_OUTBITS (Reg):
    '''Output bit resolution.'''
    red: int    # red color signal lines number
    green: int  # green color signal lines number
    blue: int   # blue color signal lines number

    def _outbit_str (self, val: int) -> str:
        lines = 8 if val == 0 else val
        return f'{lines} lines'

    @property
    def red_str (self) -> str:
        return self._outbit_str(self.red)

    @property
    def green_str (self) -> str:
        return self._outbit_str(self.green)

    @property
    def blue_str (self) -> str:
        return self._outbit_str(self.blue)

@dataclass
class REG_DITHER (Reg):
    '''Output dither enable.'''
    pass

@dataclass
class REG_SWIZZLE (Reg):
    '''Output RGB signal swizzle.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0b0000\
          or self.val == 0b0100: return 'R[7:0] G[7:0] B[7:0]'
        elif self.val == 0b0001\
          or self.val == 0b0101: return 'R[0:7] G[0:7] B[0:7]'
        elif self.val == 0b0010\
          or self.val == 0b0110: return 'B[7:0] G[7:0] R[7:0]'
        elif self.val == 0b0011\
          or self.val == 0b0111: return 'B[0:7] G[0:7] R[0:7]'
        elif self.val == 0b1000: return 'B[7:0] R[7:0] G[7:0]'
        elif self.val == 0b1001: return 'B[0:7] R[0:7] G[0:7]'
        elif self.val == 0b1010: return 'G[7:0] R[7:0] B[7:0]'
        elif self.val == 0b1011: return 'G[0:7] R[0:7] B[0:7]'
        elif self.val == 0b1100: return 'G[7:0] B[7:0] R[7:0]'
        elif self.val == 0b1101: return 'G[0:7] B[0:7] R[0:7]'
        elif self.val == 0b1110: return 'R[7:0] B[7:0] G[7:0]'
        elif self.val == 0b1111: return 'R[0:7] B[0:7] G[0:7]'
        else                   : return ''

@dataclass
class REG_CSPREAD (Reg):
    '''Output clock spreading enable.'''
    pass

@dataclass
class REG_PCLK_POL (Reg):
    '''PCLK polarity.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'rising edge'
        elif self.val == 1: return 'falling edge'
        else              : return ''

@dataclass
class REG_PCLK (Reg):
    '''PCLK frequency divider.'''

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'disable'
        else              : return '÷'+self.val

@dataclass
class REG_TAG_Y (Reg):
    '''Tag query Y coordinate.'''
    pass

@dataclass
class REG_TAG_X (Reg):
    '''Tag query X coordinate.'''
    pass

@dataclass
class REG_TAG (Reg):
    '''Tag query result.'''
    pass

@dataclass
class REG_VOL_PB (Reg):
    '''Volume for playback.'''
    pass

@dataclass
class REG_VOL_SOUND (Reg):
    '''Volume for synthesizer sound.'''
    pass

@dataclass
class REG_SOUND (Reg):
    '''Sound effect select.'''

    @property
    def val_str (self) -> str:
        s = sound[(self.val >> 8) & 0xff]
        n = note [(self.val >> 0) & 0xff]
        ret = repr(s)
        if s.pitch_adjust:
            ret += ', Note=' + n
        return ret

