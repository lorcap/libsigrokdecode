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

from dataclasses import dataclass
from typing import List
from . import annotation


@dataclass
class Byte1 (annotation.Annotation):
    '''Command byte #1 of a Host Command transaction.'''
    val: int    # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.COMMAND

    @property
    def strings_ (self) -> List[str]:
        cmd = f'{self.val:02X}h'
        return [f'Command: {cmd}',
                f'Cmd: {cmd}',
                cmd]

@dataclass
class Byte2 (annotation.Annotation):
    '''Parameter byte #2 of a Host Command transaction.'''
    val: int    # raw value

    @property
    def id_ (self) -> int:
        return annotation.Id.PARAMETER

    @property
    def strings_ (self) -> List[str]:
        par = f'{self.val:02X}h'
        return [f'Parameter: {par}',
                f'Par: {par}',
                par]

Byte3 = Byte2

#---------------------------------------------------------------------------#

@dataclass
class Command (annotation.Command):
    '''Base class for host commands.'''

    @property
    def id_ (self) -> int:
        return annotation.Id.HOST_COMMAND

@dataclass
class ACTIVE (Command):
    '''Switch from Standby/Sleep modes to active mode.'''
    pass

@dataclass
class CLKEXT (Command):
    '''Select PLL input from external crystal oscillator.'''
    pass

@dataclass
class CLKINT (Command):
    '''Select PLL input from internal relaxation oscillator.'''
    pass

@dataclass
class CLKSEL (Command):
    '''Select the system clock frequency.'''
    clock: int  # clock frequency
    pll:   int  # PLL range

    @property
    def clock_str (self) -> str:
        if self.clock == 0 and self.pll == 0:
            ft80x_mhz = '36' if self.val_ == 0x61 else '48'
            return ft80x_mhz + '/60/60MHz (FT80x/FT81x/BT81x)'
        elif (self.clock in (2, 3   ) and self.pll == 0)\
          or (self.clock in (4, 5, 6) and self.pll == 1):
            return f'{self.clock}x osc frequency'
        else:
            self._warn(warning.Warning, "invalid combination of 'clock' and 'pll'")
            return 'invalid'

@dataclass
class PIN_PD_STATE (Command):
    '''Pin state when powered down.'''
    pin:     int    # pin/pin group
    setting: int    # pin setting

    @property
    def pin_str (self) -> str:
        if   self.pin == 0x00: return 'GPIO0'
        elif self.pin == 0x01: return 'GPIO1'
        elif self.pin == 0x02: return 'GPIO2'
        elif self.pin == 0x03: return 'GPIO3'
        elif self.pin == 0x08: return 'DISP'
        elif self.pin == 0x09: return 'DE'
        elif self.pin == 0x0A: return 'V/HSYNC'
        elif self.pin == 0x0B: return 'PCLK'
        elif self.pin == 0x0C: return 'BACKLIGHT'
        elif self.pin == 0x0D: return 'RGB'
        elif self.pin == 0x0E: return 'AUDIO_L'
        elif self.pin == 0x0F: return 'INT_N'
        elif self.pin == 0x10: return 'CTP_RST_N'
        elif self.pin == 0x11: return 'CTP_SCL'
        elif self.pin == 0x12: return 'CTP_SDA'
        elif self.pin == 0x13: return 'SPI'
        elif self.pin == 0x14: return 'SPIM_SCLK'
        elif self.pin == 0x15: return 'SPIM_SS_N'
        elif self.pin == 0x16: return 'SPIM_MISO'
        elif self.pin == 0x17: return 'SPIM_MOSI'
        elif self.pin == 0x18: return 'SPIM_IO2'
        elif self.pin == 0x19: return 'SPIM_IO3'
        else                 :
            self._warn(warning.InvalidParameterValue, self.pin, 'pin')
            return '(Reserved)'

    @property
    def setting_str (self):
        if   self.setting == 0x0: return 'Float'
        elif self.setting == 0x1: return 'Pull-Down'
        elif self.setting == 0x2: return 'Pull-Up'
        elif self.setting == 0x3: return '(Reserved)'

@dataclass
class PINDRIVE (Command):
    '''Set the drive strength for various pins.'''
    pin:      int = 0   # pin/pin group (see PIN_PD_STATE)
    strength: int = 0   # drive strength

    pin_str = PIN_PD_STATE.pin_str

    @property
    def strength_str (self):
        if self.pin in (0x0d, 0x0b, 0x08, 0x0a, 0x09, 0x0c):
            if   self.strength == 0x0: return '1.2/5mA (BT81x/FT81x)'
            elif self.strength == 0x1: return '2.4/10mA (BT81x/FT81x)'
            elif self.strength == 0x2: return '3.6/15mA (BT81x/FT81x)'
            elif self.strength == 0x3: return '4.8/20mA (BT81x/FT81x)'
        else:
            if   self.strength == 0x0: return '5mA'
            elif self.strength == 0x1: return '10mA'
            elif self.strength == 0x2: return '15mA'
            elif self.strength == 0x3: return '20mA'

@dataclass
class PD_ROMS (Command):
    '''Select power down individual ROMs.'''
    MAIN    : int   # power down main ROM
    RCOSATAN: int   # power down cos() and atan() ROMs
    SAMPLE  : int   # power down sample ROM
    JABOOT  : int   # power down JABOOT ROM
    J1BOOT  : int   # power down J1BOOT ROM

    @property
    def MAIN_str (self) -> str:
        return 'down' if self.MAIN else 'up'

    @property
    def RCOSATAN_str (self) -> str:
        return 'down' if self.RCOSATAN else 'up'

    @property
    def SAMPLE_str (self) -> str:
        return 'down' if self.SAMPLE else 'up'

    @property
    def JABOOT_str (self) -> str:
        return 'down' if self.JABOOT else 'up'

    @property
    def J1BOOT_str (self) -> str:
        return 'down' if self.J1BOOT else 'up'

@dataclass
class PWRDOWN (Command):
    '''Switch off 1.2V core voltage to the digital core circuits.'''
    pass

@dataclass
class RST_PULSE (Command):
    '''Send reset pulse to FT81x core.'''
    pass

@dataclass
class SLEEP (Command):
    '''Put FT81x core to sleep mode.'''
    pass

@dataclass
class STANDBY (Command):
    '''Put BT815/6 core to standby mode.'''
    pass

#---------------------------------------------------------------------------#

@dataclass
class Transaction (annotation.Transaction):
    '''Host Command transaction.'''
    pass

    @property
    def name_ (self) -> str:
        return 'Host Command'

