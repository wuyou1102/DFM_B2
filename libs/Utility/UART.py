from Serial import Serial
import random


class UART(Serial):
    def __init__(self, port):
        Serial.__init__(self, port=port)

    def get_serial_number(self):
        pass

    def set_serial_number(self, serial):
        pass

    def get_flag_result(self, attr_name):
        print attr_name
        return random.choice(["Pass", "Fail", "NotTest"])

    def set_flag_result(self, attr_name, attr_value):
        pass
