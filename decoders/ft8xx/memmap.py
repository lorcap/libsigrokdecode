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

@dataclass
class Space:
    '''Memory space.'''
    begin: int  # begin address (inclusive)
    end: int    # end address (inclusive)
    size: int = dataclasses.field(init=False)

    def __post_init__ (self):
        self.size = self.end - self.begin

    def contains (self, addr: int) -> bool:
        return self.begin <= addr <= self.end

RAM_G          = Space(begin=0x000000, end=  0x0fffff)
ROM_FONT       = Space(begin=0x1e0000, end=  0x2ffffb)
ROM_FONT_ADDR  = Space(begin=0x2ffffc, end=  0x2fffff)
RAM_DL         = Space(begin=0x300000, end=  0x301fff)
RAM_REG        = Space(begin=0x302000, end=  0x302fff)
RAM_CMD        = Space(begin=0x308000, end=  0x308fff)
RAM_ERR_REPORT = Space(begin=0x309800, end=  0x3098ff)
FLASH          = Space(begin=0x800000, end=0x107fffff)

def space (addr: int) -> str:
    if   RAM_G         .contains(addr): return 'RAM_G'
    elif ROM_FONT      .contains(addr): return 'ROM_FONT'
    elif ROM_FONT_ADDR .contains(addr): return 'ROM_FONT_ADDR'
    elif RAM_DL        .contains(addr): return 'RAM_DL'
    elif RAM_REG       .contains(addr): return 'RAM_REG'
    elif RAM_CMD       .contains(addr): return 'RAM_CMD'
    elif RAM_ERR_REPORT.contains(addr): return 'RAM_ERR_REPORT'
    elif FLASH         .contains(addr): return 'FLASH'
    else                              : return None

def add (addr: int, offset: int) -> int:
    '''Move forward in memory.'''
    if   space(addr) == 'RAM_CMD':
        return (addr + offset) & 0x308fff
    elif addr == 0x302578: # REG_CMDB_WRITE
        return addr
    else:
        return addr + offset

