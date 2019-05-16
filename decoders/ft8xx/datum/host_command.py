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

class Byte1 (Base):
    '''Data type for Host Command's 1st byte.'''

    def __init__ (self, start, end, val):
        h = getattr(self, f'handle_{self.val:#02x}')
        h()
        super().__init__(
                start  =start,
                end    =end,
                val    =val,
                ann_id =self._decoder.AnnId.COMMAND,
                ann_str=[f'Command: 0x{val:02X} - {self.name}',
                         f'Cmd: {self.name}',
                         f'{self.name}'])

    def handle_0x00 (self): self.name = 'ACTIVE'
    def handle_0x41 (self): self.name = 'STANDBY'
    def handle_0x42 (self): self.name = 'SLEEP'
    def handle_0x43 (self): self.name = 'PWRDOWN'
    def handle_0x44 (self): self.name = 'CLKEXT'
    def handle_0x48 (self): self.name = 'CLKINT'
    def handle_0x49 (self): self.name = 'PD_ROMS'
    def handle_0x50 (self): self.name = 'PWRDOWN'
    def handle_0x61 (self): self.name = 'CLK36M/CLKSEL'
    def handle_0x62 (self): self.name = 'CLK48M/CLKSEL'
    def handle_0x68 (self): self.name = 'CORERST/RST_PULSE'
    def handle_0x71 (self): self.name = 'PIN_PD_STATE'
    def handle_0x70 (self): self.name = 'PINDRIVE'

class Byte2 (Base):
    '''Data type for Host Command's 2nd byte.'''

    def __init__ (self, start, end, val, ann_str=[]):
        if not ann_str:
            ann_str = [f'0x{val:02X}', f'{val:X}']
        super().__init__(
                start  =start,
                end    =end,
                val    =val,
                ann_id =self._decoder.AnnId.PARAMETER,
                ann_str=[f'Parameter: {ann_str[0]}',
                         f'Par: {ann_str[1]}',
                         f'{ann_str[1]}'])

class Byte2_49h (Byte2): # PD_ROMS
    def __init__ (self, start, end, *,
                  ROM_MAIN    =False,
                  ROM_RCOSATAN=False,
                  ROM_SAMPLE  =False,
                  ROM_JABOOT  =False,
                  ROM_J1BOOT  =False):
        self.ROM_MAIN    = bool(ROM_MAIN    )
        self.ROM_RCOSATAN= bool(ROM_RCOSATAN)
        self.ROM_SAMPLE  = bool(ROM_SAMPLE  )
        self.ROM_JABOOT  = bool(ROM_JABOOT  )
        self.ROM_J1BOOT  = bool(ROM_J1BOOT  )

        down = []
        up   = []
        for rom in ('MAIN', 'RCOSATAN', 'SAMPLE', 'JABOOT', 'J1BOOT'):
            rom = 'ROM_' + rom
            if getattr(self, rom):
                down.append(rom)
            else:
                up.append(rom)
        if len(down) == 0:
            down = ['(none)']
        if len(up) == 0:
            up = ['(none)']

        ann_str = [f'''down: {', '.join(down)}; up: {', '.join(up)}''',
                   ','.join(down)])
        super().__init__(start, end, val, ann_str)

class Transaction (Base):
    '''Data type for Host Command's whole transaction.'''

    def __init__ (self, cmd, par, par0):
        self.cmd      = cmd           # command
        self.par      = par           # first parameter
        self.par0     = par0          # second parameter (always 0)

        p = f'0x{par.val:02X}' if cmd.par_nr else ''
        super().__init__(
                start  =cmd.start,
                end    =par0.end,
                name   ='HostCommand',
                ann_id =self._decoder.AnnId.TRANSACTION,
                ann_str=[f'Host Command: {cmd.name}({p})',
                         f'Cmd: {cmd.name}',
                         f'{cmd.name}'])

