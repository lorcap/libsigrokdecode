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
    val_: int   # raw value

    @property
    def val (self):
        return self.val_

    @property
    def id_ (self) -> int:
        return annotation.Id.RAMREG

    def parameters (self) -> List[str]:
        return ['val_']

    @static_method
    def _pin_dir_str (dir_: bool) -> str:
        return 'output' if dir_ else 'input'

    @staticmethod
    def _pin_level_str (lvl: int) -> str:
        return 'high' if lvl else 'low'

    @staticmethod
    def _pin_strength2 (strength: int) -> str:
        if   strength == 0b0: return '1.2mA'
        elif strength == 0b1: return '2.4mA'
        else                : return ''

    @staticmethod
    def _pin_strength4 (strength: int) -> str:
        if   strength == 0b00: return '5mA'
        elif strength == 0b01: return '10mA'
        elif strength == 0b10: return '15mA'
        elif strength == 0b11: return '20mA'
        else                 : return ''

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
    addr = 0x302000
    bits = 8

@dataclass
class REG_FRAMES (Reg):
    '''Frame counter, since reset.'''
    addr = 0x302004
    bits = 32

@dataclass
class REG_CLOCK (Reg):
    '''Clock cycles, since reset.'''
    addr = 0x302008
    bits = 32

@dataclass
class REG_FREQUENCY (Reg):
    '''Main clock frequency (Hz).'''
    addr = 0x30200c
    bits = 28

    @property
    def val_str (self) -> str:
        if   self.val >= 10**6: return str(self.val/10**6) + 'MHz'
        elif self.val >= 10**3: return str(self.val/10**3) + 'kHz'
        else                  : return str(self.val      ) + 'Hz'

@dataclass
class REG_RENDERMODE (Reg):
    '''Rendering mode.'''
    addr = 0x302010
    bits = 1

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'normal'
        elif self.val == 1: return 'single-line'
        else              : return ''

@dataclass
class REG_SNAPY (Reg):
    '''Scanline select for RENDERMODE 1.'''
    addr = 0x302014
    bits = 11

@dataclass
class REG_SNAPSHOT (Reg):
    '''Trigger for RENDERMODE 1'''
    addr = 0x302018
    bits = 1

@dataclass
class REG_SNAPFORMAT (Reg):
    '''Pixel format for scanline readout.'''
    addr = 0x30201c
    bits = 6

@dataclass
class REG_CPURESET (Reg):
    '''Graphics, audio and touch engines reset control.'''
    addr = 0x302020
    bits = 3

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
    addr = 0x302024
    bits = 32

@dataclass
class REG_TAP_MASK (Reg):
    '''Live video tap mask.'''
    addr = 0x302028
    bits = 32

@dataclass
class REG_HCYCLE (Reg):
    '''Horizontal total cycle count.'''
    addr = 0x30202c
    bits = 12

@dataclass
class REG_HOFFSET (Reg):
    '''Horizontal display start offset.'''
    addr = 0x302030
    bits = 12

@dataclass
class REG_HSIZE (Reg):
    '''Horizontal display pixel count.'''
    addr = 0x302034
    bits = 12

@dataclass
class REG_HSYNC0 (Reg):
    '''Horizontal sync fall offset.'''
    addr = 0x302038
    bits = 12

@dataclass
class REG_HSYNC1 (Reg):
    '''Horizontal sync rise offset.'''
    addr = 0x30203c
    bits = 12

@dataclass
class REG_VCYCLE (Reg):
    '''Vertical total cycle count.'''
    addr = 0x302040
    bits = 12

@dataclass
class REG_VOFFSET (Reg):
    '''Vertical display start offset.'''
    addr = 0x302044
    bits = 12

@dataclass
class REG_VSIZE (Reg):
    '''Vertical display line count.'''
    addr = 0x302048
    bits = 12

@dataclass
class REG_VSYNC0 (Reg):
    '''Vertical sync fall offset.'''
    addr = 0x30204c
    bits = 10

