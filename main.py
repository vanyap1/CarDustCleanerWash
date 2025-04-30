import time
from datetime import datetime, date, timedelta
from datetime import datetime
#import random
import subprocess
import socket
#from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen , ScreenManager
from threading import Thread
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder
#from kivy.uix.gridlayout import GridLayout
#from kivy.animation import Animation
from kivy.uix.image import Image
#from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
#from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty
#from kivy.properties import BoundedNumericProperty
from kivy.properties import StringProperty

#import custom_fun
import io , os, re, smbus # , i2c , psutil
#from kivy.uix.videoplayer import VideoPlayer
#from kivy_garden import graph
#import configparser
#import struct
from kivy.core.window import Window
from kivy.animation import Animation
#from math import sin
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot, SmoothLinePlot
from kivy.factory import Factory

releaseDate = "30.06.2024"


Builder.load_file("kv/buttons_group.kv")
Builder.load_file("kv/graph.kv")
Builder.load_file("kv/PopUpWindow.kv")
Builder.load_file("kv/PopUpAirSetup.kv")
Builder.load_file("kv/meas_lbl_group.kv")
Builder.load_file("kv/fan.kv")
Builder.load_file("kv/CleanPage.kv")
import custom_fun
import configparser
import requests
from kivy.uix.video import Video
config = configparser.ConfigParser()
config.read('/home/vanya/config.ini')

controller_dev = config['safety_board']['tty_dev']
controller_baud =config['safety_board']['tty_baud']

adc_board_dev = config['adc_board']['tty_dev']
adc_board_baud = config['adc_board']['tty_dev']
rtc_str = ['-', '-', '-', '-', '-']
adc_arr = [0, 0, 0, 0, 0, 0]
adc2_arr = [0, 0, 0, 0, 0, 0]
from kivy.config import Config

if config['relay_board1']['i2c_bus'] != '0':
    Window.size = (int(config['screen']['x']),int(config['screen']['y']))

server_data = ""
run_seq = "none"
tty_data = ""
command_tr = "none"
timer_en = 'false'
air_pressure = int(0)
pre_check_points = []
post_check_points = []
pre_check_average = int(0)
post_check_average = int(0)
minuts_duration = int(0)
second_duration = int(0)
FullTimeInSecond = int(0)
CleaningTimeInSecond = int(0)
DryingTimeInSecond = int(0)
TankWaterLevel = int(0)
AirTempActual = int(0)
AirTempSetPoint_H = int(50)
AirTempSetPoint_L = int(45)
air_duration = int(1)
air_cycle_duration = int(3)
manualAir = False

WaterTempSetPoint_H = int(50)
WaterTempSetPoint_L = int(55)
air_heater_button_state = 'true'
Water_heater_1_Stat = 'false'
Water_heater_2_Stat = 'false'

heater1_heater_on = 'images/3kw.png'
heater1_heater_off = 'images/3kw_off.png'
heater2_heater_on = 'images/6kw.png'
heater2_heater_off = 'images/6kw_off.png'


