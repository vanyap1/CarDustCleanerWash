import configparser
config = configparser.ConfigParser()


class action():
    def __init__(self):
        pass

    def price_update(self, arg1 , arg2 ):
        config.read('price.ini')
        with open("price.ini", "w") as f: #a+ - appened text
            f.write("[price]\n")
            f.write("font_size = " + config["price"]['font_size'] + "\n")
            for i in range(1, 25):
                if arg1 == "drink" + str(i):
                    f.write("drink" + str(i) + " = " + arg2 + "\n")
                else:
                    f.write("drink" + str(i) + " = " + config["price"]["drink" + str(i)] + "\n")
        dat = arg1 + arg2
        return dat

    def check_price(self):
        try:
            config.read('price.ini')
            #for i in range(1, 24):
            #    print(config["price"]["drink"+str(i)])
            return "file is ok"
        except:
            config.read('price2.ini')
            with open("price.ini", "w") as f:  # a+ - appened text
                f.write("[price]\n")
                f.write("font_size = " + config["price"]['font_size'] + "\n")
                for i in range(1, 25):
                    f.write("drink" + str(i) + " = " + config["price"]["drink" + str(i)] + "\n")
            return "file restored"
    def sync_price(self):
        config.read('price.ini')
        with open("price2.ini", "w") as f:  # a+ - appened text
            f.write("[price]\n")
            f.write("font_size = " + config["price"]['font_size'] + "\n")
            for i in range(1, 25):
                f.write("drink" + str(i) + " = " + config["price"]["drink" + str(i)] + "\n")
            return "file synchronised"


class io_controll():
    def set_bit(self, v, index, x):
        mask = 1 << index
        v &= ~mask
        if x:
            v |= mask
        return v
    def write_bit(self, sbit , stat):
        #global io_status
        #io_status = custom_fun.io_controll.set_bit(self, io_status, 1, 0)
        #bus.write_byte_data(0x20, 0x02, io_status)
        pass