#commandout = adcnum
#commandout |= 0x18  # start bit + single-ended bit
#commandout <<= 3  # we only need to send 5 bits here
#for i in range(5):
#    if (commandout & 0x80):
#        bin(0x18)[2:]



class Device(object):
    def __init__(self, address, bus):
        self._bus = bus
        self._address = address

    def writeRaw8(self, value):
        value = value & 0xff
        self._bus.write_byte(self._address, value)

    def readRaw8(self):
        result = self._bus.read_byte(self._address) & 0xff
        return result

    def write8(self, register, value):
        value = value & 0xff
        self._bus.write_byte_data(self._address, register, value)

    def readU8(self, register):
        result = self._bus.read_byte_data(self._address, register) & 0xFF
        return result

    def readS8(self, register):
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def write16(self, register, value):
        value = value & 0xffff
        self._bus.write_word_data(self._address, register, value)

    def readU16(self, register, little_endian = True):
        result = self._bus.read_word_data(self._address,register) & 0xFFFF
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian = True):
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def writeList(self, register, data):
        self._bus.write_i2c_block_data(self._address, register, data)

    def readList(self, register, length):
        results = self._bus.read_i2c_block_data(self._address, register, length)
        return results