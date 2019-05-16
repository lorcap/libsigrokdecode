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
from .. import datum

class Decoder (Base):
    '''Decoder of _Host Command_ transactions.'''

    def decode (self, mosi):
        '''Decode an _Host Command_ transaction.'''
        cmd  = datum.host_command.Command  (mosi[0])
        par  = datum.host_command.Parameter(mosi[1])
        par0 = datum.host_command.Parameter(mosi[2])
        return datum.host_command.Transaction(cmd, par, par0)