ntc_table = [1466 , 1456 , 1445 , 1434 , 1424 , 1414 , 1404 , 1394 , 1384 , 1375,  1365 , 1356 , 1347 , 1338 , 1329 , 1320 , 1311 , 1303 , 1294 , 1286,  1278 , 1270 , 1262 , 1254 , 1246 , 1238 , 1231 , 1223 , 1216 , 1209,  1202 , 1195 , 1188 , 1181 , 1174 , 1167 , 1160 , 1154 , 1147 , 1141,  1135 , 1128 , 1122 , 1116 , 1110 , 1104 , 1098 , 1092 , 1087 , 1081,  1075 , 1070 , 1064 , 1059 , 1053 , 1048 , 1043 , 1037 , 1032 , 1027,  1022 , 1017 , 1012 , 1007 , 1002 , 997 , 993 , 988 , 983 , 979,  974 , 969 , 965 , 961 , 956 , 952 , 947 , 943 , 939 , 935,  931 , 926 , 922 , 918 , 914 , 910 , 906 , 902 , 899 , 895,  891 , 887 , 883 , 880 , 876 , 872 , 869 , 865 , 862 , 858,  855 , 851 , 848 , 844 , 841 , 838 , 834 , 831 , 828 , 824,  821 , 818 , 815 , 812 , 809 , 805 , 802 , 799 , 796 , 793,  790 , 787 , 784 , 781 , 779 , 776 , 773 , 770 , 767 , 764,  762 , 759 , 756 , 753 , 751 , 748 , 745 , 743 , 740 , 737,  735 , 732 , 730 , 727 , 725 , 722 , 720 , 717 , 715 , 712,  710 , 707 , 705 , 703 , 700 , 698 , 696 , 693 , 691 , 689,  686 , 684 , 682 , 680 , 677 , 675 , 673 , 671 , 669 , 666,  664 , 662 , 660 , 658 , 656 , 654 , 652 , 650 , 648 , 646,  644 , 642 , 640 , 638 , 636 , 634 , 632 , 630 , 628 , 626,  624 , 622 , 620 , 618 , 616 , 614 , 613 , 611 , 609 , 607,  605 , 603 , 602 , 600 , 598 , 596 , 594 , 593 , 591 , 589,  587 , 586 , 584 , 582 , 581 , 579 , 577 , 575 , 574 , 572,  570 , 569 , 567 , 566 , 564 , 562 , 561 , 559 , 557 , 556,  554 , 553 , 551 , 550 , 548 , 546 , 545 , 543 , 542 , 540,  539 , 537 , 536 , 534 , 533 , 531 , 530 , 528 , 527 , 525,  524 , 523 , 521 , 520 , 518 , 517 , 515 , 514 , 513 , 511,  510 , 508 , 507 , 506 , 504 , 503 , 501 , 500 , 499 , 497,  496 , 495 , 493 , 492 , 491 , 489 , 488 , 487 , 485 , 484,  483 , 481 , 480 , 479 , 478 , 476 , 475 , 474 , 473 , 471,  470 , 469 , 467 , 466 , 465 , 464 , 463 , 461 , 460 , 459,  458 , 456 , 455 , 454 , 453 , 452 , 450 , 449 , 448 , 447,  446 , 444 , 443 , 442 , 441 , 440 , 439 , 437 , 436 , 435,  434 , 433 , 432 , 431 , 429 , 428 , 427 , 426 , 425 , 424,  423 , 422 , 420 , 419 , 418 , 417 , 416 , 415 , 414 , 413,  412 , 411 , 410 , 408 , 407 , 406 , 405 , 404 , 403 , 402,  401 , 400 , 399 , 398 , 397 , 396 , 395 , 394 , 393 , 391,  390 , 389 , 388 , 387 , 386 , 385 , 384 , 383 , 382 , 381,  380 , 379 , 378 , 377 , 376 , 375 , 374 , 373 , 372 , 371,  370 , 369 , 368 , 367 , 366 , 365 , 364 , 363 , 362 , 361,  360 , 359 , 358 , 357 , 356 , 355 , 355 , 354 , 353 , 352,  351 , 350 , 349 , 348 , 347 , 346 , 345 , 344 , 343 , 342,  341 , 340 , 339 , 338 , 337 , 337 , 336 , 335 , 334 , 333,  332 , 331 , 330 , 329 , 328 , 327 , 326 , 325 , 325 , 324,  323 , 322 , 321 , 320 , 319 , 318 , 317 , 316 , 315 , 315,  314 , 313 , 312 , 311 , 310 , 309 , 308 , 307 , 306 , 306,  305 , 304 , 303 , 302 , 301 , 300 , 299 , 298 , 298 , 297,  296 , 295 , 294 , 293 , 292 , 291 , 291 , 290 , 289 , 288,  287 , 286 , 285 , 284 , 284 , 283 , 282 , 281 , 280 , 279,  278 , 278 , 277 , 276 , 275 , 274 , 273 , 272 , 272 , 271,  270 , 269 , 268 , 267 , 266 , 266 , 265 , 264 , 263 , 262,  261 , 260 , 260 , 259 , 258 , 257 , 256 , 255 , 255 , 254,  253 , 252 , 251 , 250 , 249 , 249 , 248 , 247 , 246 , 245,  244 , 244 , 243 , 242 , 241 , 240 , 239 , 238 , 238 , 237,  236 , 235 , 234 , 233 , 233 , 232 , 231 , 230 , 229 , 228,  228 , 227 , 226 , 225 , 224 , 223 , 223 , 222 , 221 , 220,  219 , 218 , 218 , 217 , 216 , 215 , 214 , 213 , 212 , 212,  211 , 210 , 209 , 208 , 207 , 207 , 206 , 205 , 204 , 203,  202 , 202 , 201 , 200 , 199 , 198 , 197 , 197 , 196 , 195,  194 , 193 , 192 , 192 , 191 , 190 , 189 , 188 , 187 , 186,  186 , 185 , 184 , 183 , 182 , 181 , 181 , 180 , 179 , 178,  177 , 176 , 175 , 175 , 174 , 173 , 172 , 171 , 170 , 170,  169 , 168 , 167 , 166 , 165 , 164 , 164 , 163 , 162 , 161,  160 , 159 , 158 , 158 , 157 , 156 , 155 , 154 , 153 , 152,  152 , 151 , 150 , 149 , 148 , 147 , 146 , 146 , 145 , 144,  143 , 142 , 141 , 140 , 139 , 139 , 138 , 137 , 136 , 135,  134 , 133 , 132 , 132 , 131 , 130 , 129 , 128 , 127 , 126,  125 , 124 , 124 , 123 , 122 , 121 , 120 , 119 , 118 , 117,  116 , 115 , 115 , 114 , 113 , 112 , 111 , 110 , 109 , 108,  107 , 106 , 105 , 105 , 104 , 103 , 102 , 101 , 100 , 99,  98 , 97 , 96 , 95 , 94 , 93 , 93 , 92 , 91 , 90,  89 , 88 , 87 , 86 , 85 , 84 , 83 , 82 , 81 , 80,  79 , 78 , 77 , 76 , 75 , 75 , 74 , 73 , 72 , 71,  70 , 69 , 68 , 67 , 66 , 65 , 64 , 63 , 62 , 61,  60 , 59 , 58 , 57 , 56 , 55 , 54 , 53 , 52 , 51,  50 , 49 , 48 , 47 , 46 , 45 , 44 , 43 , 42 , 41,  40 , 39 , 37 , 36 , 35 , 34 , 33 , 32 , 31 , 30,  29 , 28 , 27 , 26 , 25 , 24 , 23 , 22 , 20 , 19,  18 , 17 , 16 , 15 , 14 , 13 , 12 , 11 , 10 , 8,  7 , 6 , 5 , 4 , 3 , 2 , 1 , -1 , -2 , -3,  -4 , -5 , -6 , -7 , -9 , -10 , -11 , -12 , -13 , -14,  -16 , -17 , -18 , -19 , -20 , -22 , -23 , -24 , -25 , -26,  -28 , -29 , -30 , -31 , -33 , -34 , -35 , -36 , -37 , -39,  -40 , -41 , -43 , -44 , -45 , -46 , -48 , -49 , -50 , -51,  -53 , -54 , -55 , -57 , -58 , -59 , -61 , -62 , -63 , -65,  -66 , -67 , -69 , -70 , -71 , -73 , -74 , -76 , -77 , -78,  -80 , -81 , -83 , -84 , -85 , -87 , -88 , -90 , -91 , -93,  -94 , -95 , -97 , -98 , -100 , -101 , -103 , -104 , -106 , -107,  -109 , -110 , -112 , -113 , -115 , -116 , -118 , -120 , -121 , -123,  -124 , -126 , -127 , -129 , -131 , -132 , -134 , -136 , -137 , -139,  -140 , -142 , -144 , -145 , -147 , -149 , -151 , -152 , -154 , -156,  -157 , -159 , -161 , -163 , -164 , -166 , -168 , -170 , -172 , -173,  -175 , -177 , -179 , -181 , -183 , -184 , -186 , -188 , -190 , -192,  -194 , -196 , -198 , -200 , -202 , -204 , -206 , -208 , -210 , -212,  -214 , -216 , -218 , -220 , -222 , -224 , -226 , -228 , -230 , -232,  -234 , -236 , -239 , -241 , -243 , -245 , -247 , -250 , -252 , -254,  -256 , -259 , -261 , -263 , -266 , -268 , -270 , -273 , -275 , -277,  -280 , -282 , -285 , -287 , -290 , -292 , -295 , -297 , -300 , -302,  -305 , -307 , -310 , -313 , -315 , -318 , -321 , -323 , -326 , -329,  -332 , -334 , -337 , -340 , -343 , -346 , -349 , -351 , -354 , -357,  -360 , -363 , -366 , -369 , -372 , -375 , -379 , -382 , -385 , -388,  -391 , -394 , -398 , -401 , -404 , -408 , -411 , -414 , -418 , -421,  -425 , -428 , -432 , -435 , -439 , -442 , -446 , -450 , -453 , -457,  -461 , -465 , -469 , -472]
data_for_print = "none"
e_stop = "false"
heater1 = "false"
heater2 = "false"


io_status = 0xffff
expander_config_port = [0x00, 0x00]
expander_config_polar = [0x00, 0x00]
expander_config_stat = [0xff, 0xff]
bus = smbus.SMBus(int(config['relay_board1']['i2c_bus']))