@dataclass
class REG_VSYNC1 (Reg):
    '''Vertical sync rise offset.'''
    addr = 0x302050
    bits = 10

@dataclass
class REG_DLSWAP (Reg):
    '''Display list swap control.'''
    addr = 0x302054
    bits = 2

    @property
    def val_str (self) -> str:
        if   self.val == 0b00: return 'ready'
        elif self.val == 0b01: return 'line'
        elif self.val == 0b10: return 'frame'
        else             : return ''

@dataclass
class REG_ROTATE (Reg):
    '''Screen rotation control.'''
    addr = 0x302058
    bits = 3

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
    addr = 0x30205c
    bits = 9

    @staticmethod
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
    addr = 0x302060
    bits = 1

@dataclass
class REG_SWIZZLE (Reg):
    '''Output RGB signal swizzle.'''
    addr = 0x302064
    bits = 4

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
    addr = 0x302068
    bits = 1

@dataclass
class REG_PCLK_POL (Reg):
    '''PCLK polarity.'''
    addr = 0x30206c
    bits = 1

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'rising edge'
        elif self.val == 1: return 'falling edge'
        else              : return ''

@dataclass
class REG_PCLK (Reg):
    '''PCLK frequency divider.'''
    addr = 0x302070
    bits = 8

    @property
    def val_str (self) -> str:
        if   self.val == 0: return 'disable'
        else              : return '÷'+self.val

@dataclass
class REG_TAG_X (Reg):
    '''Tag query X coordinate.'''
    addr = 0x302074
    bits = 11

@dataclass
class REG_TAG_Y (Reg):
    '''Tag query Y coordinate.'''
    addr = 0x302078
    bits = 11

@dataclass
class REG_TAG (Reg):
    '''Tag query result.'''
    addr = 0x30207c
    bits = 8

@dataclass
class REG_VOL_PB (Reg):
    '''Volume for playback.'''
    addr = 0x302080
    bits = 8

@dataclass
class REG_VOL_SOUND (Reg):
    '''Volume for synthesizer sound.'''
    addr = 0x302084
    bits = 8

@dataclass
class REG_SOUND (Reg):
    '''Sound effect select.'''
    addr = 0x302088
    bits = 16

    @property
    def val_str (self) -> str:
        s = sound[(self.val >> 8) & 0xff]
        n = note [(self.val >> 0) & 0xff]
        ret = repr(s)
        if s.pitch_adjust:
            ret += ', Note=' + n
        return ret

@dataclass
class REG_PLAY (Reg):
    '''Start effect playback.'''
    addr = 0x30208c
    bits = 1

@dataclass
class REG_GPIO_DIR (Reg):
    '''Legacy GPIO pin direction.'''
    DISP: bool  # direction of pin DISP
    GPIO1: bool # direction of GPIO1
    GPIO0: bool # direction of GPIO0
    addr = 0x302090
    bits = 8

    @property
    def DISP_str (self) -> str:
        return self._pin_dir_str(self.DISP)

    @property
    def GPIO1_str (self) -> str:
        return self._pin_dir_str(self.GPIO1)

    @property
    def GPIO0_str (self) -> str:
        return self._pin_dir_str(self.GPIO0)

@dataclass
class REG_GPIO (Reg):
    '''Legacy GPIO read/write.'''
    DISP: int   # high or low level of pin DISP
    GPIO: int   # drive strength settings for pins GPIO0, GPIO1, CTP_RST_N
    LCD: int    # drive strength settings for pins PCLK, DISP, VSYNC, HSYNC,DE, R, G, B, BACKLIGHT
    SPI: int    # drive Strength Setting for pins MISO, MOSI, INT_N
    GPIO1: int  # high or low level of pin GPIO1
    GPIO0: int  # high or low level of pin GPIO0
    addr = 0x302094
    bits = 8

    @property
    def DISP_str (self) -> str:
        return self._pin_level(self.DISP)

    @property
    def LCD_str (self) -> str:
        return self._pin_strength4(self.LCD)

    @property
    def GPIO_str (self) -> str:
        return self._pin_strength2(self.GPIO)

    @property
    def SPI_str (self) -> str:
        return self._pin_strength4(self.SPI)

    @property
    def GPIO1_str (self) -> str:
        return self._pin_level(self.GPIO1)

    @property
    def GPIO0_str (self) -> str:
        return self._pin_level(self.GPIO0)

