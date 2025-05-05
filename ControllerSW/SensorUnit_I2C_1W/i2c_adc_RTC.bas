
$regfile = "m328pbdef.dat"
Const Loaderchip = 328
'$PROG &HFF, &HDE , &HC1 , &HF6



$crystal = 16000000
$hwstack = 256
$swstack = 256
$framesize = 256
$baud = 500000 '
'$baud = 38400
$version 1 , 1 , 40


Config Watchdog = 2048
Start Watchdog


$PROGRAMMER = 3
const debg = 0


Const ADC_W = &H90
Const ADC_R = &H91

Config Scl = Portc.3
Config Sda = Portc.4
I2cinit
Config I2cdelay = 1
Config 1wire = Portc.0

Dim 1w_key(8) As Byte

Dim Ar(8) As Byte ,  C As Byte

1w_key(8) = &h1d
1w_key(7) = &h00
1w_key(6) = &h00
1w_key(5) = &h00
1w_key(4) = &h57
1w_key(3) = &h32
1w_key(2) = &h36
1w_key(1) = &h24





Config Clock = User                                         'Use USER to write/use your own code
Config Date = Dmy , Separator = .
Date$ = "10.08.22"
Time$ = "20:35:30"


dim nodeID as byte, e_nodeID as eram byte , def_state as byte , e_def_state as eram byte

nodeID = e_nodeID
def_state = e_def_state




dim S As Sram String * 128                                   'ser.Ausgabepuffer







alm_led alias portb.0 : config alm_led = output : reset alm_led
run_led alias portd.7 : config run_led = output : reset run_led
tx_en alias portd.5 : config tx_en = output : reset tx_en


Config Com1 = 500000 , Synchrone = 0 , Parity = None , Stopbits = 1 , Databits = 8 , Clockpol = 0


Dim adc_data As Word
Dim ADC_l_byte As Byte At adc_data Overlay
Dim ADC_h_byte As Byte At ADC_l_byte + 1 Overlay

Dim Arg(6) As String * 32 , el_count as byte , i as byte , port_mask as byte
dim adc_args(2) as byte


Dim S1 As String * 100 , Str_com1 As String * 100
Dim s_buf1(100) As Byte At S1 Overlay
'dim arg(5) as string*16 ', args_count as byte

dim time_long as long , temp as byte
dim _tm(4) as byte At time_long Overlay


Declare sub Com1_read()

declare sub rs485_write (byval arg as string*100)
declare function 1W_RTC_reset()as byte
declare function 1W_RTC_write()as byte
declare function 1W_RTC_read()as byte
declare function 1W_KEY_check()as byte
declare function 1W_KEY_write_new()as byte
declare function readADC(byval adc_ch As Byte , byval pga as byte) as string*6



Config Timer1 = Timer , Prescale = 64
Dim Wtime As Byte
Const Timer1pre = 40536 '0.2hz - 16784
On Timer1 convercion_request:
Timer1 = Timer1pre


dim conversion_ready as byte , conversion_start as byte  , stat as byte
conversion_start = def_state

rs485_write "baud 500000kbps, type AT+HELP?"



Enable Interrupts
'Enable Int0
'Enable Int1
Enable Timer1

do
   reset Watchdog

   If Ischarwaiting() = 1 Then
      Com1_read
      s1 = Lcase(s1)
      el_count = split(s1 , Arg() , ":")
      if left(s1 , 1) = "d" then
      stat = 1W_RTC_read ()
      s = "date$/" + str(time_long) + "/" + date$ + "/" + time$ + "/eof"
      print s
      end if

      if Arg(1) = "rtc" and Arg(4) = "s" then
         Replacechars arg(3) , "." , ":"
         Date$ = arg(2)
         Time$ = arg(3)
         temp = 1W_RTC_write()
      end if


    'rs485_write  arg(1)


   end if







   if conversion_ready > 0 and conversion_start > 0 then
      set run_led
      s = "adc/" + readADC(adc_args(1) , 0) + "/" + readADC(adc_args(1) , 1) + "/" + readADC(adc_args(1) , 2) + "/" + readADC(adc_args(1) , 3) + "/eof"
      rs485_write s

      reset run_led


      conversion_ready = 0
      if conversion_start > 1 then : conversion_start = 1 : end if





   end if