if config['relay_board1']['board_ver'] == "pf575c":

    pass



#0x68 - ADC (mcp3424e)
#0x21 - IO (PCAL9555A)
# i2cdetect -y 5
# i2cset -y 5 0x21 0x06 0x00 b


class PopUpAirSetup(Screen):
    text = StringProperty("")
    duty = StringProperty(str(air_duration))
    full = StringProperty(str(air_cycle_duration))

    def close_popup(self):
        global manualAir
        self.ids.sw1.active=False
        manualAir = False
    def io_swich(self, arg1):
        global manualAir
        if (arg1 == 'True') :
            self.set_uot(0, 1)
            manualAir = True
        else:
            self.set_uot(0, 0)
            manualAir = False

    def cycle_duration_incr(self):
        global air_cycle_duration
        if air_cycle_duration < 100:
            air_cycle_duration += 1
            self.full = str(air_cycle_duration)
        pass
    def cycle_duration_decr(self):
        global air_cycle_duration
        global air_duration
        if air_cycle_duration > 3:
            air_cycle_duration -=1
            self.full = str(air_cycle_duration)
            if air_duration >= air_cycle_duration:
                air_duration = air_cycle_duration
                self.duty = str(air_duration)
        pass

    def incr_duration(self):
        global air_duration
        if air_duration <= (air_cycle_duration):
            air_duration +=1
            if air_duration >= air_cycle_duration:
                self.duty = str(air_cycle_duration)
                self.text = "Постійна подача повітря"
            else:
                self.duty = str(air_duration)
                self.text = ""

    def decr_duration(self):
        global air_duration
        if air_duration != 0:
            air_duration -= 1
            self.duty = str(air_duration)
            if air_duration == 0:
                self.text = "Без повітря"
            else:
                self.text = ""
        else:
            self.text = "Без повітря"

    def set_uot(self, num_out, state):
        global io_status
        self.state = not state
        io_status = self.set_bit(io_status, num_out, self.state)

        self.bus_write()

    def bus_write(self):
        if config['relay_board1']['board_ver'] == "pf575c":
            try:
                bus.write_byte_data(0x27, io_status, 0xff)
            except:
                time.sleep(.1)
                try:
                    bus.write_byte_data(0x27, io_status, 0xff)
                except:
                    pass
    def set_bit(self, v, index, x):
        mask = 1 << index
        v &= ~mask
        if x:
            v |= mask
        return v



class PopUpWindow(Screen):
    text = StringProperty('no data')
    pressPre = 0
    pressPost = 0
    newPrintData = StringProperty('no data')
    
    pressPreCorrection = NumericProperty(0)
    pressPostCorrection = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(PopUpWindow, self).__init__(**kwargs)
        self.bind(on_open=self.on_open)

    def popupVent(self):
        print("popup ACT <<<<<<<<<<<<<<")
        self.print_result(self.newPrintData)


    def resultRefresh(self):
        result = f'Average after precheck: {pre_check_average + self.pressPreCorrection} KPa\n'
        result += f'Average after cleaning: {post_check_average + self.pressPostCorrection} KPa\n'
        result += f'Cleaning time: {pre_check_average} Seconds\n'
        result += f'Drying time: {DryingTimeInSecond} Seconds'
        self.newPrintData = result
        self.text = self.newPrintData


        

    def on_open(self):
        print('on enter popup')

    def dataPrepare(self):
        result = f'Average after precheck: {pre_check_average} KPa\n'
        result += f'Average after cleaning: {post_check_average} KPa\n'
        result += f'Cleaning time: {pre_check_average} Seconds\n'
        result += f'Drying time: {DryingTimeInSecond} Seconds'
        self.newPrintData = result
        self.text = self.newPrintData

    def print_result(self, arg1):
        try:
            with open('/dev/ttyUSB0', "w") as f:
                # with open('/home/vanya/PycharmProjects/Matsola_GUI/logs/log.txt', "a") as f:
                # f.write(datetime.now().strftime('%d/%m/%Y-%H:%M:%S') + ' printer ready')
                f.write("DateTime: " + datetime.now().strftime('%d/%m/%Y-%H:%M:%S') + "\n")
                f.write(arg1 +"\n")
                time.sleep(.2)
                f.write("\x1b\x69")
                time.sleep(.2)
                f.write("\x0c\n")

                print("printer OK")
        except:
            print("An exception occurred")


class Fan_Page(Scatter):
    pass
class Clean_Page(Scatter):
    pass



class Meas_lbl_group(Screen):
    run_time = StringProperty("[color=ff1a1a]00:00:00[/color]")
    ResultPressure = StringProperty('[color=FFFFFF]---[/color]')
    #AirPressure = StringProperty('[color=FFFFFF]116[/color]')
    AirTemperature = StringProperty("[color=FFFFFF]__._[/color]")
    InputWaterPressure = StringProperty('[color=FFFFFF]__._[/color]')
    OutputWaterPressure = StringProperty('[color=FFFFFF]__._[/color]')
    OutputWaterPressure2 = StringProperty('[color=FFFFFF]__._[/color]')
    OutputWaterTemp = StringProperty("[color=ffffff]__._°C[/color]")
    WaterLevel = StringProperty("[color=ffffff]80%[/color]")
    InputWaterTemp = StringProperty("[color=ffffff]__._°C[/color]")
    RunstateIcon = StringProperty('images/stop_icon.png')
    heater_en_led = StringProperty('images/led_off_g.png') #
    heater_button_off = StringProperty('images/switch0_off.png')
    heater_button_on = StringProperty('images/switch0.png')
    heater_button_state = StringProperty('_')
    AirTempSetPointLBL = StringProperty("[color=000000]" + str(AirTempSetPoint_H) + "°C[/color]")
    WaterTempSetPoint = StringProperty("[color=FFFFFF]" + str(WaterTempSetPoint_H) + "°C[/color]")
    Heater1_icon = StringProperty(heater1_heater_off)
    Heater2_icon = StringProperty(heater2_heater_off)
    IPaddress = StringProperty('None')
    sysUpdteInfo = StringProperty(f"[color=FFFFFF]Оновлено: {releaseDate}[/color]")
    def io_swich(self, arg):
        global air_heater_button_state
        if self.ids.toggle_btn.state == "down":
            air_heater_button_state = 'false'
        if self.ids.toggle_btn.state == "normal":
            air_heater_button_state = 'true'
    def temp_ajust(self):
        global AirTempSetPoint_H
        global AirTempSetPoint_L
        AirTempSetPoint_H += 10
        if AirTempSetPoint_H > 120:
            AirTempSetPoint_H = 30
        self.AirTempSetPointLBL = "[color=000000]" + str(AirTempSetPoint_H) + "°C[/color]"
        AirTempSetPoint_L = AirTempSetPoint_H - 5
    def AirSetupOpen(self):

        pass

    def WaterTempAjust(self):
        global WaterTempSetPoint_H
        global WaterTempSetPoint_L
        WaterTempSetPoint_H += 5
        if WaterTempSetPoint_H > 95:
            WaterTempSetPoint_H = 30
        WaterTempSetPoint_L = WaterTempSetPoint_H - 5
        self.WaterTempSetPoint = "[color=FFFFFF]" + str(WaterTempSetPoint_H) + "°C[/color]"


