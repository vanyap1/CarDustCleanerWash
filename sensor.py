class HTU21D():
    """Class for accessing HTU21D sensors via I2C.

    Code taken from https://github.com/jasiek/HTU21D.

    Args:
        busno (int): The I2C bus (0 or 1, default is 1).
        address (byte): The I2C address of the sensor.
    """
    CMD_TRIG_TEMP_HM = 0xE3
    CMD_TRIG_HUMID_HM = 0xE5
    CMD_TRIG_TEMP_NHM = 0xF3
    CMD_TRIG_HUMID_NHM = 0xF5
    CMD_WRITE_USER_REG = 0xE6
    CMD_READ_USER_REG = 0xE7
    CMD_RESET = 0xFE

    def __init__(self, busno=1, address=config.SENSOR_ID_HUMIDITY_EXT):
        self.bus = SMBus(busno)
        self.i2c_address = address

    def read_temperature(self):
        self.reset()
        msb, lsb, crc = self.bus.read_i2c_block_data(
            self.i2c_address, self.CMD_TRIG_TEMP_HM, 3)
        return -46.85 + 175.72 * (msb * 256 + lsb) / 65536

    def read_humidity(self):
        self.reset()
        msb, lsb, crc = self.bus.read_i2c_block_data(
            self.i2c_address, self.CMD_TRIG_HUMID_HM, 3)
        return (-6 + 125 * (msb * 256 + lsb) / 65536.0) / 100.0

    def reset(self):
        self.bus.write_byte(self.i2c_address, self.CMD_RESET)