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

'''
This decoder stacks on top of the 'spi' PD and decodes the FTDI FT80x and FT81x
advanced embedded video engine protocol, single channel mode.  Three data
transactions are understood:
- Host Memory Read
- Host Memory Write
- Host Command

Data read from or written to memory are further decoded when target address is
within the range:
- 0x302000-0x302ffff (registers)
- 0x308000-0x308ffff (command buffer)

Host command are also decoded to produce a more human friendly stream of data.

Details:
- http://www.ftdichip.com/Products/ICs/FT81X.html
- http://brtchip.com/wp-content/uploads/Support/Documentation/Datasheets/ICs/EVE/DS_FT81x.pdf
- http://brtchip.com/wp-content/uploads/Support/Documentation/Programming_Guides/ICs/EVE/FT81X_Series_Programmer_Guide.pdf
'''

from .pd import Decoder
