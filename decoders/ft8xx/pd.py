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

import sigrokdecode as srd
from . import annotation
from . import host_cmd
from . import warning

class Int:
    '''Integer juggler.'''
    __slots__ = ('ss', 'es', 'val', 'size')

    def __init__ (self, ss, es, bytes, byteorder='little', *, signed=False):
        self.ss   = ss    # start sample
        self.es   = es    # end sample
        self.val  = int.from_bytes(bytes, signed=signed, byteorder=byteorder)
        self.size = len(bytes)

    def __iter__ (self):
        '''Allow starred expression.'''
        yield self.ss
        yield self.es
        yield self.val

    def __getitem__ (self, key):
        '''Extract bits ([msb:lsb], [bit]).'''
        if isinstance(key, slice)\
        and key.step == None\
        and 31 >= key.start >= key.stop >= 0:
            start = key.start
            stop  = key.stop
        elif isinstance(key, int) \
        and 31 >= key >= 0:
            start = stop = key
        else:
            raise IndexError

        return (self.val >> stop) & (2**(start - stop + 1) - 1)

    def __iadd__ (self, other):
        '''This is meant for memory addresses only.'''
        ram = memory.ram_str(self.val)
        if   ram == 'RAM_CMD':
            self.val = (self.val + other) & 0x308fff
        elif ram == 0x302578: # REG_CMDB_WRITE
            pass
        else:
            self.val += other

class Fsm:
    '''Decoding finite-state machine implemented as coroutine.'''

    def __init__ (self):
        self.val        = bytearray()   # current value
        self.ss         = []            # sample start buffer
        self.es         = []            # sample end buffer
        self.miso_size  = 0             # number of bytes read
        self.mosi_size  = 0             # number of bytes written

        self._addr      = None          # current address when accessing memory
        self._out       = []            # list of output data

    def __iter__ (self):
        '''Decoding core function.'''
        try:
            for i in range(3):
                yield from self.read_uint8('mosi')
        except GeneratorExit:
            self.out = warning.TruncatedCommand(self.ss[0], self.es[-1])
            raise

        host_cmd_active = False
        if sum(self.val) == 0x000000:
            # Uhm... host command ACTIVE or memory read at 0x000000xx?
            try:
                yield from self.read_uint8('mosi')
            except GeneratorExit:
                host_cmd_active = True

        transaction_type = self.val[0] & 0xc0

#        iftransaction_type == 0x00 and not host_cmd_active:
#            # Host Memory Read
#            self._addr = self._start_addr = addr = yield from self.read_addr(u8)
#            self.out = memory.Address(*addr, ann.Id.WRITE_ADDRESS)
#            dummy = yield from self.read_uint8('mosi')
#            self.out = memory.Dummy(*dummy)
#            try:
#                yield from self.decode_memory('miso')
#            except GeneratorExit:
#                self.out = memory.Transaction(
#                        addr.ss, self.es[-1],
#                        self.miso_size, self.mosi_size)
#                raise

