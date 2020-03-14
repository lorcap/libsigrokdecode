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
from typing import List, Tuple
from . import memmap

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

    def __bool__ (self):
        return self.ss_ < self.es_

    @property
    def name_ (self) -> str:
        return self.__class__.__name__

    @staticmethod
    def _addr_str (val: int) -> str:
        '''Uniform representation of a memory address.'''
        s = memmap.space(val)
        return s if s else '(unknown space)'

    @staticmethod
    def _dec_str (val: int) -> str:
        '''Uniform representation of a decimal.'''
        return f'{val:_d}'

    @staticmethod
    def _fixed_point_str (val: int, int_len: int, dec_len: int) -> str:
        '''Return a string representation of a fixed-point value, "int.dec"-bit long.'''
        tot_len = int_len + dec_len
        assert(tot_len <= 32)
        v = val / 2**dec_len
        i = (val >> dec_len) & (2**int_len - 1)
        d = (val >> 0      ) & (2**dec_len - 1)
        return f'{v} ({i}.{d})'

    @staticmethod
    def _format_str (val: int) -> str:
        if   val ==     0: return 'ARGB1555'
        elif val ==     1: return 'L1'
        elif val ==     2: return 'L4'
        elif val ==     3: return 'L8'
        elif val ==     4: return 'RGB322'
        elif val ==     5: return 'ARGB2'
        elif val ==     6: return 'ARGB4'
        elif val ==     7: return 'RGB565'
        elif val ==     9: return 'TEXT8X8'
        elif val ==    10: return 'TEXTVGA'
        elif val ==    11: return 'BARGRAPH'
        elif val ==    14: return 'PALETTED565'
        elif val ==    15: return 'PALETTED4444'
        elif val ==    16: return 'PALETTED8'
        elif val ==    17: return 'L2'
        elif val ==    31: return 'GLFORMAT'
        elif val == 37808: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 4,  4)
        elif val == 37809: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 5,  4)
        elif val == 37810: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 5,  5)
        elif val == 37811: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 6,  5)
        elif val == 37812: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 6,  6)
        elif val == 37813: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  5)
        elif val == 37814: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  6)
        elif val == 37815: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format( 8,  8)
        elif val == 37816: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  5)
        elif val == 37817: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  6)
        elif val == 37818: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10,  8)
        elif val == 37819: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(10, 10)
        elif val == 37820: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(12, 10)
        elif val == 37821: return 'COMPRESSED_RGBA_ASTC_{0}x{1}_KHR'.format(12, 12)
        else                     : return ''

    @staticmethod
    def _freq_str (val: int) -> str:
        if   val >= 10**6: return str(val/10**6) + 'MHz'
        elif val >= 10**3: return str(val/10**3) + 'kHz'
        else             : return str(val      ) + 'Hz'

    @staticmethod
    def _hex_str (val: int) -> str:
        '''Uniform representation of a hexadecimal.'''
        return f'{val:_X}h'

    @staticmethod
    def _int_str (val: int) -> str:
        '''Uniform representation of an integer.'''
        return str(val) if val < 10 else f'{Annotation._dec_str(val)} [{Annotation._hex_str(val)}]'

    @staticmethod
    def _par_str (val: int, name: str='', desc: str='') -> str:
        '''Uniform representation of parameter name and value.'''
        int_str = Annotation._int_str(val)
        if name and desc:
            return f'{name}={int_str}: {desc}'
        elif name and not desc:
            return f'{name}={int_str}'
        elif not name and desc:
            return f'{int_str}: {desc}'
        else:
            return int_str

    @staticmethod
    def _reg_rotate_str (val: int) -> str:
        '''Uniform representation of REG_ROTATE's value.'''
        if   val == 0b000: return 'landscape'
        elif val == 0b001: return 'inverted landscape'
        elif val == 0b010: return 'potrait'
        elif val == 0b011: return 'inverted potrait'
        elif val == 0b100: return 'mirrored landscape'
        elif val == 0b101: return 'mirrored inverted landscape'
        elif val == 0b110: return 'mirrored potrait'
        elif val == 0b111: return 'mirrored inverted potrait'
        else             : return ''

    @staticmethod
    def _size_str (val: int) -> str:
        '''Uniform representation of size parameters.'''
        if   val >= 1024**2: return '{:.1f}'.format(val/1024**2) + 'MiB'
        elif val >= 1024**1: return '{:.1f}'.format(val/1024**1) + 'KiB'
        else               : return '{}'    .format(val        ) + 'B'

    @staticmethod
    def _variant (ft80x: str, ft81x: str, bt81x: str, unit: str = '') -> str:
        '''Uniform representation of parameter variants.'''
        return f'{ft80x}/{ft81x}/{bt81x}{unit} (FT80x/FT81x/BT81x)'

#---------------------------------------------------------------------------#

@dataclass
class Command (Annotation):
    '''Annotation common to all command types.'''

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
                    print(f'no string for {name} in {self}')
                    assert val_str
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

    def parameters (self) -> List[str]:
        '''Return a list of command's parameters, if any.'''
        return [f.name for f in dataclasses.fields(self)
                if not f.name.endswith('_')]

    @staticmethod
    def _matrix_abde_str (v: int, p: int = -1) -> str:
        '''Return a string representation of a matrix transformation coefficients A/B/D/E.'''
        if p not in (0, 1):
            p = (v >> 17) & 0x1
        v = v & 0xffff
        return Command._fixed_point_str(v, 8,  8) if p == 0 else\
               Command._fixed_point_str(v, 1, 15)

    @staticmethod
    def _matrix_cf_str (v: int) -> str:
        '''Return a string representation of a matrix transformation coefficient C/F.'''
        return Command._fixed_point_str(v, 15, 8)


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
        size = self._size_str(max(self.miso_size, self.mosi_size))
        mosi = self._size_str(self.mosi_size)
        miso = self._size_str(self.miso_size)
        return [f'{name} transaction: out: {mosi}, in: {miso}',
                f'{name}: {size}',
                name]

