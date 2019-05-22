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
from . import annotation, displist_cmd, host_cmd, memory, warning

class Int:
    '''Integer juggler.'''
    __slots__ = ('ss', 'es', 'val', 'size')

    def __init__ (self, ss: int, es: int, bytes, byteorder='little', *, signed=False):
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

class Fsm:
    '''Decoding finite-state machine implemented as coroutine.'''

    def __init__ (self):
        self.val        = bytearray()   # current value
        self.ss         = []            # sample start buffer
        self.es         = []            # sample end buffer
        self.miso_size  = 0             # number of bytes read
        self.mosi_size  = 0             # number of bytes written

        self._stack     = []            # stack for CALL/RETURN

        self._addr      = 0             # current address when accessing memory
        self._out       = []            # list of output data

    def __iter__ (self):
        '''Decoding core function.'''
        try:
            for i in range(3):
                yield from self.read_uint8('mosi')
        except GeneratorExit:
            self.out = warning.TruncatedCommand(self.ss[0], self.es[-1])
            raise

        if sum(self.val) != 0x000000:
            host_cmd_active = False
        else:
            # Uhm... host command ACTIVE or memory read at 0x000000xx?
            try:
                yield from self.read_uint8('mosi')
            except GeneratorExit:
                host_cmd_active = True

        transaction_type = self.val[0] & 0xc0

        if transaction_type == 0x00 and not host_cmd_active:
            # Host Memory Read
            self._addr = self.read_addr()
            self.out = memory.HostRead(*self._addr)

            if len(self.val) == 4:
                dummy = Int(self.ss[-1], self.es[-1], self.val[-1:])
            else:
                try:
                    dummy = yield from self.read_uint8('mosi')
                except GeneratorExit:
                    self.out = warning.MissingDummy(self.ss[0], self.es[-1])
                    raise
            self.out = memory.Dummy(*dummy)

            try:
                yield from self.decode_memory('miso')
            except GeneratorExit:
                self.out = memory.Transaction(
                        transaction_ss, self.es[-1],
                        self.miso_size, self.mosi_size)
                raise

        if transaction_type == 0x80:
            # Host Memory Write
            addr = self.read_addr()
            self.out = memory.HostWrite(*addr)

            try:
                self._addr = addr.val
                yield from self.decode_memory('mosi')
            except GeneratorExit:
                self.out = memory.WriteTransaction(
                        addr.ss, self.es[-1],
                        self.miso_size, self.mosi_size)
                raise

        if transaction_type == 0x40 or host_cmd_active:
            # Host Command
            byte1 = Int(self.ss[0], self.es[0], self.val[0:1])
            byte2 = Int(self.ss[1], self.es[1], self.val[1:2])
            byte3 = Int(self.ss[2], self.es[2], self.val[2:3])
            self.decode_host_command(byte1, byte2, byte3)

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
            try:
                u32 = yield from self.read_uint32(line)
                self.out = memory.Address(u32.ss, u32.es, self._addr, line)
                ram = memory.space(self._addr)
                if   ram == 'RAM_DL':
                    cmd = self.decode_dl_command(u32)
                elif ram == 'RAM_CMD':
                    cmd = self.decode_dl_command(u32)\
                        or (yield from self.decode_coproc_command(u32))
                else:
                    cmd = False
                    continue
                self.out = cmd
            except GeneratorExit:
                self.out = warning.TruncatedCommand(self.ss[0], self.es[-1])
                raise
        else:
            warn = warning.UnknownCommand(*u32)
            while True:
                try:
                    yield from self.read(line, 1)
                except GeneratorExit:
                    warn.es = self.es[-1]
                    self.out = warn
                    raise

    def read_addr (self) -> Int:
        '''Read memory address.'''
        addr = Int(self.ss[-3], self.es[-1], self.val[-3:], byteorder='big', signed=False)
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

    def decode_host_command (self, byte1: Int, byte2: Int, byte3: Int) -> None:
        '''Decode Host Commands.'''

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

    def decode_dl_command (self, u32: Int):
        '''Decode Display List commands.'''
        msb = u32[31:24]

        if   msb == 0xff:
            # co-processor command
            return None

        #-- Setting Graphics State -----------------------------------------#
        elif msb == 0x09:
            cmd = displist_cmd.ALPHA_FUNC(*u32, func=u32[10:8], ref=u32[7:0])
        elif msb == 0x2e:
            cmd = displist_cmd.BITMAP_EXT_FORMAT(*u32, format=u32[15:0])
        elif msb == 0x05:
            cmd = displist_cmd.BITMAP_HANDLE(*u32, handle=u32[4:0])
        elif msb == 0x07:
            cmd = displist_cmd.BITMAP_LAYOUT(*u32, format=u32[23:19], linestride=u32[18:9], height=u32[8:0])
        elif msb == 0x28:
            cmd = displist_cmd.BITMAP_LAYOUT_H(*u32, linestride=u32[3:2], height=u32[1:0])
        elif msb == 0x08:
            cmd = displist_cmd.BITMAP_SIZE(*u32, filter=u32[20], wrapx=u32[19], wrapy=u32[18], width=u32[17:9], height=u32[8:0])
        elif msb == 0x29:
            cmd = displist_cmd.BITMAP_SIZE_H(*u32, width=u32[3:2], height=u32[1:0])
        elif msb == 0x01:
            cmd = displist_cmd.BITMAP_SOURCE(*u32, addr=u32[23:0])
        elif msb == 0x2f:
            cmd = displist_cmd.BITMAP_SWIZZLE(*u32, r=u32[11:9], g=u32[8:6], b=u32[5:3], a=u32[2:0])
        elif msb == 0x15:
            cmd = displist_cmd.BITMAP_TRANSFORM_A(*u32, p=u32[17], v=u32[16:0])
        elif msb == 0x16:
            cmd = displist_cmd.BITMAP_TRANSFORM_B(*u32, p=u32[17], v=u32[16:0])
        elif msb == 0x17:
            cmd = displist_cmd.BITMAP_TRANSFORM_C(*u32, c=u32[23:0])
        elif msb == 0x18:
            cmd = displist_cmd.BITMAP_TRANSFORM_D(*u32, p=u32[17], v=u32[16:0])
        elif msb == 0x19:
            cmd = displist_cmd.BITMAP_TRANSFORM_E(*u32, p=u32[17], v=u32[16:0])
        elif msb == 0x1a:
            cmd = displist_cmd.BITMAP_TRANSFORM_F(*u32, f=u32[23:0])
        elif msb == 0x0b:
            cmd = displist_cmd.BLEND_FUNC(*u32, src=u32[5:4], dst=u32[2:0])
        elif msb == 0x06:
            cmd = displist_cmd.CELL(*u32, cell=u32[6:0])
        elif msb == 0x26:
            cmd = displist_cmd.CLEAR(*u32, c=u32[2], s=u32[1], t=u32[0])
        elif msb == 0x0f:
            cmd = displist_cmd.CLEAR_COLOR_A(*u32, alpha=u32[7:0])
        elif msb == 0x02:
            cmd = displist_cmd.CLEAR_COLOR_RGB(*u32, red=u32[23:16], blue=u32[15:8], green=u32[7:0])
        elif msb == 0x11:
            cmd = displist_cmd.CLEAR_STENCIL(*u32, s=u32[7:0])
        elif msb == 0x12:
            cmd = displist_cmd.CLEAR_TAG(*u32, t=u32[7:0])
        elif msb == 0x10:
            cmd = displist_cmd.COLOR_A(*u32, alpha=u32[4:0])
        elif msb == 0x20:
            cmd = displist_cmd.COLOR_MASK(*u32, r=u32[3], g=u32[2], b=u32[1], a=u32[0])
        elif msb == 0x04:
            cmd = displist_cmd.COLOR_RGB(*u32, u32[23:16], u32[15:8], u32[7:0])
        elif msb == 0x0e:
            cmd = displist_cmd.LINE_WIDTH(*u32, width=u32[11:0])
        elif msb == 0x2a:
            cmd = displist_cmd.PALETTE_SOURCE(*u32, addr=u32[21:0])
        elif msb == 0x0d:
            cmd = displist_cmd.POINT_SIZE(*u32, size=u32[12:0])
        elif msb == 0x23:
            cmd = displist_cmd.RESTORE_CONTEXT(*u32)
        elif msb == 0x22:
            cmd = displist_cmd.SAVE_CONTEXT(*u32)
        elif msb == 0x1c:
            cmd = displist_cmd.SCISSOR_SIZE(*u32, width=u32[23:12], height=u32[11:0])
        elif msb == 0x1b:
            cmd = displist_cmd.SCISSOR_XY(*u32, x=u32[21:11], y=u32[10:0])
        elif msb == 0x0a:
            cmd = displist_cmd.STENCIL_FUNC(*u32, func=u32[19:16], ref=u32[15:8], mask=u32[7:0])
        elif msb == 0x13:
            cmd = displist_cmd.STENCIL_MASK(*u32, mask=u32[7:0])
        elif msb == 0x0c:
            cmd = displist_cmd.STENCIL_OP(*u32, sfail=u32[5:3], spass=u32[2:0])
        elif msb == 0x03:
            cmd = displist_cmd.TAG(*u32, s=u32[7:0])
        elif msb == 0x14:
            cmd = displist_cmd.TAG_MASK(*u32, mask=u32[0])
        elif msb == 0x27:
            cmd = displist_cmd.VERTEX_FORMAT(*u32, frac=u32[2:0])
        elif msb == 0x2b:
            cmd = displist_cmd.VERTEX_TRANSLATE_X(*u32, x=u32[16:0])
        elif msb == 0x2c:
            cmd = displist_cmd.VERTEX_TRANSLATE_Y(*u32, y=u32[16:0])

        #-- Drawing Actions ------------------------------------------------#
        elif msb == 0x1f:
            cmd = displist_cmd.BEGIN(*u32, prim=u32[3:0])
        elif msb == 0x21:
            cmd = displist_cmd.END(*u32)
        elif msb == 0x01:
            cmd = displist_cmd.VERTEX2F(*u32, x=u32[29:15], y=u32[14:0])
        elif msb == 0x02:
            cmd = displist_cmd.VERTEX2II(*u32, x=u32[29:21], y=u32[20:12], handle=u32[11:7], cell=u32[6:0])

        #-- Execution Control ----------------------------------------------#
        elif msb == 0x2d:
            cmd = displist_cmd.NOP(*u32)
        elif msb == 0x1e:
            cmd = displist_cmd.JUMP(*u32, dest=u32[15:0])
        elif msb == 0x25:
            cmd = displist_cmd.MACRO(*u32, m=u32[1])
        elif msb == 0x1d:
            cmd = displist_cmd.CALL(*u32, dest=u32[15:0])
            if cmd.dest_is_valid():
                if len(self._stack) < 4:
                    self._stack.append(self._addr + 4)
                else:
                    self.out = warning.Message('stack full')
        elif msb == 0x24:
            if self._stack:
                cmd = displist_cmd.RETURN(*u32, addr=self._stack.pop())
            else:
                cmd = displist_cmd.RETURN(*u32)
                self.out = warning.Message('stack empty')
        elif msb == 0x00:
            cmd = displist_cmd.DISPLAY(*u32)

        #-------------------------------------------------------------------#
        else:
            cmd = warning.UnknownCommand(*u32)

        self._addr = memory.add(self._addr, 4)
        return cmd

    #########################################################################

