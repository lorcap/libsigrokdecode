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
from .host_memory import *

class Transaction (Base):
    '''Data type for Host Memory Write's whole transaction.'''

    def __init__ (self, addr, dataset):
        self.addr    = addr    # address
        self.dataset = dataset # plain data
        self.warnings = WarningList() # list of warnings

        super().__init__(
                start  =addr.start,
                end    =dataset.end,
                name   ='HostMemoryWrite',
                ann_id =self._decoder.AnnId.TRANSACTION,
                ann_str=[f'Host Memory Write: 0x{addr.val:06X} ({dataset.val} bytes)',
                         f'Write: {addr.val:X}',
                         f'W:{addr.val:X}'])