class SetGraph(Scatter):
    pass





class Dashboard(FloatLayout):
    global io_status
    sec_tick = int(0)
    T_iteration = int(0)
    pre_check_plot = LinePlot(line_width=2, color=[255 / 255, 255 / 255, 0 / 255, 255 / 255])
    post_check_plot = LinePlot(line_width=2, color=[57 / 255, 255 / 255, 150 / 255, 255 / 255])

    animation = False
    count = int(0)
    air_anim_x = int(500)
    air_anim_y = int(563)
    timer_en = "false"
    if config['relay_board1']['board_ver'] == "pf575c" and int(config['relay_board1']['i2c_bus']) >= 0:
        bus.write_byte_data(int(config['relay_board1']['hex_address'], 16), 0xff, 0xff)
        #bus.write_i2c_block_data(int(config['relay_board1']['hex_address'] , 16), 0x00, expander_config_polar)
        #bus.write_i2c_block_data(int(config['relay_board1']['hex_address'] , 16), 0x00, expander_config_port)
        #bus.write_byte_data(int(config['relay_board1']['hex_address'] , 16), 0x02, io_status)

    if config['relay_board1']['board_ver'] == "pd9535" and int(config['relay_board1']['i2c_bus']) >= 0:
        bus.write_i2c_block_data(int(config['relay_board1']['hex_address'], 16), 0x04, expander_config_polar)
        bus.write_i2c_block_data(int(config['relay_board1']['hex_address'], 16), 0x06, expander_config_port)
        bus.write_byte_data(int(config['relay_board1']['hex_address'], 16), 0x02, io_status)

    current_operation = "idle"

    def __init__(self, **kwargs):

        super(Dashboard, self).__init__(**kwargs)

        self.background_image = Image(source='images/bg.png', size=self.size)
        self.add_widget(self.background_image)

        self.printWindow = PopUpWindow()  # Create a new instance of the P class
        self.popupWindow = Factory.Popup(title="Information field", content=self.printWindow, size_hint=(None, None), size=(400, 400), auto_dismiss=False)
        #self.popupWindow.bind(on_open=self.printWindow.on_open)


        self.show = PopUpAirSetup()


        self.popupAirSetup = Factory.Popup(title="Налаштування", content=self.show, size_hint=(None, None),
                                         size=(400, 300), auto_dismiss=False)


        self.SysInfoLabel = Button(markup=True, font_size=44, text='[color=000000]MK-40/300[/color]', pos=(60, 910),
                              size=(260, 50), size_hint=(None, None), background_normal='images/SysInfoLBL.png',
                              background_down='images/SysInfoLBL.png', )

        self.SysInfoLabel.bind(on_press=self.SysInfo)
        self.add_widget(self.SysInfoLabel)


        self.printButton = Button(markup= True, pos=(340,901), size=(65, 64), size_hint=(None, None), background_normal = 'images/print.png',background_down ='images/print_p.png')
        self.add_widget(self.printButton)
        self.printButton.bind(on_press=self.printRequest)
        

        self.AirSetup = Button(text='', pos=(1010,901),  size=(65, 64), size_hint=(None, None), background_normal = 'images/air.png',
                     background_down ='images/air.png',)


        self.FN1 = Button(markup=True, font_size=34 , text='[color=000000]Тест забрудненого \n          фільтра[/color]', pos=(890,736),  size=(320, 157), size_hint=(None, None), background_normal = 'images/fn_btn_active.png',
                     background_down ='images/fn_btn_idle_press.png',)


        self.FN2 = Button(markup=True, font_size=34, text='[color=000000]Промивка фільтра[/color]', pos=(890, 577),
                     size=(320, 157), size_hint=(None, None), background_normal='images/fn_btn_idle.png',
                     background_down='images/fn_btn_idle_press.png', )


        self.FN3 = Button(markup=True, font_size=34, text='[color=000000]Просушка фільтра[/color]', pos=(890, 418),
                     size=(320, 157), size_hint=(None, None), background_normal='images/fn_btn_idle.png',
                     background_down='images/fn_btn_idle_press.png', )


        self.FN4 = Button(markup=True, font_size=34, text='[color=000000]Тест очищеного \n        фільтра[/color]', pos=(890, 259),
                     size=(320, 157), size_hint=(None, None), background_normal='images/fn_btn_idle.png',
                     background_down='images/fn_btn_idle_press.png',)



        self.RUN_btn = Button(pos=(635 , 274),
                     size=(217, 149), size_hint=(None, None), background_normal='images/run_btn.png',
                     background_down='images/run_btn_press.png', text="")


        self.STP_btn = Button(pos=(987, 77),
                         size=(217, 149), size_hint=(None, None), background_normal='images/stop_btn.png',
                         background_down='images/stop_btn_press.png', text="")
        self.FN1.bind(on_press=self.FN1_event)
        self.FN2.bind(on_press=self.FN2_event)
        self.FN3.bind(on_press=self.FN3_event)
        self.FN4.bind(on_press=self.FN4_event)
        self.RUN_btn.bind(on_press=self.RUN_event)
        self.STP_btn.bind(on_press=self.STP_event)
        self.AirSetup.bind(on_press=self.AirSetupPopUp)

        self.Meas_lbl = Meas_lbl_group()


        #self.FL4 = Image(source='images/fan_icon.png', opacity=0, size_hint=(.2, .2), pos=(self.air_anim_x-312, self.air_anim_y-10))

        self.AnimWaterFlow = Image(source='images/AnimWaterFlow.zip', opacity=0, size_hint=(.2, .2), 
                                   pos=(self.air_anim_x - 80 , self.air_anim_y - 37), anim_loop=0, anim_delay=-1)

        self.AnimFan = Image(source='images/fan_animation3.gif', opacity=0, size_hint=(.2, .2),
                                   pos=(self.air_anim_x - 312, self.air_anim_y - 10), anim_loop=0, anim_delay=-1)
        
        self.AnimAirFlow = Image(source='images/AirFlowAnimation.gif', opacity=0, size_hint=(.2, .2),
                             pos=(self.air_anim_x, self.air_anim_y-45), anim_loop=0, anim_delay=-1)

        self.FanPg = Fan_Page(pos=(85, 440), size=(750, 420), size_hint=(None, None), opacity=0, do_rotation=False, do_scale=False, do_translation=False)
        self.ClnPg = Clean_Page(pos=(85, 440), size=(750, 420), size_hint=(None, None), opacity=0, do_rotation=False,
                              do_scale=False, do_translation=False)




        self.add_widget(self.FanPg)
        self.add_widget(self.AirSetup)
        self.add_widget(self.ClnPg)

        self.add_widget(self.AnimFan)
        self.add_widget(self.AnimWaterFlow)
        self.add_widget(self.AnimAirFlow)

        self.add_widget(self.FN1)
        self.add_widget(self.FN2)
        self.add_widget(self.FN3)
        self.add_widget(self.FN4)
        self.add_widget(self.Meas_lbl)
        self.add_widget(self.RUN_btn)
        self.add_widget(self.STP_btn)
        #self.player.state = "play"
        #self.Sys_info = Float_menu(pos=(1050, 50), size=(300, 200), size_hint=(None, None))
        #self.screen.add_widget(self.Sys_info)


        #self.ButtonsGroup = btns_group(pos=(1250,580), size=(100, 180), size_hint=(None, None))
        #self.add_widget(self.ButtonsGroup)

        self.GraphExample = SetGraph(pos=(85, 450), size=(750, 400), size_hint=(None, None), do_rotation=False,
                                     do_scale=False, do_translation=False)
        self.add_widget(self.GraphExample)




        #DEBUG SECTION<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        Clock.schedule_interval(lambda dt: self.one_second_loop(), 1)
        Clock.schedule_interval(lambda dt: self.screen_update(), .2)
        #self.GraphExample.update_graph()

    def printRequest(self, event):
        self.printWindow.dataPrepare()
        self.popupWindow.open()

    def print_result(self, arg1):
        try:
            with open('/dev/ttyUSB0', "w") as f:
                # with open('/home/vanya/PycharmProjects/Matsola_GUI/logs/log.txt', "a") as f:
                # f.write(datetime.now().strftime('%d/%m/%Y-%H:%M:%S') + ' printer ready')
                f.write("DateTime: " + datetime.now().strftime('%d/%m/%Y-%H:%M:%S') + "\n")
                f.write(arg1 +"\n")
                time.sleep(.2)
                f.write("\x1b\x69")
                time.sleep(.2)
                f.write("\x0c\n")

                print("printer OK")
        except:
            print("An exception occurred")
    def AirSetupPopUp(self, event):
        self.popupAirSetup.open()

    def SysInfo(self, event):
        print("sysinfo")
    def FN1_event(self, event):
        global second_duration
        self.animation = False
        self.FN1.background_normal = "images/fn_btn_active.png"
        self.FN2.background_normal = "images/fn_btn_idle.png"
        self.FN3.background_normal = "images/fn_btn_idle.png"
        self.FN4.background_normal = "images/fn_btn_idle.png"
        self.current_operation = "pre_check"

        self.AnimAirFlow.opacity = 0
        self.AnimFan.opacity = 0
        self.AnimWaterFlow.opacity = 0
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.FanPg)
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.ClnPg)
        anim = Animation(scale=1, opacity=1, t='linear', duration=0.1)
        anim.start(self.GraphExample)
        if self.timer_en == 'false':
            second_duration = 0
        print("FN 1")
    def FN2_event(self, event):
        self.animation = False
        self.FN2.background_normal = "images/fn_btn_active.png"
        self.FN1.background_normal = "images/fn_btn_idle.png"
        self.FN3.background_normal = "images/fn_btn_idle.png"
        self.FN4.background_normal = "images/fn_btn_idle.png"
        self.current_operation = "clean"

        self.AnimAirFlow.opacity = 0
        self.AnimFan.opacity = 0
        self.AnimWaterFlow.opacity = 1


        anim = Animation(scale=.5, opacity=0, t='linear', duration=0.1)
        anim.start(self.GraphExample)
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.FanPg)
        anim = Animation(scale=1, opacity=1, t='linear', duration=0.1)
        anim.start(self.ClnPg)

    def FN3_event(self, event):
        self.animation = False
        self.FN3.background_normal = "images/fn_btn_active.png"
        self.FN1.background_normal = "images/fn_btn_idle.png"
        self.FN2.background_normal = "images/fn_btn_idle.png"
        self.FN4.background_normal = "images/fn_btn_idle.png"
        self.current_operation = "drying"


        self.AnimAirFlow.opacity = 1
        self.AnimFan.opacity = 1
        self.AnimWaterFlow.opacity = 0
        anim = Animation(scale=.5, opacity=0, t='linear', duration=0.1)
        anim.start(self.GraphExample)
        anim = Animation(scale=1, opacity=1, t='linear', duration=0.1)
        anim.start(self.FanPg)
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.ClnPg)
    def FN4_event(self, event):
        global second_duration
        self.animation = False
        self.FN4.background_normal = "images/fn_btn_active.png"
        self.FN1.background_normal = "images/fn_btn_idle.png"
        self.FN2.background_normal = "images/fn_btn_idle.png"
        self.FN3.background_normal = "images/fn_btn_idle.png"
        self.current_operation = "post_check"
        if self.timer_en != 'true':
            second_duration = 0

        self.AnimAirFlow.opacity = 0
        self.AnimFan.opacity = 0
        self.AnimWaterFlow.opacity = 0
        #self.player.state = "stop"
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.FanPg)
        anim = Animation(scale=1, opacity=0, t='linear', duration=0.1)
        anim.start(self.FanPg)
        anim = Animation(scale=1, opacity=1, t='linear', duration=0.1)
        anim.start(self.GraphExample)
    def RUN_event(self, event):
        global pre_check_points
        global post_check_points
        global minuts_duration
        global second_duration
        global FullTimeInSecond
        global CleaningTimeInSecond
        global DryingTimeInSecond
        global TankWaterLevel
        TankWaterLevel = int(0)


        if (self.current_operation == 'idle' or self.current_operation == 'pre_check' or self.current_operation == 'pre_check') and self.timer_en == 'false':
            minuts_duration = 0
            second_duration = 0
            

        if self.current_operation == "drying" or self.current_operation == "clean":
            FullTimeInSecond += 900

        if self.current_operation == "drying":
            #print("@@@", self.current_operation)
            self.AnimFan.anim_delay = .05
            self.AnimAirFlow.anim_delay = 0.1
            DryingTimeInSecond = 0
            #self.animation = True
            #self.AnimWaterFlow.anim_delay = .1
        if self.current_operation == "clean":
            #print("@@@", self.current_operation)
            self.AnimWaterFlow.anim_delay=.1
            CleaningTimeInSecond = 0
            #self.animation = True

        self.T_iteration = 0
        print("Reset counters")


        #fan_animation.repeat = True


        self.RUN_btn.background_normal = "images/run_btn_press.png"
        #self.set_uot(1 , 1)

        if self.current_operation == "idle":
            self.current_operation = "pre_check"

        if self.current_operation == "pre_check":
            pre_check_points = []
        if self.current_operation == "post_check":
            post_check_points = []

        self.timer_en = "true"
        #print('start request')
    def STP_event(self, event):
        self.stop_operation()
        


    def minimize(self, arg):
        anim = Animation(scale=.5, opacity=0, t='linear', duration=0.2)
        anim.start(arg)

    def maximize(self, arg):
        anim = Animation(scale=1, opacity=1, t='linear', duration=0.2)
        anim.start(arg)



    def reset_counter(self):
        self.sec_tick = int(0)
        #self.T_iteration = int(0)
        #self.data_to_graph = []
    def stop_operation(self):
        global FullTimeInSecond
        FullTimeInSecond = 0
        self.current_operation == "idle"
        self.animation = False
        self.AnimFan.anim_delay = -1
        self.AnimWaterFlow.anim_delay = -1
        self.AnimAirFlow.anim_delay = -1
        self.RUN_btn.background_normal = "images/run_btn.png"
        #self.current_operation = "idle"
        self.timer_en = "false"
        # self.player.state = "stop"
        io_status = 0xffff
        self.reset_all_out()
        pass
    def screen_update(self):
        global server_data
        global pre_check_points
        global post_check_points
        global pre_check_average
        global post_check_average
        global CleaningTimeInSecond
        global DryingTimeInSecond
        global TankWaterLevel
        global data_for_print
        global AirTempActual
        if run_seq == "none":
            self.reset_counter()
        pressure = float(0)
        #self.lbl_group.ids.lbl6.text = command_tr
        if e_stop == 'true':
            self.Meas_lbl.RunstateIcon = 'images/run_icon.png'
        else:
            self.Meas_lbl.RunstateIcon = 'images/stop_icon.png'

        #self.lbl_group.ids.lbl10.text = tty_data
        #print(tty_data)

        #print(x)
        if adc2_arr[0] == "S0" and adc2_arr[1] == "run" and len(adc2_arr) == 8:
            #print(ntc_table[int(x[2])]/10)
            AirTempActual = ntc_table[int(adc2_arr[3])]/10
            self.Meas_lbl.AirTemperature = str(AirTempActual)

            self.Meas_lbl.OutputWaterTemp = '[color=FFFFFF]' + str(ntc_table[int(adc2_arr[4])] / 10) + '°C[/color]'
            self.Meas_lbl.InputWaterTemp = '[color=FFFFFF]' + str(ntc_table[int(adc2_arr[2])] / 10) + '°C[/color]'

            #tmp = int(adc_arr[2].replace("+", " "))
            tmp = int(adc_arr[2])
            tmp -= 2310
            tmp *= 0.00043636363636363637
            tmp = round(tmp, 2)
            if tmp > 0.1:
                self.Meas_lbl.OutputWaterPressure2 = '[color=FFFFFF]' + str(tmp)  + '[/color]'
            else:
                self.Meas_lbl.OutputWaterPressure2 = '[color=FFFFFF]0.00[/color]'

            #tmp = int(adc_arr[3].replace("+", " "))
            tmp = int(adc_arr[3])
            tmp -= 2310
            tmp *= 0.00043636363636363637
            tmp = round(tmp, 2)
            if tmp > 0.1:
                self.Meas_lbl.OutputWaterPressure = '[color=FFFFFF]' + str(tmp) + '[/color]'
            else:
                self.Meas_lbl.OutputWaterPressure = '[color=FFFFFF]0.00[/color]'

            #tmp = int(adc_arr[4].replace("+", " "))
            tmp = int(adc_arr[4])
            tmp -= 2310
            tmp *= 0.00043636363636363637
            tmp = round(tmp, 2)
            if tmp > 0.1:
                self.Meas_lbl.InputWaterPressure = '[color=FFFFFF]' + str(tmp) + '[/color]'
            else:
                self.Meas_lbl.InputWaterPressure = '[color=FFFFFF]0.00[/color]'

            if int(adc2_arr[5]) <= 615:
                TankWaterLevel = 0
            if int(adc2_arr[5]) >= 700:
                TankWaterLevel = 100
            if int(adc2_arr[5]) > 615 and int(adc2_arr[5]) < 700:
                TankWaterLevel = int(adc2_arr[5]) - 600
            self.Meas_lbl.WaterLevel = '[color=FFFFFF]' + str(TankWaterLevel) + '%[/color]'

            #self.Meas_lbl.run_time = '[color=FFFFFF]' + rtc_str[3][0:5] + '[/color]'


            #розкоментувати якщо треба інфо за поточну операцію
            #print(self.current_operation , " E_stop" , e_stop)
            #print(adc2_arr)
            #print(rtc_str)
            self.Meas_lbl.ResultPressure = '[color=FFFFFF]' + str(round((int(adc_arr[1]) / 2), 1)) + '[/color]'
            if self.current_operation == "pre_check" and self.timer_en == "true":
                self.set_uot(6, 1)
                pre_check_points.append((self.T_iteration, int(adc_arr[1])/2))
                #self.Meas_lbl.ResultPressure = '[color=FFFFFF]' + str(round((int(adc_arr[1])/2),1)) + '[/color]'
                self.pre_check_plot.points = pre_check_points
                self.GraphExample.ids.graph_test.add_plot(self.pre_check_plot)
                self.T_iteration += 1
                if self.T_iteration >= 100:
                    self.set_uot(6, 0)
                    self.stop_operation()
                    self.T_iteration = 0
                    #print(self.pre_check_plot.points[int(len(self.pre_check_plot.points)) - 1], ">>> ", self.T_iteration)
                    pre_check_average = 0
                    for i in pre_check_points:
                        pre_check_average = pre_check_average + int(i[1])
                    pre_check_average = pre_check_average / len(pre_check_points)

            if self.current_operation == "post_check" and self.timer_en == "true":
                self.set_uot(6, 1)
                post_check_points.append((self.T_iteration, int(adc_arr[1])/2))
                self.Meas_lbl.ResultPressure = '[color=FFFFFF]' + str(round((int(adc_arr[1]) / 2), 1)) + '[/color]'
                self.post_check_plot.points = post_check_points
                self.GraphExample.ids.graph_test.add_plot(self.post_check_plot)
                self.T_iteration += 1
                if self.T_iteration >= 100:
                    self.set_uot(6, 0)
                    self.stop_operation()
                    self.T_iteration = int(0)

                    post_check_average = 0
                    for i in post_check_points:
                        post_check_average = post_check_average + int(i[1])
                    post_check_average = post_check_average / len(post_check_points)

                    #print("all - " , post_check_average)
                    #print(post_check_points[1][1])
                    #post_check_average = post_check_points
                    self.printWindow.text = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')  + '\n'
                    self.printWindow.text += 'Average after precheck: ' + str(pre_check_average) + ' KPa\n'
                    self.printWindow.text+= 'Average after cleaning: ' + str(post_check_average) + ' KPa\n'
                    self.printWindow.text += "Cleaning time:" + str(CleaningTimeInSecond) + ' Seconds\n'
                    self.printWindow.text += "Drying time:" + str(DryingTimeInSecond) + ' Seconds\n'
                    #self.print_result(self.show.text)
                    data_for_print = self.printWindow.text
                    try:
                        # with open('/dev/ttyUSB0', "w") as f:
                        with open('/home/vanya/log.txt', "a") as f:
                            f.write(self.printWindow.text + '\n printer ready \n\r\x1b\x69')
                            f.write('\x0c\n')
                            print("printer OK")
                    except:
                        print("An exception occurred")
                    self.printWindow.dataPrepare()    
                    self.popupWindow.open()
                    #self.popupWindow.ids.pop_label.text = "fff"
                #print(self.post_check_plot.points[int(len(self.post_check_plot.points)) - 1], ">>> ", self.T_iteration)


            if adc2_arr[0] == "adc" and adc2_arr[1] == "0":
                tmp=int(adc2_arr[2].replace("+" , " "))
                tmp *=0.00125128492664237
                tmp *=111.11111111111111
                tmp -=136
                pressure = tmp
                #self.lbl_group.ids.lbl7.text = "P1 = " + str(round(tmp,2)) + "KPa"
            if adc2_arr[0] == "adc" and adc2_arr[1] == "1":
                tmp=int(adc2_arr[2].replace("+" , " "))
                tmp -= 2310
                tmp *= 0.00043636363636363637
                tmp = round(tmp , 2)
                #self.lbl_group.ids.lbl8.text = "ADC1 = " + str(tmp)



        if server_data != "none":
            #self.Sys_info.ids.debug_lbl2.text = server_data
            server_data = "none"

    indata = ""



    timer_counter = int(0)

    def one_second_loop(self):
        global minuts_duration
        global second_duration
        global FullTimeInSecond
        global CleaningTimeInSecond
        global DryingTimeInSecond
        global TankWaterLevel
        global Water_heater_1_Stat , Water_heater_2_Stat
        if TankWaterLevel <= 70:
            self.set_uot(1, 1)


        self.Meas_lbl.IPaddress = self.get_ip_addresses()


        if TankWaterLevel > 90:
            self.set_uot(1, 0)
        if self.timer_en == 'true':
            if self.current_operation == "drying" or self.current_operation == "clean":
                second_duration +=1
                #FullTimeInSecond +=1
                if FullTimeInSecond > 0 and (self.current_operation == "drying" or self.current_operation == "clean"):
                    FullTimeInSecond -= 1
                if FullTimeInSecond < 1 and (self.current_operation == "drying" or self.current_operation == "clean"):
                    self.stop_operation()
                ty_res = time.gmtime(FullTimeInSecond)
                self.Meas_lbl.run_time = str(time.strftime("%H:%M:%S", ty_res))  #"%H:%M:%S"
                #if second_duration == 60:
                #minuts_duration += 1
            if self.current_operation == "pre_check" or self.current_operation == "post_check":
                second_duration += 1
                ty_res = time.gmtime(second_duration)
                self.Meas_lbl.run_time = str(time.strftime("%M:%S", ty_res))  # "%H:%M:%S"




        if heater1 == 'true' and (ntc_table[int(adc2_arr[4])] / 10) <= WaterTempSetPoint_L:
            Water_heater_1_Stat = 'true'
            self.Meas_lbl.Heater1_icon = heater1_heater_on
            self.set_uot(3, 1)

        if heater2 == 'true' and (ntc_table[int(adc2_arr[4])] / 10) <= WaterTempSetPoint_L:
            Water_heater_2_Stat = 'true'
            self.Meas_lbl.Heater2_icon = heater2_heater_on
            self.set_uot(4, 1)
        if (ntc_table[int(adc2_arr[4])] / 10) >= WaterTempSetPoint_H:
            Water_heater_1_Stat = 'false'
            Water_heater_2_Stat = 'false'
            self.Meas_lbl.Heater1_icon = heater1_heater_off
            self.Meas_lbl.Heater2_icon = heater2_heater_off
            self.set_uot(3, 0)
            self.set_uot(4, 0)

        if heater1 == 'false':
            self.Meas_lbl.Heater1_icon = heater1_heater_off
            self.set_uot(3, 0)
        if heater2 == 'false':
            self.Meas_lbl.Heater2_icon = heater2_heater_off
            self.set_uot(4, 0)


        if self.current_operation == "drying" and self.timer_en == 'true':
            DryingTimeInSecond += 1
            if air_heater_button_state == 'true':
                if AirTempActual <= AirTempSetPoint_L:
                    self.set_uot(7, 1)
                    self.Meas_lbl.heater_en_led = 'images/led_on_g.png'
                if AirTempActual >= AirTempSetPoint_H:
                    self.set_uot(7, 0)
                    self.Meas_lbl.heater_en_led = 'images/led_off_g.png'
            else:
                self.set_uot(7, 0)
                self.Meas_lbl.heater_en_led = 'images/led_off_g.png'

            self.set_uot(6, 1)
        #if Water_heater_1_Stat == 'true' or Water_heater_2_Stat == 'true':
        #    self.Meas_lbl.heater_en_led = 'images/led_on_g.png'
        #else:
        #    self.Meas_lbl.heater_en_led = 'images/led_off_g.png'




        if self.current_operation == "clean" and self.timer_en == 'true':
            CleaningTimeInSecond += 1

            self.set_uot(5, 1)
            if self.timer_counter == 0:
                self.set_uot(0, 1)
            if self.timer_counter == air_duration:
                self.set_uot(0, 0)

        else:
            self.set_uot(5, 0)
            if manualAir != True:
                self.set_uot(0, 0)

        global server_data
        #self.Sys_info.ids.debug_lbl.text = str(self.sec_tick)
        #self.ButtonsGroup.ids.stuff_p.text = str(self.sec_tick)
        #print(io_status)
        #self.data_to_graph.append((self.sec_tick, random.randint(10,15)))
        #self.plot.points = self.data_to_graph
        #self.GraphExample.ids.graph_test.add_plot(self.plot)
        #self.GraphExample.update_graph()
        if self.timer_en == 'true':
            self.timer_counter +=1
            print(str(self.timer_counter))
            if self.timer_counter ==1:
                #self.set_uot(2, 1)
                #self.set_uot(5, 1)
                pass

            if self.timer_counter ==air_cycle_duration:
                self.timer_counter = 0
                #self.command_write("bit:0:0:s")

        if self.sec_tick >= 100:
            self.sec_tick = 0
            self.data_to_graph = [(0, 0)]


        #self.Sys_info.ids.debug_lbl2.text = "RAM: " + str(round((psutil.Process(os.getpid()).memory_info().rss/1024)/1024, 1)) + " mB\nCPU: " + str(psutil.cpu_percent()) + " %"
    def get_ip_addresses(self):
        result = subprocess.run(['ip', 'addr'], stdout=subprocess.PIPE, text=True)
        ip_addresses = []
        for line in result.stdout.split('\n'):
            if 'inet ' in line and '127.0.0.1' not in line:
                ip_address = line.split()[1].split('/')[0]
                ip_addresses.append(ip_address)
        res = ', '.join(ip_addresses)
        return res
    

    def bus_write(self):
        if config['relay_board1']['board_ver'] == "pf575c":
            try:
                bus.write_byte_data(0x27, io_status, 0xff)
            except:
                time.sleep(.1)
                try:
                    bus.write_byte_data(0x27, io_status, 0xff)
                except:
                    pass


        if config['relay_board1']['board_ver'] == "pd9535":
            bus.write_byte_data(int(config['relay_board1']['hex_address'], 16), 0x02, io_status)


    def reset_all_out(self):
        global io_status
        io_status = 0xffff
        self.bus_write()
    def set_uot(self, num_out , state):
        global io_status
        self.state = not state
        io_status = self.set_bit(io_status, num_out, self.state)
        self.bus_write()
    def set_bit(self, v, index, x):
        mask = 1 << index
        v &= ~mask
        if x:
            v |= mask
        return v


    def server_handler(self, arg):
        global server_data
        server_data = arg
        print(server_data)

    def command_write(self, command):
        try:
            with open(controller_dev, "w") as f:
                f.write(command + '\r')
                time.sleep(.1)
        except:
            pass



