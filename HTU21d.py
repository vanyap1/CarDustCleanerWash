class HTU21D:
    def __init__(self, busno):
        self.bus = SMBus(busno)

    def read_temperature(self):
        self.reset()
        msb, lsb, crc = self.bus.read_i2c_block_data(I2C_ADDR, CMD_TRIG_TEMP_HM, 3)
        return -46.85 + 175.72 * (msb * 256 + lsb) / 65536

    def read_humidity(self):
        self.reset()
        msb, lsb, crc = self.bus.read_i2c_block_data(I2C_ADDR, CMD_TRIG_HUMID_HM, 3)
        return -6 + 125 * (msb * 256 + lsb) / 65536.0

    def reset(self):
        self.bus.write_byte(I2C_ADDR, CMD_RESET)