@dataclass
class REG_GPIOX_DIR (Reg):
    '''Extended GPIO pin direction.'''
    DISP: bool  # direction of pin DISP
    GPIO3: bool # direction of GPIO3
    GPIO2: bool # direction of GPIO2
    GPIO1: bool # direction of GPIO1
    GPIO0: bool # direction of GPIO0
    addr = 0x302098
    bits = 16

    DISP_str = REG_GPIO_DIR.DISP_str

    @property
    def GPIO3_str (self) -> str:
        return self._pin_dir_str(self.GPIO3)

    @property
    def GPIO2_str (self) -> str:
        return self._pin_dir_str(self.GPIO2)

    GPIO1_str = REG_GPIO_DIR.GPIO1_str
    GPIO0_str = REG_GPIO_DIR.GPIO0_str

@dataclass
class REG_GPIOX (Reg):
    '''Extended GPIO read/write.'''
    DISP: int   # high or low level of pin DISP
    GPIO: int   # drive strength settings for pins GPIO0,GPIO1, GPIO2, GPIO3, CTP_RST_N
    LCD: int    # drive strength settings for pins PCLK, DISP, VSYNC, HSYNC, DE, R, G, B, BACKLIGHT
    SPI: int    # drive Strength Setting for pins MISO, MOSI, INT_N, IO2, IO3, SPIM_SCLK, SPIM_SS_N, SPIM_MOSI, SPIM_MISO, SPIM_IO2, SPIM_IO3
    GPIO3: int  # high or low level of pin GPIO3
    GPIO2: int  # high or low level of pin GPIO2
    GPIO1: int  # high or low level of pin GPIO1
    GPIO0: int  # high or low level of pin GPIO0
    addr = 0x30209c
    bits = 16

    DISP_str = REG_GPIO.DISP_str
    GPIO_str = REG_GPIO.GPIO_str
    LCD_str  = REG_GPIO.LCD_str
    SPI_str  = REG_GPIO.SPI_str

    @property
    def GPIO3_str (self) -> str:
        return self._pin_level_str(self.GPIO3)

    @property
    def GPIO2_str (self) -> str:
        return self._pin_level_str(self.GPIO2)

    GPIO1_str = REG_GPIO.GPIO1_str
    GPIO0_str = REG_GPIO.GPIO0_str

@dataclass
class REG_INT_FLAGS (Reg):
    '''Interrupt flags.'''
    addr = 0x3020a8
    bits = 8

    @property
    def val_str (self) -> str:
        flags = ()
        if   self.val & 2**0: flags.append('SWAP'        )
        elif self.val & 2**1: flags.append('TOUCH'       )
        elif self.val & 2**2: flags.append('TAG'         )
        elif self.val & 2**3: flags.append('SOUND'       )
        elif self.val & 2**4: flags.append('PLAYBACK'    )
        elif self.val & 2**5: flags.append('CMDEMPTY'    )
        elif self.val & 2**6: flags.append('CMDFLAG'     )
        elif self.val & 2**7: flags.append('CONVCOMPLETE')
        return '|'.join(flags)

@dataclass
class REG_INT_EN (Reg):
    '''Global interrupt enable.'''
    addr = 0x3020ac
    bits = 1

@dataclass
class REG_INT_MASK (Reg):
    '''Individual interrupt enable.'''
    addr = 0x3020b0
    bits = 8

    val_str = REG_INT_FLAGS.val_str

@dataclass
class REG_PLAYBACK_START (Reg):
    '''Audio playback RAM start address.'''
    addr = 0x3020b4
    bits = 20

@dataclass
class REG_PLAYBACK_LENGTH (Reg):
    '''Audio playback sample length (bytes).'''
    addr = 0x3020b8
    bits = 20

