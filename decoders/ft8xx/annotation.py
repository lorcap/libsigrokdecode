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
from typing import List

class Id:
    '''Annotation IDs.'''
    COMMAND          ,\
    COPROC           ,\
    DISPLIST         ,\
    HOSTCMD          ,\
    HOST_MEMORY_READ ,\
    HOST_MEMORY_WRITE,\
    PARAMETER        ,\
    RAMREG           ,\
    READ_ADDRESS     ,\
    READ_DATA        ,\
    TRANSACTION      ,\
    WARNING          ,\
    WRITE_ADDRESS    ,\
    WRITE_DATA       ,\
    WRITE_DUMMY      ,\
        = range(15)

@dataclass
class Annotation:
    '''Base class for all annotations.'''
    ss_: int    # start sample
    es_: int    # end sample

    @property
    def name_ (self) -> str:
        return self.__class__.__name__

    def _dec_str (self, val: int) -> str:
        '''Uniform representation of a decimal.'''
        return f'{val:_d}'

    def _hex_str (self, val: int) -> str:
        '''Uniform representation of a hexadecimal.'''
        return f'{val:_X}h'

    def _int_str (self, val: int) -> str:
        '''Uniform representation of an integer.'''
        return str(val) if val < 10 else f'{self._dec_str(val)} [{self._hex_str(val)}]'

    def _par_str (self, val: int, name: str='', desc: str='') -> str:
        '''Uniform representation of parameter name and value.'''
        int_str = self._int_str(val)
        if name and desc:
            return f'{name}={int_str}: {desc}'
        elif name and not desc:
            return f'{name}={int_str}'
        elif not name and desc:
            return f'{int_str}: {desc}'
        else:
            return int_str

    def _variant (self, ft80x: str, ft81x: str, bt81x: str, unit: str = '') -> str:
        '''Uniform representation of parameter variants.'''
        return f'{ft80x}/{ft81x}/{bt81x}{unit} (FT80x/FT81x/BT81x)'

#---------------------------------------------------------------------------#
from . import warning

@dataclass
class Command (Annotation):
    '''Annotation common to all command types.'''

    def __post_init__ (self) -> None:
        '''Dataclass' post-init processing.'''
        self._warning = None # Warning annotation, if any

    @property
    def strings_ (self) -> List[str]:
        '''Generate annotation strings from dataclass' fields.'''
        long = list()
        mid  = list()

        for par in self.parameters():
            name = par.rstrip('_')
            val = getattr(self, par)
            try:
                # parameter is represented by '<par>_str'
                val_str = getattr(self, name + '_str')
                if not val_str:
                    self._warning = warning.InvalidParameterValue(self.ss_, self.es_, val, name)
            except AttributeError:
                # '<par>_str' doesn't exist
                val_str = ''

            par_name = name if not par.endswith('_') else ''
            if val_str:
                long.append(self._par_str(val, par_name, val_str))
                mid .append(val_str)
            else:
                long.append(self._par_str(val, par_name))
                mid .append(self._par_str(val))

        if mid:
            long_str = '; '.join(long)
            mid_str  = '; '.join(mid )
            ret = [f'{self.name_}({long_str})',
                   f'{self.name_}({mid_str})']
            if len(mid) > 1:
                ret.append(f'{self.name_}({mid[-1]})')
        else:
            ret = [f'{self.name_}()']

        ret.append(self.name_)
        return ret

    @property
    def warning_ (self) -> warning.Warning:
        '''Warning annotation, if any.'''
        return self._warning

    def parameters (self) -> List[str]:
        '''Return a list of command's parameters, if any.'''
        return [f.name for f in dataclasses.fields(self)
                if not f.name.endswith('_')]

#---------------------------------------------------------------------------#

@dataclass
class Transaction (Annotation):
    '''Base class for transaction annotations.'''
    miso_size: int  # number of bytes read from MISO line
    mosi_size: int  # number of bytes written to MOSI line.

    @property
    def id_ (self) -> int:
        return Id.TRANSACTION

    @property
    def strings_ (self):
        name = self.name_
        size = max(self.miso_size, self.mosi_size)
        return [f'{name} transaction: out: {self.mosi_size}B, in: {self.miso_size}B',
                f'{name}: {size}B',
                name]