class Server_handler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        ps = Dashboard()
        if (config['server']['enable'] == "true"):
            print("http enable")
            while True:
                server_str_request = "http://" + config['server']['url'] + ":" + config['server']['port'] + "/" + \
                                     config['server']['script']
                response = requests.get(server_str_request)
                if (response.status_code == 200):
                    result = response.content
                    ps.server_handler(str(result))
                time.sleep(5)

class PlcDataReader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global PlcRead
        global tty_data
        global adc2_arr
        tty = io.TextIOWrapper(io.FileIO(os.open(controller_dev, os.O_NOCTTY | os.O_RDWR), "r+"))
        while True:
            try:
                for line in iter(tty.readline, None):
                    tmp = line.strip()

                    if len(tmp) >= 1:
                        re.sub("^\s+|\n|\r|\s+$", '', tmp)
                        precheck_arr = tmp.split(";")

                        if len(precheck_arr) == 8:

                            if precheck_arr[0] == 'S0':

                                adc2_arr = tmp.split(";")
            except:
                #pass
                print("ADC data read error")

class AdcDataReader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global adc_arr
        global rtc_str
        ttyADC = io.TextIOWrapper(io.FileIO(os.open(adc_board_dev, os.O_NOCTTY | os.O_RDWR), "r+"))
        while True:
            try:
                for line in iter(ttyADC.readline, None):
                    tmp = line.strip()
                    if len(tmp) >= 1:
                        re.sub("^\s+|\n|\r|\s+$", '', tmp)
                        precheck_arr = tmp.split("/")
                        if len(precheck_arr) == 6:
                            if precheck_arr[0] == 'adc' and precheck_arr[5] == 'eof':
                                adc_arr = tmp.split("/")
                        if len(precheck_arr) == 5:
                            if precheck_arr[0] == 'date$' and precheck_arr[4] == 'eof':
                                rtc_str = tmp.split("/")
            except:
                #pass
                print("rs484 error")