#        if transaction_type == 0x80:
#            # Host Memory Write
#            self._addr = addr = yield from self.read_addr(u8)
#            self.out = memory.Address(*addr, ann.Id.WRITE_ADDRESS)
#            try:
#                yield from self.decode_memory('mosi')
#            except GeneratorExit:
#                self.out = memory.Transaction(
#                        addr.ss, self.es[-1],
#                        self.miso_size, self.mosi_size)
#                raise

        if transaction_type == 0x40 or host_cmd_active:
            # Host Command
            self.decode_host_command()
            self.out = host_cmd.Transaction(
                    self.ss[0], self.es[-1],
                    self.miso_size, self.mosi_size)

            if not host_cmd_active:
                u8 = yield from self.read_uint8('mosi')
                warn = warning.TrailingData(u8.ss, u8.es, 1)
                while True:
                    try:
                        u8 = yield from self.read_uint8('mosi')
                    except GeneratorExit:
                        self.out = warn
                        raise
                    warn.end = u8.es
                    warn.count = warn.count + 1

    def decode_memory (self, line):
        '''Decode Host Memory Read/Write commands.'''
        cmd = True
        while cmd:
            yield from self.read(line, 1)
            try:
                u32 = yield from self.read_uint32(line, size=3)
                ram_str = memory.ram_str(self._addr.val)
                if   ram_str == 'RAM_DL':
                    self.out = cmd = self.decode_dl_command(u32)
                elif ram_str == 'RAM_CMD':
                    self.out = cmd = self.decode_dl_command(u32)\
                        or (yield from self.decode_coproc_command(u32))
            except GeneratorExit:
                self.out = warning.TruncatedCommand(self._addr.ss, self.es[-1])
                raise
        else:
            warn = warning.UnknownCommand(*u32)
            while True:
                try:
                    u8 = yield from self.read_uint8(line)
                except GeneratorExit:
                    self.out = warn
                    raise
                warn = warn._replace(end=u8.es)

    def read_addr (self, prev_int=None) -> Int:
        '''Read memory address.'''
        addr = yield from self.read('mosi', count=3 - prev_int.size, byteorder='big', size=3)
        addr.val = addr[21:0]
        return addr

    def read_uint8 (self, line) -> Int:
        '''Read 8-bit unsigned integer.'''
        return (yield from self.read(line, 1))

    def read_uint32 (self, line, *, count=4) -> Int:
        '''Read 32-bit unsigned integer.'''
        return (yield from self.read(line, count, size=4))

    def read (self, line, count, byteorder='little', signed=False, size=0) -> Int:
        '''Read up-to 'count' bytes from MISO/MOSI and make a 'size' byte integer.'''
        assert 0 < count <= 4
        assert line in ('miso', 'mosi')

        for i in range(count):
            mosi, miso = yield self.out
            if line == 'mosi':
                byte = mosi
                self.mosi_size += 1
            else:
                byte = miso
                self.miso_size += 1
            self.val.append(byte.val)
            self.ss .append(byte.ss )
            self.es .append(byte.es )

        # truncate FIFO to the last 4 bytes
        self.val = self.val[-4:]
        self.ss  = self.ss [-4:]
        self.es  = self.es [-4:]

        if size:
            assert count <= size <= 4
        else:
            size = count
        return Int(self.ss[-size], self.es[-1], self.val[-size:],
                   byteorder=byteorder, signed=signed)

    @property
    def out (self):
        _out = self._out
        self._out = []
        return _out

    @out.setter
    def out (self, out):
        if (out == None):
            return
        self._out.append(out)

    #########################################################################

    def decode_host_command (self) -> None:
        '''Decode Host Commands.'''
        byte1 = Int(self.ss[0], self.es[0], self.val[0:1])
        byte2 = Int(self.ss[1], self.es[1], self.val[1:2])
        byte3 = Int(self.ss[2], self.es[2], self.val[2:3])

        #-- Power Modes ----------------------------------------------------#
        if   byte1.val == 0x00:
            cmd = host_cmd.ACTIVE(*byte1)

        elif byte1.val == 0x41:
            cmd = host_cmd.STANDBY(*byte1)

        elif byte1.val == 0x42:
            cmd = host_cmd.SLEEP(*byte1)

        elif byte1.val == 0x43 or byte1.val == 0x50:
            cmd = host_cmd.PWRDOWN(*byte1)

        elif byte1.val == 0x49:
            cmd = host_cmd.PD_ROMS(*byte1, MAIN    =byte2[7],
                                           RCOSATAN=byte2[6],
                                           SAMPLE  =byte2[5],
                                           JABOOT  =byte2[4],
                                           J1BOOT  =byte2[3])

        #-- Clock and Reset ------------------------------------------------#
        elif byte1.val == 0x44:
            cmd = host_cmd.CLKEXT(*byte1)

        elif byte1.val == 0x48:
            cmd = host_cmd.CLKINT(*byte1)

        elif byte1.val == 0x61 or byte1.val == 0x62:
            cmd = host_cmd.CLKSEL(*byte1, pll=byte2[7:6], clock=byte2[5:0])

        elif byte1.val == 0x68:
            cmd = host_cmd.RST_PULSE(*byte1)

        #-- Configuration --------------------------------------------------#
        elif byte1.val == 0x70:
            cmd = host_cmd.PINDRIVE(*byte1, pin=byte2[7:2], strength=byte2[1:0])

        elif byte1.val == 0x71:
            cmd = host_cmd.PIN_PD_STATE(*byte1, pin=byte2[7:2], setting=byte2[1:0])

        #-------------------------------------------------------------------#
        else:
            cmd = None
            self.out = warning.UnknownCommand(*byte1)

        self.out = host_cmd.Byte1(*byte1)
        self.out = host_cmd.Byte2(*byte2)
        self.out = host_cmd.Byte3(*byte3)

        if not cmd or not cmd.has_parameters():
            if byte2.val != 0:
                self.out = warning.Warning(*byte2, 'Byte2 is not 00h')

        if byte3.val != 0:
            self.out = warning.Warning(*byte3, 'Byte3 is not 00h')

        if cmd:
            cmd.es_ = byte3.es
            self.out = cmd
            if cmd.warning_:
                self.out = cmd.warning_

    #########################################################################

