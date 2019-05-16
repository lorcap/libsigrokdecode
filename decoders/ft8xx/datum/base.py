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

def bit (val, msb, lsb=None):
    '''Extract parameter value from MSB to LSB bits.'''
    if lsb == None:
        lsb = msb
    return (val >> lsb) & (2**(msb + 1 - lsb) - 1)

class Base:
    '''Base class for all data types.'''

    _decoder = None
    '''Class' protocol decoder object.'''

    def __init__ (self, start, end, val=None, name='',
                  ann_id=None, ann_str=[]):
        '''Initialize a new data type.'''
        self.start   = start    # start sample
        self.end     = end      # end sample
        self.val     = val      # raw value
        self.name    = name     # label as per datasheet
        self.ann_id  = ann_id   # annotation id
        self.ann_str = ann_str  # list of annotation strings

    @classmethod
    def set_decoder (class_, decoder):
        '''Set protocol decoder object.'''
        class_._decoder = decoder

    def __repr__ (self):
        return self.__dict__.__repr__()

    def put_ann (self):
        '''Put an annotation back to the backend.'''
        assert self.ann_id != None, f'bad ann_id: {self.ann_id}'
        self._decoder.put(self.start, self.end,
                          self._decoder.out_ann,
                          [self.ann_id, self.ann_str])

class Warning (Base):
    '''Data type for warnings.'''

    def __init__ (self, start, end, msg):
        super().__init__(
                start  =start,
                end    =end,
                val    =msg,
                ann_id =self._decoder.AnnId.WARNING,
                ann_str=msg)