loop

convercion_request:
   Timer1 = Timer1pre
   conversion_ready = 1
return


Settime:

Return

Getdatetime:

Return

Setdate:
Return



function readADC(byval adc_ch As Byte, byval pga as byte) as string*6
   local ch as byte
   select case adc_ch
      case 0 : ch = &B11000000
      case 1 : ch = &B11010000
      case 2 : ch = &B11100000
      case 3 : ch = &B11110000    '0010
   end select
   Shift pga , Left , 1
   ch = ch + pga
   I2cstart
   I2cwbyte ADC_W
   I2cwbyte 1
   I2cwbyte ch
   I2cwbyte &B10000011
   I2cstop
   Waitms 10
   I2cstart
   I2cwbyte ADC_W
   I2cwbyte 0
   I2cstart
   I2cwbyte ADC_R
   I2crbyte ADC_h_byte , Ack
   I2crbyte ADC_l_byte , Nack
   I2cstop
   if adc_data.15 = 1 Then
      adc_data = 65535 - adc_data
      readADC = "-" + str(adc_data)
   else
      readADC = "+" + str(adc_data)
   end if
end function



function 1W_KEY_check()as byte
   local tmp as byte
   Ar(1) = 1wsearchfirst()
   #if debg = 1
      print "FN"
      For tmp = 1 To 8                                             'print the number
         Print Hex(Ar(tmp));
      Next
      Print
      For tmp = 1 To 8                                             'print the number
         Print Hex(1w_key(tmp));
      Next
      Print
      print "end FN"
   #endif

   1W_KEY_check = Compare(Ar , 1w_key , 8)
end function


function 1W_KEY_write_new()as byte


end function

function 1W_RTC_read() as byte
   local tmp as byte
   1wreset                                                  'reset the device
   1wwrite &HCC
   1wwrite &H66
   tmp = 1wread()
   _tm(1) = 1wread()
   _tm(2) = 1wread()
   _tm(3) = 1wread()
   _tm(4) = 1wread()
   Time$ = Time(time_long)
   Date$ = Date(time_long)
   1W_RTC_read = 0
end function

function 1W_RTC_write() as byte
   time_long = Syssec()
   1wreset
   1wwrite &HCC
   1wwrite &H99
   1wwrite &b00001100
   1wwrite _tm(1)
   1wwrite _tm(2)
   1wwrite _tm(3)
   1wwrite _tm(4)
   1W_RTC_write = 0
end function

function 1W_RTC_reset()as byte
   1wreset
   1wwrite &HCC
   1wwrite &H99
   1wwrite &b00001100
   1wwrite &H00
   1wwrite &H00
   1wwrite &H00
   1wwrite &H00
   1W_RTC_reset = 0
end function

sub rs485_write (byval arg as string*100)
   set tx_en
   print  arg
   Bitwait UCSR0A.5 , set
   waitus 50
   reset tx_en
end sub


sub Com1_read()
   $timeout = 100000
   Input  S1 Noecho
   'Com1_read = s1 '+ "<" + str(len(s))
end sub


status_table:

data "stop" , "run"


$data