@dataclass
class REG_PLAYBACK_READPTR (Reg):
    '''Audio playback current read pointer.'''
    addr = 0x3020bc
    bits = 20

@dataclass
class REG_PLAYBACK_FREQ (Reg):
    '''Audio playback sampling frequency (Hz).'''
    addr = 0x3020c0
    bits = 16

@dataclass
class REG_PLAYBACK_FORMAT (Reg):
    '''Audio playback format.'''
    addr = 0x3020c4
    bits = 2

@dataclass
class REG_PLAYBACK_LOOP (Reg):
    '''Audio playback loop enable.'''
    addr = 0x3020c8
    bits = 1

@dataclass
class REG_PLAYBACK_PLAY (Reg):
    '''Start audio playback.'''
    addr = 0x3020cc
    bits = 1

@dataclass
class REG_PWM_HZ (Reg):
    '''BACKLIGHT PWM output frequency (Hz).'''
    addr = 0x3020d0
    bits = 14

@dataclass
class REG_PWM_DUTY (Reg):
    '''BACKLIGHT PWM output duty cycle.'''
    addr = 0x3020d4
    bits = 8

@dataclass
class REG_MACRO_0 (Reg):
    '''Display list macro command 0.'''
    addr = 0x3020d8
    bits = 32

@dataclass
class REG_MACRO_1 (Reg):
    '''Display list macro command 1.'''
    addr = 0x3020dc
    bits = 32

@dataclass
class REG_CMD_READ (Reg):
    '''Command buffer read pointer.'''
    addr = 0x3020f8
    bits = 12

@dataclass
class REG_CMD_WRITE (Reg):
    '''Command buffer write pointer.'''
    addr = 0x3020fc
    bits = 12

@dataclass
class REG_CMD_DL (Reg):
    '''Command display list offset.'''
    addr = 0x302100
    bits = 13

@dataclass
class REG_TOUCH_MODE (Reg):
    '''Touch-screen sampling mode.'''
    addr = 0x302104
    bits = 2

@dataclass
class REG_TOUCH_ADC_MODE (Reg):
    '''Set Touch ADC mode / Set capacitive touch operation mode.'''
    addr = 0x302108
    bits = 1

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_EXTENDED'

@dataclass
class REG_TOUCH_CHARGE (Reg):
    '''Touch charge time.'''
    addr = 0x30210c
    bits = 16

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_EHOST_TOUCH_X'

@dataclass
class REG_TOUCH_SETTLE (Reg):
    '''Touch settle time / Touch host mode: touch x value updated by host.'''
    addr = 0x302110
    bits = 4

@dataclass
class REG_TOUCH_OVERSAMPLE (Reg):
    '''Touch oversample factor / Touch host mode:touch ID.'''
    addr = 0x302114
    bits = 4

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_EHOST_TOUCH_ID'

@dataclass
class REG_TOUCH_RZTHRESH (Reg):
    '''Touch resistance threshold / Touch host mode: touch y value updated by host.'''
    addr = 0x302118
    bits = 16

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_EHOST_TOUCH_Y'

@dataclass
class REG_TOUCH_RAW_XY (Reg):
    '''Touch-screen raw / Touch-screen screen data for touch 1.'''
    addr = 0x30211c
    bits = 32

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_TOUCH1_XY'

@dataclass
class REG_TOUCH_RZ (Reg):
    '''Touch-screen resistance / Touch-screen screen Y data for touch 4.'''
    addr = 0x302120
    bits = 16

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_TOUCH4_Y'

@dataclass
class REG_TOUCH_SCREEN_XY (Reg):
    '''Touch-screen screen / Touch-screen screen data for touch 0.'''
    addr = 0x302124
    bits = 32

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_TOUCH0_XY'

@dataclass
class REG_TAG_XY (Reg):
    '''Touch-screen screen used for tag 0 lookup.'''
    addr = 0x302128
    bits = 32

@dataclass
class REG_TOUCH_TAG (Reg):
    '''Touch-screen tag result 0.'''
    addr = 0x30212c
    bits = 8