#    def decode_coproc_command (self, u32: Int):
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
        ('command'          , 'Command'        ),
        ('host_command'     , 'HostCommand'    ),
        ('host_memory_read' , 'HostMemoryRead' ),
        ('host_memory_write', 'HostMemoryWrite'),
        ('parameter'        , 'Parameter'      ),
        ('read_address'     , 'ReadAddress'    ),
        ('read_command'     , 'ReadCommand'    ),
        ('read_data'        , 'ReadData'       ),
        ('transaction'      , 'Transaction'    ),
        ('warning'          , 'Warning'        ),
        ('write_address'    , 'WriteAddress'   ),
        ('write_data'       , 'WriteData'      ),
        ('write_dummy'      , 'WriteDummy'     ),
    )
    annotation_rows = (
        ('transaction', 'Transaction', (annotation.Id.TRANSACTION      , )),
        ('command'    , 'Command'    , (annotation.Id.DISPLAY_LIST     ,
                                        annotation.Id.HOST_COMMAND     ,
                                        annotation.Id.HOST_MEMORY_READ ,
                                        annotation.Id.HOST_MEMORY_WRITE, )),
        ('write'      , 'Write'      , (annotation.Id.COMMAND          ,
                                        annotation.Id.PARAMETER        ,
                                        annotation.Id.WRITE_ADDRESS    ,
                                        annotation.Id.WRITE_DATA       ,
                                        annotation.Id.WRITE_DUMMY      , )),
        ('read'       , 'Read'       , (annotation.Id.READ_ADDRESS     ,
                                        annotation.Id.READ_DATA        , )),
        ('warning'    , 'Warning'    , (annotation.Id.WARNING          , )),
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