'NTC-Temperatursensor Tabelle , 0-1023 = Temperatur in °C/10
Ntcsensor:
   Data 1466 % , 1456 % , 1445 % , 1434 % , 1424 % , 1414 % , 1404 % , 1394 % , 1384 % , 1375 %
   Data 1365 % , 1356 % , 1347 % , 1338 % , 1329 % , 1320 % , 1311 % , 1303 % , 1294 % , 1286 %
   Data 1278 % , 1270 % , 1262 % , 1254 % , 1246 % , 1238 % , 1231 % , 1223 % , 1216 % , 1209 %
   Data 1202 % , 1195 % , 1188 % , 1181 % , 1174 % , 1167 % , 1160 % , 1154 % , 1147 % , 1141 %
   Data 1135 % , 1128 % , 1122 % , 1116 % , 1110 % , 1104 % , 1098 % , 1092 % , 1087 % , 1081 %
   Data 1075 % , 1070 % , 1064 % , 1059 % , 1053 % , 1048 % , 1043 % , 1037 % , 1032 % , 1027 %
   Data 1022 % , 1017 % , 1012 % , 1007 % , 1002 % , 997 % , 993 % , 988 % , 983 % , 979 %
   Data 974 % , 969 % , 965 % , 961 % , 956 % , 952 % , 947 % , 943 % , 939 % , 935 %
   Data 931 % , 926 % , 922 % , 918 % , 914 % , 910 % , 906 % , 902 % , 899 % , 895 %
   Data 891 % , 887 % , 883 % , 880 % , 876 % , 872 % , 869 % , 865 % , 862 % , 858 %
   Data 855 % , 851 % , 848 % , 844 % , 841 % , 838 % , 834 % , 831 % , 828 % , 824 %
   Data 821 % , 818 % , 815 % , 812 % , 809 % , 805 % , 802 % , 799 % , 796 % , 793 %
   Data 790 % , 787 % , 784 % , 781 % , 779 % , 776 % , 773 % , 770 % , 767 % , 764 %
   Data 762 % , 759 % , 756 % , 753 % , 751 % , 748 % , 745 % , 743 % , 740 % , 737 %
   Data 735 % , 732 % , 730 % , 727 % , 725 % , 722 % , 720 % , 717 % , 715 % , 712 %
   Data 710 % , 707 % , 705 % , 703 % , 700 % , 698 % , 696 % , 693 % , 691 % , 689 %
   Data 686 % , 684 % , 682 % , 680 % , 677 % , 675 % , 673 % , 671 % , 669 % , 666 %
   Data 664 % , 662 % , 660 % , 658 % , 656 % , 654 % , 652 % , 650 % , 648 % , 646 %
   Data 644 % , 642 % , 640 % , 638 % , 636 % , 634 % , 632 % , 630 % , 628 % , 626 %
   Data 624 % , 622 % , 620 % , 618 % , 616 % , 614 % , 613 % , 611 % , 609 % , 607 %
   Data 605 % , 603 % , 602 % , 600 % , 598 % , 596 % , 594 % , 593 % , 591 % , 589 %
   Data 587 % , 586 % , 584 % , 582 % , 581 % , 579 % , 577 % , 575 % , 574 % , 572 %
   Data 570 % , 569 % , 567 % , 566 % , 564 % , 562 % , 561 % , 559 % , 557 % , 556 %
   Data 554 % , 553 % , 551 % , 550 % , 548 % , 546 % , 545 % , 543 % , 542 % , 540 %
   Data 539 % , 537 % , 536 % , 534 % , 533 % , 531 % , 530 % , 528 % , 527 % , 525 %
   Data 524 % , 523 % , 521 % , 520 % , 518 % , 517 % , 515 % , 514 % , 513 % , 511 %
   Data 510 % , 508 % , 507 % , 506 % , 504 % , 503 % , 501 % , 500 % , 499 % , 497 %
   Data 496 % , 495 % , 493 % , 492 % , 491 % , 489 % , 488 % , 487 % , 485 % , 484 %
   Data 483 % , 481 % , 480 % , 479 % , 478 % , 476 % , 475 % , 474 % , 473 % , 471 %
   Data 470 % , 469 % , 467 % , 466 % , 465 % , 464 % , 463 % , 461 % , 460 % , 459 %
   Data 458 % , 456 % , 455 % , 454 % , 453 % , 452 % , 450 % , 449 % , 448 % , 447 %
   Data 446 % , 444 % , 443 % , 442 % , 441 % , 440 % , 439 % , 437 % , 436 % , 435 %
   Data 434 % , 433 % , 432 % , 431 % , 429 % , 428 % , 427 % , 426 % , 425 % , 424 %
   Data 423 % , 422 % , 420 % , 419 % , 418 % , 417 % , 416 % , 415 % , 414 % , 413 %
   Data 412 % , 411 % , 410 % , 408 % , 407 % , 406 % , 405 % , 404 % , 403 % , 402 %
   Data 401 % , 400 % , 399 % , 398 % , 397 % , 396 % , 395 % , 394 % , 393 % , 391 %
   Data 390 % , 389 % , 388 % , 387 % , 386 % , 385 % , 384 % , 383 % , 382 % , 381 %
   Data 380 % , 379 % , 378 % , 377 % , 376 % , 375 % , 374 % , 373 % , 372 % , 371 %
   Data 370 % , 369 % , 368 % , 367 % , 366 % , 365 % , 364 % , 363 % , 362 % , 361 %
   Data 360 % , 359 % , 358 % , 357 % , 356 % , 355 % , 355 % , 354 % , 353 % , 352 %
   Data 351 % , 350 % , 349 % , 348 % , 347 % , 346 % , 345 % , 344 % , 343 % , 342 %
   Data 341 % , 340 % , 339 % , 338 % , 337 % , 337 % , 336 % , 335 % , 334 % , 333 %
   Data 332 % , 331 % , 330 % , 329 % , 328 % , 327 % , 326 % , 325 % , 325 % , 324 %
   Data 323 % , 322 % , 321 % , 320 % , 319 % , 318 % , 317 % , 316 % , 315 % , 315 %
   Data 314 % , 313 % , 312 % , 311 % , 310 % , 309 % , 308 % , 307 % , 306 % , 306 %
   Data 305 % , 304 % , 303 % , 302 % , 301 % , 300 % , 299 % , 298 % , 298 % , 297 %
   Data 296 % , 295 % , 294 % , 293 % , 292 % , 291 % , 291 % , 290 % , 289 % , 288 %
   Data 287 % , 286 % , 285 % , 284 % , 284 % , 283 % , 282 % , 281 % , 280 % , 279 %
   Data 278 % , 278 % , 277 % , 276 % , 275 % , 274 % , 273 % , 272 % , 272 % , 271 %
   Data 270 % , 269 % , 268 % , 267 % , 266 % , 266 % , 265 % , 264 % , 263 % , 262 %
   Data 261 % , 260 % , 260 % , 259 % , 258 % , 257 % , 256 % , 255 % , 255 % , 254 %
   Data 253 % , 252 % , 251 % , 250 % , 249 % , 249 % , 248 % , 247 % , 246 % , 245 %
   Data 244 % , 244 % , 243 % , 242 % , 241 % , 240 % , 239 % , 238 % , 238 % , 237 %
   Data 236 % , 235 % , 234 % , 233 % , 233 % , 232 % , 231 % , 230 % , 229 % , 228 %
   Data 228 % , 227 % , 226 % , 225 % , 224 % , 223 % , 223 % , 222 % , 221 % , 220 %
   Data 219 % , 218 % , 218 % , 217 % , 216 % , 215 % , 214 % , 213 % , 212 % , 212 %
   Data 211 % , 210 % , 209 % , 208 % , 207 % , 207 % , 206 % , 205 % , 204 % , 203 %
   Data 202 % , 202 % , 201 % , 200 % , 199 % , 198 % , 197 % , 197 % , 196 % , 195 %
   Data 194 % , 193 % , 192 % , 192 % , 191 % , 190 % , 189 % , 188 % , 187 % , 186 %
   Data 186 % , 185 % , 184 % , 183 % , 182 % , 181 % , 181 % , 180 % , 179 % , 178 %
   Data 177 % , 176 % , 175 % , 175 % , 174 % , 173 % , 172 % , 171 % , 170 % , 170 %
   Data 169 % , 168 % , 167 % , 166 % , 165 % , 164 % , 164 % , 163 % , 162 % , 161 %
   Data 160 % , 159 % , 158 % , 158 % , 157 % , 156 % , 155 % , 154 % , 153 % , 152 %
   Data 152 % , 151 % , 150 % , 149 % , 148 % , 147 % , 146 % , 146 % , 145 % , 144 %
   Data 143 % , 142 % , 141 % , 140 % , 139 % , 139 % , 138 % , 137 % , 136 % , 135 %
   Data 134 % , 133 % , 132 % , 132 % , 131 % , 130 % , 129 % , 128 % , 127 % , 126 %
   Data 125 % , 124 % , 124 % , 123 % , 122 % , 121 % , 120 % , 119 % , 118 % , 117 %
   Data 116 % , 115 % , 115 % , 114 % , 113 % , 112 % , 111 % , 110 % , 109 % , 108 %
   Data 107 % , 106 % , 105 % , 105 % , 104 % , 103 % , 102 % , 101 % , 100 % , 99 %
   Data 98 % , 97 % , 96 % , 95 % , 94 % , 93 % , 93 % , 92 % , 91 % , 90 %
   Data 89 % , 88 % , 87 % , 86 % , 85 % , 84 % , 83 % , 82 % , 81 % , 80 %
   Data 79 % , 78 % , 77 % , 76 % , 75 % , 75 % , 74 % , 73 % , 72 % , 71 %
   Data 70 % , 69 % , 68 % , 67 % , 66 % , 65 % , 64 % , 63 % , 62 % , 61 %
   Data 60 % , 59 % , 58 % , 57 % , 56 % , 55 % , 54 % , 53 % , 52 % , 51 %
   Data 50 % , 49 % , 48 % , 47 % , 46 % , 45 % , 44 % , 43 % , 42 % , 41 %
   Data 40 % , 39 % , 37 % , 36 % , 35 % , 34 % , 33 % , 32 % , 31 % , 30 %
   Data 29 % , 28 % , 27 % , 26 % , 25 % , 24 % , 23 % , 22 % , 20 % , 19 %
   Data 18 % , 17 % , 16 % , 15 % , 14 % , 13 % , 12 % , 11 % , 10 % , 8 %
   Data 7 % , 6 % , 5 % , 4 % , 3 % , 2 % , 1 % , -1 % , -2 % , -3 %
   Data -4 % , -5 % , -6 % , -7 % , -9 % , -10 % , -11 % , -12 % , -13 % , -14 %
   Data -16 % , -17 % , -18 % , -19 % , -20 % , -22 % , -23 % , -24 % , -25 % , -26 %
   Data -28 % , -29 % , -30 % , -31 % , -33 % , -34 % , -35 % , -36 % , -37 % , -39 %
   Data -40 % , -41 % , -43 % , -44 % , -45 % , -46 % , -48 % , -49 % , -50 % , -51 %
   Data -53 % , -54 % , -55 % , -57 % , -58 % , -59 % , -61 % , -62 % , -63 % , -65 %
   Data -66 % , -67 % , -69 % , -70 % , -71 % , -73 % , -74 % , -76 % , -77 % , -78 %
   Data -80 % , -81 % , -83 % , -84 % , -85 % , -87 % , -88 % , -90 % , -91 % , -93 %
   Data -94 % , -95 % , -97 % , -98 % , -100 % , -101 % , -103 % , -104 % , -106 % , -107 %
   Data -109 % , -110 % , -112 % , -113 % , -115 % , -116 % , -118 % , -120 % , -121 % , -123 %
   Data -124 % , -126 % , -127 % , -129 % , -131 % , -132 % , -134 % , -136 % , -137 % , -139 %
   Data -140 % , -142 % , -144 % , -145 % , -147 % , -149 % , -151 % , -152 % , -154 % , -156 %
   Data -157 % , -159 % , -161 % , -163 % , -164 % , -166 % , -168 % , -170 % , -172 % , -173 %
   Data -175 % , -177 % , -179 % , -181 % , -183 % , -184 % , -186 % , -188 % , -190 % , -192 %
   Data -194 % , -196 % , -198 % , -200 % , -202 % , -204 % , -206 % , -208 % , -210 % , -212 %
   Data -214 % , -216 % , -218 % , -220 % , -222 % , -224 % , -226 % , -228 % , -230 % , -232 %
   Data -234 % , -236 % , -239 % , -241 % , -243 % , -245 % , -247 % , -250 % , -252 % , -254 %
   Data -256 % , -259 % , -261 % , -263 % , -266 % , -268 % , -270 % , -273 % , -275 % , -277 %
   Data -280 % , -282 % , -285 % , -287 % , -290 % , -292 % , -295 % , -297 % , -300 % , -302 %
   Data -305 % , -307 % , -310 % , -313 % , -315 % , -318 % , -321 % , -323 % , -326 % , -329 %
   Data -332 % , -334 % , -337 % , -340 % , -343 % , -346 % , -349 % , -351 % , -354 % , -357 %
   Data -360 % , -363 % , -366 % , -369 % , -372 % , -375 % , -379 % , -382 % , -385 % , -388 %
   Data -391 % , -394 % , -398 % , -401 % , -404 % , -408 % , -411 % , -414 % , -418 % , -421 %
   Data -425 % , -428 % , -432 % , -435 % , -439 % , -442 % , -446 % , -450 % , -453 % , -457 %
   Data -461 % , -465 % , -469 % , -472 %