class controller_handler(Thread):
    command = "none"
    line_num = 0
    iteration = int(0)
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
        Clock.schedule_interval(lambda dt: self.controll_loop(), .5)
        Clock.schedule_interval(lambda dt: self.rtc_parce(), 3)
    def run(self):
        while True:
            time.sleep(1)
            self.command_write("f")

    def command_write(self, command):
        with open(controller_dev, "w") as f:
            f.write(command + '\r')
            #time.sleep(.1)
    def rtc_parce(self):
        try:
            with open(adc_board_dev, "w") as f:
                f.write('d\r')
        except:
            print("An exception occurred")

    def controll_loop(self):
        global  e_stop
        global heater1
        global heater2
        result = 255
        if config['relay_board1']['board_ver'] == "pf575c" and int(config['relay_board1']['i2c_bus']) >= 0:
            try:
                result = bus.read_word_data(int(config['relay_board1']['hex_address'], 16), io_status)
                pass
            except:
                time.sleep(.1)
                try:
                    result = bus.read_word_data(int(config['relay_board1']['hex_address'], 16), io_status)
                    pass
                except:
                    pass


        if config['relay_board1']['board_ver'] == "pd9535" and int(config['relay_board1']['i2c_bus']) >= 0:
            result = bus.read_word_data(int(config['relay_board1']['hex_address'], 16), 0x00)
        result = (result & (0xff << 8)) >> 8
        result = 255 - result


        if (result >> 0) & 1:
            e_stop = 'true'
        else:
            e_stop = 'false'

        if (result >> 1) & 1:
            heater1 = 'true'
        else:
            heater1 = 'false'
        if (result >> 2) & 1:
            heater2 = 'true'
        else:
            heater2 = 'false'

        #print("io state: ", result)







class BoxApp(App):
    def build(self):
        dashboard = Dashboard()

        return dashboard
    def on_request_close(self, *args):
        print("end of programm")
        pass

if __name__ == '__main__':

    os.system(f'stty -F {controller_dev} {controller_baud} cs8 -cstopb -parenb -echo')
    os.system(f'stty -F {adc_board_dev} {adc_board_baud} cs8 -cstopb -parenb -echo')
    os.system('stty -F /dev/ttyS2 500000 cs8 -cstopb -parenb -echo')
    os.system('stty -F /dev/ttyUSB0 115200 cs8 -cstopb -parenb -echo')
    #os.system('stty -F /dev/ttyUSB1 500000 cs8 -cstopb -parenb -echo')

    #Panel = DashBoard()
    #Server_handler()
    PlcDataReader()
    AdcDataReader()
    controller_handler()
    #Panel.run()
    BoxApp().run()

