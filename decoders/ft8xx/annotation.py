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

import dataclasses
from dataclasses import dataclass
from typing import List

class Id:
    '''Annotation IDs.'''
    COMMAND          ,\
    DISPLAY_LIST     ,\
    HOST_COMMAND     ,\
    HOST_MEMORY_READ ,\
    HOST_MEMORY_WRITE,\
    PARAMETER        ,\
    READ_ADDRESS     ,\
    READ_DATA        ,\
    TRANSACTION      ,\
    WARNING          ,\
    WRITE_ADDRESS    ,\
    WRITE_DATA       ,\
    WRITE_DUMMY      ,\
        = range(13)

#---------------------------------------------------------------------------#

@dataclass
class Annotation:
    '''Base class for all annotations.'''
    ss_: int    # start sample
    es_: int    # end sample

    @property
    def name_ (self) -> str:
        return self.__class__.__name__

    def _par_str (self, val: int, name: str=None, desc: str=None) -> str:
        '''Standard representation of parameter name and value.'''
        int_str = str(val) if val < 10 else f'{val} [{val:_X}h]'
        if name and desc:
            return f'{name}={int_str}: {desc}'
        elif name and not desc:
            return f'{name}={int_str}'
        elif not name and desc:
            return f'{int_str}: {desc}'
        else:
            return int_str


#---------------------------------------------------------------------------#

@dataclass
class Warning (Annotation):
    '''Annotation common to all warnings.'''

    @property
    def id_ (self) -> int:
        return Id.WARNING

#---------------------------------------------------------------------------#

@dataclass
class Command (Annotation):
    '''Annotation common to all command types.'''
    val_: int   # raw value

    def __post_init__ (self) -> None:
        '''Dataclass' post-init processing.'''
        self._warning = None # Warning annotation, if any

    @property
    def strings_ (self) -> List[str]:
        '''Generate annotation strings from dataclass' fields.'''
        long = list()
        mid  = list()

        for field_name in self._field_names():
            val = getattr(self, field_name)
            try:
                # field is represented by '<field_name>_str'
                val_str = getattr(self, field_name + '_str')
                long.append(self._par_str(val, field_name, val_str))
                mid .append(val_str)
            except AttributeError:
                # '<field_name>_str' doesn't exist
                long.append(self._par_str(val, field_name))
                mid .append(self._par_str(val))

        return ['{0}({1})'.format(self.name_, '; '.join(long)),
                '{0}({1})'.format(self.name_, '; '.join(mid )),
                self.name_]

    @property
    def warning_ (self) -> Warning:
        '''Warning annotation, if any.'''
        return self._warning

    def has_parameters (self) -> bool:
        '''Check wheather command has e or more parameters.'''
        return bool(self._field_names())

    #--- private ---#

    def _field_names (self) -> List[str]:
        return [f.name for f in dataclasses.fields(self)
                if not f.name.endswith('_')]

    def _warn (self, cls: Warning, *args) -> None:
        '''Make a warning annotation.'''
        assert(issubclass(cls, Warning))
        self._warning = cls(self.ss_, self.es_, args)

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

