import smbus
import struct
import time


class AStar:
    def __init__(self, address=20, bus_num=1):
        self.address = address
        self.bus = smbus.SMBus(bus_num)

    def read_unpack(self, register, size, fmt):
        for i in range(5):
            try:
                self.bus.write_byte(self.address, register)
                time.sleep(0.0001)
                byte_list = [self.bus.read_byte(self.address) for _ in range(size)]
                return struct.unpack(fmt, bytes(byte_list))
            except OSError:
                time.sleep(0.01)
                if i == 4:
                    raise

    def write_pack(self, register, fmt, *data):
        data_array = list(struct.pack(fmt, *data))
        for i in range(5):
            try:
                self.bus.write_i2c_block_data(self.address, register, data_array)
                time.sleep(0.0001)
                return
            except OSError:
                time.sleep(0.01)
                if i == 4:
                    raise

    def motors(self, left, right):
        self.write_pack(6, "hh", left, right)

    def read_battery_millivolts(self):
        return self.read_unpack(10, 2, "H")

    def read_analog(self):
        return self.read_unpack(12, 12, "HHHHHH")

    def read_encoders(self):
        return self.read_unpack(39, 4, "hh")

    def set_auto_mode(self, enable):
        self.write_pack(43, "?", enable)

    def trigger_calibration(self):
        self.write_pack(44, "?", True)

    def check_if_calibrating(self):
        return self.read_unpack(44, 1, "?")[0]

    def write_pid(self, kp, ki, kd):
        self.write_pack(45, "fff", kp, ki, kd)

    def read_p5_telemetry(self):
        return self.read_unpack(57, 8, "fhh")