@dataclass
class REG_TOUCH_TAG1_XY (Reg):
    '''Touch-screen screen used for tag 1 lookup.'''
    addr = 0x302130
    bits = 32

@dataclass
class REG_TOUCH_TAG1 (Reg):
    '''Touch-screen tag result 1.'''
    addr = 0x302134
    bits = 8

@dataclass
class REG_TOUCH_TAG2_XY (Reg):
    '''Touch-screen screen used for tag 2 lookup.'''
    addr = 0x302138
    bits = 32

@dataclass
class REG_TOUCH_TAG2 (Reg):
    '''Touch-screen tag result 2.'''
    addr = 0x30213c
    bits = 8

@dataclass
class REG_TOUCH_TAG3_XY (Reg):
    '''Touch-screen screen used for tag 3 lookup.'''
    addr = 0x302140
    bits = 32

@dataclass
class REG_TOUCH_TAG3 (Reg):
    '''Touch-screen tag result 3.'''
    addr = 0x302144
    bits = 8

@dataclass
class REG_TOUCH_TAG4_XY (Reg):
    '''Touch-screen screen used for tag 4 lookup.'''
    addr = 0x302148
    bits = 32

@dataclass
class REG_TOUCH_TAG4 (Reg):
    '''Touch-screen tag result 4.'''
    addr = 0x30214c
    bits = 8

@dataclass
class REG_TRANSFORM_A (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x302150
    bits = 32

@dataclass
class REG_TRANSFORM_B (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x302154
    bits = 32

@dataclass
class REG_TRANSFORM_C (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x302158
    bits = 32

@dataclass
class REG_TRANSFORM_D (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x30215c
    bits = 32

@dataclass
class REG_TRANSFORM_E (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x302160
    bits = 32

@dataclass
class REG_TRANSFORM_F (Reg):
    '''Touch-screen transform coefficient.'''
    addr = 0x302164
    bits = 32

@dataclass
class REG_TOUCH_CONFIG (Reg):
    '''Touch configuration.'''
    addr = 0x302168
    bits = 16

@dataclass
class REG_CTOUCH_TOUCH4_X (Reg):
    '''Touch-screen screen X data for touch 4.'''
    addr = 0x30216c
    bits = 16

@dataclass
class REG_EHOST_TOUCH_ACK (Reg):
    '''Touch host mode: acknowledgement.'''
    addr = 0x302170
    bits = 4

@dataclass
class REG_BIST_EN (Reg):
    '''BIST memory mapping enable.'''
    addr = 0x302174
    bits = 1

@dataclass
class REG_TRIM (Reg):
    '''Internal relaxation clock trimming.'''
    addr = 0x302180
    bits = 5

@dataclass
class REG_ANA_COMP (Reg):
    '''Analogue control register.'''
    addr = 0x302184
    bits = 8

@dataclass
class REG_SPI_WIDTH (Reg):
    addr = 0x302188
    bits = 3

@dataclass
class REG_TOUCH_DIRECT_XY (Reg):
    addr = 0x30218c
    bits = 32

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_TOUCH2_XY'

@dataclass
class REG_TOUCH_DIRECT_Z1Z2 (Reg):
    addr = 0x302190
    bits = 32

    @property
    def name_ (self) -> str:
        return super().name_ + '/REG_CTOUCH_TOUCH3_XY'

@dataclass
class REG_DATESTAMP (Reg):
    addr = 0x302564
    bits = 128

@dataclass
class REG_CMDB_SPACE (Reg):
    addr = 0x302574
    bits = 12

@dataclass
class REG_CMDB_WRITE (Reg):
    addr = 0x302578
    bits = 32

@dataclass
class REG_ADAPTIVE_FRAMERATE (Reg):
    addr = 0x30257c
    bits = 1

@dataclass
class REG_PLAYBACK_PAUSE (Reg):
    addr = 0x3025ec
    bits = 1

@dataclass
class REG_FLASH_STATUS (Reg):
    addr = 0x3025f0
    bits = 2

