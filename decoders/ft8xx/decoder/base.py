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

def is_host_command (mosi):
    '''Check whether MOSI contains a _Host Command_ transaction.'''
    return len(mosi) == 3                 \
       and ( (mosi[0].val & 0xc0) == 0x40 \
            or (mosi[0].val == 0 and      \
                mosi[1].val == 0 and      \
                mosi[2].val == 0        ) )

def is_host_memory_read (mosi):
    '''Check whether MOSI contains a _Host Memory Read_ transaction.'''
    return len(mosi) >= 3               \
       and (mosi[0].val & 0xc0) == 0x00

def is_host_memory_write (mosi):
    '''Check whether MOSI contains a _Host Memory Write_ transaction.'''
    return len(mosi) >= 3               \
       and (mosi[0].val & 0xc0) == 0x80

class Base:
    '''Base class for all transaction decoders.'''

    _decoder = None
    '''Shared protocol decoder object.'''

    @classmethod
    def set_decoder (class_, decoder):
        '''Set protocol decoder object.'''
        class_._decoder = decoder