#    def decode_dl_command (self, u32):
#        '''Decode Display List commands.'''
#        msb = u32[31:24]
#
#        if   msb == 0xff:
#            # co-processor command
#            return None
#
#        #-- Setting Graphics State -----------------------------------------#
#        elif msb == 0x09:
#            cmd = dl.ALPHA_FUNC(*u32, u32[10:8], u32[7:0])
#
#        #-- Drawing Actions ------------------------------------------------#
#        elif msb == 0x1f:
#            cmd = dl.BEGIN(*u32, u32[3:0])
#
#        #-- Execution Control ----------------------------------------------#
#
#        #-------------------------------------------------------------------#
#        else:
#            return None
#
#        self._addr += 4
#        return cmd

    #########################################################################

#    def decode_coproc_command (self, u32):
#        '''Decode Co-Processor Engine commands.'''
#        if u32[31:24] != 0xff:
#            return None
#
#        #-- Display List Management ----------------------------------------#
#        elif u32.val == 0xffffff00:
#            cmd = coproc.CMD_DLSTART(*u32)
#
#        elif u32.val == 0xffffff01:
#            cmd = coproc.CMD_SWAP(*u32)
#
#        #-- Graphics Objects Drawing ---------------------------------------#
#        #-- Memory Operations ----------------------------------------------#
#        #-- Image Data Loading ---------------------------------------------#
#        #-- Bitmap Transform Matrix Setting --------------------------------#
#        #-- Other Commands -------------------------------------------------#
#        #-------------------------------------------------------------------#
#        else:
#            return None
#
#        self._addr += 4
#        return cmd

class Decoder (srd.Decoder):
    api_version = 3
    id = 'ft8xx'
    name = 'FT8xx'
    longname = 'SPI of FTDI FT80x and FT81x'
    desc = 'SPI protocol of FTDI FT80x and FT81x advanced embedded video engines'
    license = 'gplv2+'
    inputs = ['spi']
    outputs = ['ft8xx']
    annotations = (
        ('command'      , 'Command'     ),
        ('dummy'        , 'Dummy'       ),
        ('host_command' , 'HostCommand' ),
        ('parameter'    , 'Parameter'   ),
        ('read_address' , 'ReadAddress' ),
        ('read_command' , 'ReadCommand' ),
        ('read_data'    , 'ReadData'    ),
        ('transaction'  , 'Transaction' ),
        ('warning'      , 'Warning'     ),
        ('write_address', 'WriteAddress'),
        ('write_data'   , 'WriteData'   ),
    )
    annotation_rows = (
        ('transaction', 'Transaction', (annotation.Id.TRANSACTION  , )),
        ('command'    , 'Command'    , (annotation.Id.HOST_COMMAND , )),
        ('write'      , 'Write'      , (annotation.Id.COMMAND      ,
                                        annotation.Id.PARAMETER    ,
                                        annotation.Id.WRITE_ADDRESS,
                                        annotation.Id.READ_ADDRESS ,
                                        annotation.Id.DUMMY        ,
                                        annotation.Id.WRITE_DATA   , )),
        ('read'       , 'Read'       , (annotation.Id.READ_DATA    , )),
        ('warning'    , 'Warning'    , (annotation.Id.WARNING      , )),
    )

    def start (self):
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)

    def decode (self, start_sample, stop_sample, data):
        ptype, mosi, miso = data
        if ptype != 'TRANSFER' or len(mosi) == 0:
            return

        fsm = Fsm()
        gen = iter(fsm)
        next(gen)
        for byte in zip(mosi, miso):
            for ann in gen.send(byte):
                self.put(ann.ss_, ann.es_, self.out_ann, [ann.id_, ann.strings_])
        gen.close()
        for ann in fsm.out:
            self.put(ann.ss_, ann.es_, self.out_ann, [ann.id_, ann.strings_])

