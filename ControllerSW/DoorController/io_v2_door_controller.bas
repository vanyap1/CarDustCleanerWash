
'$regfile = "m64def.dat"
'Const Loaderchip = 64


$regfile = "m328PBdef.dat"
Const Loaderchip = 328
$PROG &HFF, &HDE , &HC1 , &HF6



$crystal = 16000000
$hwstack = 256
$swstack = 256
$framesize = 256
'$baud = 500000 '
$baud = 250000
$version 1 , 1 , 494


Config Watchdog = 2048
Start Watchdog



$PROGRAMMER = 3
const debg = 0
dim slave as byte
slave = 0


Config Timer1 = Timer , Prescale = 256
Dim Wtime As Byte
On Timer1 Pulse:


#if Loaderchip = 328
   Config Scl = Portc.5
   Config Sda = Portc.4
   I2cinit
   Config I2cdelay = 5
   test_led alias portd.5   : config test_led = output
   io_en alias portd.7   : config io_en = output
   fail_led alias portd.6   : config fail_led = output'  : set fail_led

   exp_int alias pine.7 : config exp_int = input  : set porte.7
   Config 1wire = Porte.1

   On PCINT3 Pcint27_isr:
   Pcmsk3 = &B00001000
   PCICR = &B00001000
   Enable PCINT3



#endif



#if Loaderchip = 64
   config portb = output
   Config Portc = input
   portc = 255
   Config Scl = PortG.4
   Config Sda = Portg.3
   Config I2cdelay = 1
   I2cinit

   test_led alias portd.5   : config test_led = output
   io_en alias portd.6   : config io_en = output
   fail_led alias portd.7   : config fail_led = output'  : set fail_led
   exp_int alias pind.2 : config exp_int = input  : set portd.2
   Config 1wire = Porte.2
#endif




Const RTC_R = &HD1
Const RTC_W = &HD0

Const EXP_R = &H4D
Const EXP_W = &H4C

Const EXP2_R = &H4F
Const EXP2_W = &H4E

Const ADC_W = &H90
Const ADC_R = &H91

Dim adc_data As Word
Dim ADC_l_byte As Byte At adc_data Overlay
Dim ADC_h_byte As Byte At ADC_l_byte + 1 Overlay


Config Serialin = Buffered , Size = 64
Dim S As String * 64 , Str_com As String * 64
Dim s_buf(64) As Byte At S Overlay

Dim Arg(6) As String * 32 , el_count as byte , i as byte , port_mask as byte
dim adc_args(2) as byte  , tmp_str as string*8

dim time_long as long
dim _tm(4) as byte At time_long Overlay


dim port_common_state as word
dim port_state_tmp as byte , bit_num as byte

dim temp as byte
dim operation as byte , operation_request as byte , err_detect as byte
dim io_enable as byte
dim keep_alive_timer as long

Declare function serial_read() as string
declare function readADC(byval pga as byte, byval adc_ch As Byte) as string*6


declare sub io_data_write (byval arg1 as byte ,byval arg2 as byte, byval io_power_en as byte)


declare function io_data_read ()as byte
declare function i2c_devices_check(byval arg1 as byte)as byte

declare function 1W_RTC_reset()as byte
declare function 1W_RTC_write()as byte
declare function 1W_RTC_read()as byte
declare sub 1W_ID_scan()
declare sub 1W_KEY_scan()
declare sub i2c_scan()
dim tmp_array(8) as byte
declare function 1W_KEY_check()as byte
declare function 1W_KEY_write_new()as byte

declare function get_temp(byval arg1 as byte) as word

Config Clock = User                                         'Use USER to write/use your own code
Config Date = Dmy , Separator = .

'28,B0,D9,EA,31,21,06,4B, - soldered
'28,88,76,DF,31,21,06,92,

Dim t1_eram(8) As Eram Byte At $10
Dim t2_eram(8) As Eram Byte At $20
Dim key_eram(8) As Eram Byte At $30

dim id_tmp(8) as string*2
Dim t1_addr(8) As Byte , t(2) as integer  , w as byte
Dim t2_addr(8) As Byte
Dim 1w_key(8) As Byte


for i = 1 to 8
 t1_addr(i) = t1_eram(i)
 t2_addr(i) = t2_eram(i)
 1w_key(i) = key_eram(i)
next
Dim Ar(8) As Byte ,  C As Byte

'0 - 000 : FSR = ±6.144 V
'1 - 001 : FSR = ±4.096 V
'2 - 010 : FSR = ±2.048 V (default)
'3 - 011 : FSR = ±1.024 V
'4 - 100 : FSR = ±0.512 V
'5 - 101 : FSR = ±0.256 V
'6 - 110 : FSR = ±0.256 V
'7 - 111 : FSR = ±0.256 V
io_enable = 0
io_data_write 0  , EXP_W , io_enable
io_data_write 0  , EXP2_W , io_enable

Enable Interrupts


'if 1W_KEY_check() > 0 then
'   do
'      reset Watchdog
'      print "err:invalid 1W_key"
'      toggle fail_led
'      waitms 500
'      If Ischarwaiting() = 1 Then
'      set test_led
'      Str_com = serial_read()
'          if left(Str_com , 4) = "skip" then
'          goto run
'          end if
'      end if
'   loop
'end if

run:

waitms 100
'adc:0:2:r{013}
'in:ff:h:r{013}
'out:b:00000001:s{013}
'

Enable Timer1


'Date$ = "09.01.22"
'Time$ = "20:47:00"
'1W_RTC_write

'do
't1_addr(1) = 1wsearchfirst()
'for i = 1 to 8
'print hex(t1_addr(i)) ; "," ;
'next
'print
't2_addr(1) = 1wsearchnext()
'for i = 1 to 8
'print hex(t2_addr(i)) ; "," ;
'next
'print







'loop
'do
'   if 1W_RTC_read() > 0 then
'   print "err:rtc:read"
'   end if
'   print "32bit - " ; time_long ; " d > " ; date$ ; " t> " ;time$
'   wait 1
'   reset Watchdog
'loop
W = 1wirecount()


declare sub close_door()
declare sub open_door()


'print w
dim tmp2 as byte

up_btn alias temp.4
dn_btn alias temp.3

u_stp alias temp.1
d_stp alias temp.0

stop_btn alias temp.2
dim downtime as word

do
   reset Watchdog
   temp = io_data_read()

   if up_btn = 1 and u_stp = 0 then

       open_door
   end if

   if dn_btn = 1 and d_stp = 0 then
       close_door

   end if

   'io_data_write tmp2  , EXP_W  , 1


    '1817 up

    '1655 down






   'print bin(temp)

   waitms 10



   loop

sub close_door()
   tmp2.1 = 1
   downtime = 0
   do

   io_data_write tmp2  , EXP_W  , 1
   temp = io_data_read()
   print "close loop"
   waitms 10
   incr downtime
   loop until d_stp = 1 or stop_btn = 0 or downtime > 1955
   tmp2.1 = 0
   io_data_write tmp2  , EXP_W  , 1
   print downtime
end sub





sub open_door()
   tmp2.0 = 1
   downtime = 0
   do
   io_data_write tmp2  , EXP_W  , 1
   temp = io_data_read()
   print "open loop"
   waitms 10
   incr downtime
   loop until u_stp = 1 or stop_btn = 0 or downtime > 2117
   tmp2.0 = 0
   io_data_write tmp2  , EXP_W  , 1
   print downtime
end sub




   do

   if slave = 1 then
   set io_en
   end if

   If Ischarwaiting() = 1 Then
      set test_led
      Str_com = serial_read()
      el_count = split(Str_com , Arg() , ":")
      keep_alive_timer = 0
      fail_led = 0
      #if debg = 1
         print el_count
         for i = 1 to el_count
            print "arg(" ; i ; ") " ; Arg(i)
         next
      #endif
      if Arg(1) = "out" and Arg(4) = "s" then
         io_enable = 1
         select case Arg(2)
            case "b" : if len(arg(3)) = 8 then   : io_data_write binval(Arg(3)) , EXP_W , io_enable : else : print "err:input:bin" : end if
            case "h" : if len(arg(3)) = 2 then   : io_data_write hexval(Arg(3)) , EXP_W , io_enable : else : print "err:input:hex" : end if
            case "d" : if val(arg(3)) < 256 then : io_data_write val(Arg(3)) , EXP_W , io_enable    : else : print "err:input:dec" : end if
            case else : print "err:datatype:arg"
         end select
      end if

      if Arg(1) = "bit" and Arg(4) = "s" then
         select case arg(2)
            case "rst" :
               port_common_state = 0
               io_data_write low(port_common_state)  , EXP_W  , 0
               io_data_write high(port_common_state)  , EXP2_W  , 0
            case else :
               bit_num = val(arg(2))
               port_state_tmp = val(arg(3))
               if port_state_tmp > 0 then : port_state_tmp = 1 : io_enable = 1 :  end if
               if bit_num <= 15 or port_state_tmp <= 1 then
                  port_common_state.bit_num = port_state_tmp
                  io_data_write low(port_common_state)  , EXP_W , io_enable
                  io_data_write high(port_common_state)  , EXP2_W , io_enable
               else
                  print "err:mismatch:arg"
               end if
         end select
         #if debg = 1
            print bit_num
            print port_state_tmp
            print port_common_state
         #endif
      end if

      if Arg(1) = "in" and Arg(4) = "r" then
         select case Arg(3)
            case "b" : port_mask = binval(Arg(2)) : temp = io_data_read() : temp = temp and port_mask : print "in:b:" ; bin(temp)
            case "h" : port_mask = hexval(Arg(2)) : temp = io_data_read() : temp = temp and port_mask : print "in:h:" ; hex(temp)
            case "d" : port_mask = val(Arg(2)) : temp = io_data_read() : temp = temp and port_mask : print "in:v:" ; temp
            case else : print "err:datatype:arg"
         end select
      end if

      if Arg(1) = "adc" and Arg(4) = "r" then



         select case arg(2)
            case "0":
               adc_args(2) = val(Arg(3))
               tmp_str = readADC(adc_args(1) , 0)
            case "1":
               adc_args(2) = val(Arg(3))
               tmp_str = readADC(adc_args(1) , 1)
            case "2":
               adc_args(2) = val(Arg(3))
               tmp_str = readADC(adc_args(1) , 2)
            case "3":
               adc_args(2) = val(Arg(3))
               tmp_str = readADC(adc_args(1) , 3)
            case "4":
               adc_args(2) = val(Arg(3))
               tmp_str = readADC(adc_args(1) , 0) + ":" + readADC(adc_args(1) , 1)

         end select
         print "adc:"; Arg(2);":"; tmp_str ;":e"
      end if


      if Arg(1) = "tmp" and Arg(4) = "r" then
         print "tmp:"; arg(2) ; ":"; get_temp(val(Arg(2))) ; ":c"
      end if

      if Arg(1) = "rtc" and Arg(4) = "r" then
         temp = 1W_RTC_read()
         arg(2) = Time$
         Replacechars arg(2) , ":" , "."
         print "rtc:"; Date$ ; ";"; arg(2) ; ":e"
      end if

      if Arg(1) = "rtc" and Arg(4) = "s" then
         Replacechars arg(3) , "." , ":"
         Date$ = arg(2)
         Time$ = arg(3)
         temp = 1W_RTC_write()
      end if




      if Arg(1) = "1w_scan" and Arg(4) = "r" then
         1W_ID_scan
      end if
      if Arg(1) = "1w_key_scan" and Arg(4) = "r" then
         1w_key_scan
      end if
      if Arg(1) = "i2c_scan" and Arg(4) = "r" then
         i2c_scan
      end if




      if Arg(1) = "devID" and Arg(6) = "r" then
         if Arg(2) = "key" then
             if Arg(3) = "get" then
                 print "1W_key:" ;
                  for i = 1 to 8
                     print hex(1w_key(i)) ; "," ;
                  next
                  print ":end"

             end if
             if Arg(3) = "set" then

                  el_count = split(Arg(4) , id_tmp() , ",")
                  for i = 1 to 8
                   1w_key(i) = hexval(id_tmp(i))
                   key_eram(i) = 1w_key(i)
                  next



                  print "NOW-KEY_ID:" ;
                  for i = 1 to 8
                     temp = key_eram(i)
                     print hex(temp) ; "," ;
                  next
                  print ":end"

             end if
         end if

         if Arg(2) = "1w" then
            if Arg(3) = "get" then
               if Arg(4) = "1" then
                  print "T1_ID:" ;
                  for i = 1 to 8
                     print hex(t1_addr(i)) ; "," ;
                  next
                  print "end"
               end if
               if Arg(4) = "2" then
                  print "T2_ID:" ;
                  for i = 1 to 8
                     print hex(t2_addr(i)) ; "," ;
                  next
                  print "end"
               end if
            end if
            if Arg(3) = "set" then
               if Arg(4) = "1" then
                  el_count = split(Arg(5) , id_tmp() , ",")
                  for i = 1 to 8
                   t1_addr(i) = hexval(id_tmp(i))
                   t1_eram(i) = t1_addr(i)
                  next

                  print "NOW-T1_ID:" ;
                  for i = 1 to 8
                     temp = t1_eram(i)
                     print hex(temp) ; "," ;
                  next
                  print "end"
               end if

               if Arg(4) = "2" then
                  el_count = split(Arg(5) , id_tmp() , ",")
                  for i = 1 to 8
                   t2_addr(i) = hexval(id_tmp(i))
                   t2_eram(i) = t2_addr(i)
                  next

                  print "NOW-T2_ID:" ;
                  for i = 1 to 8
                     temp = t2_eram(i)
                     print hex(temp) ; "," ;
                  next
                  print "end"
               end if
            end if

         end if

      end if



      reset test_led
   end if
   if keep_alive_timer > 3 and slave = 0 then
      keep_alive_timer = 0
      io_enable = 0
      io_data_write 0  , EXP_W , io_enable
      io_data_write 0  , EXP2_W , io_enable
      fail_led = 1
      print "err:connection:lost"
   else
   end if

   if operation_request >= 1 then
      operation_request = 0
      1wreset
      1wwrite &HCC
      1wwrite &H44
      'print "operation_request"
   end if
loop

'END program-------------------------------------------------------------------------------

function get_temp(byval arg1 as byte) as word
   stop Timer1
   local t_tmp as integer
   1wreset
   1wwrite &H55
   select case arg1
      case 1 : 1wverify t1_addr(1)
      case 2 : 1wverify t2_addr(1)
   end select
   if err = 1 then
      t_tmp = 0 :
      get_temp = &hffff
   else
      1wwrite &HBE
      t_tmp = 1wread(2)
      t_tmp = t_tmp * 10
      t_tmp = t_tmp \ 16
      get_temp = t_tmp
   end if
   start timer1
end function



function 1W_KEY_check()as byte
   local tmp as byte
   Ar(1) = 1wsearchfirst(pind , 3)
   #if debg = 1
      print "read_key " ;
      For tmp = 1 To 8                                             'print the number
         Print Hex(Ar(tmp));
      Next
      Print
      Print "eram_key " ;
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

sub 1W_ID_scan()
   local devs as byte  , num as byte
   devs = 1wirecount()
   if devs = 0 then
      print "err:no_find"
   else
      print "devs:" ; str(devs) ; ":";
      tmp_array(1) = 1wsearchfirst()
      for i = 1 to 8
         print hex(tmp_array(i)) ; "," ;
      next
      Print ":";
      for num = 2 to devs
         tmp_array(1) = 1wsearchnext()
         for i = 1 to 8
            print hex(tmp_array(i)) ; "," ;
         next
         print ":";
      next
      print "end"
   end if

end sub


sub 1W_KEY_scan()
   local devs as byte  , num as byte
   devs = 1wirecount(pind , 3)
   if devs = 0 then
      print "err:no_find"
   else
      print "keys:" ; str(devs) ; ":";
      tmp_array(1) = 1wsearchfirst(pind , 3)
      for i = 1 to 8
         print hex(tmp_array(i)) ; "," ;
      next
         print ":";
      print "end"
   end if

end sub



pulse:
   incr operation
   incr keep_alive_timer
   if operation => 2 then : operation = 0 : end if
   operation_request = 1
return






function 1W_RTC_read() as byte
   local tmp as byte
   1wreset Pind , 3                                                 'reset the device
   1wwrite &HCC , 1 , Pind , 3
   1wwrite &H66 , 1 , Pind , 3
   tmp = 1wread(1 , Pind , 3)
   _tm(1) = 1wread(1 , Pind , 3)
   _tm(2) = 1wread(1 , Pind , 3)
   _tm(3) = 1wread(1 , Pind , 3)
   _tm(4) = 1wread(1 , Pind , 3)
   Time$ = Time(time_long)
   Date$ = Date(time_long)
   1W_RTC_read = 0
end function

function 1W_RTC_write() as byte
   time_long = Syssec()
   1wreset Pind , 3
   1wwrite &HCC  , 1 , Pind , 3
   1wwrite &H99   , 1 , Pind , 3
   1wwrite &b00001100 , 1 , Pind , 3
   1wwrite _tm(1)  , 1 , Pind , 3
   1wwrite _tm(2) , 1 , Pind , 3
   1wwrite _tm(3) , 1 , Pind , 3
   1wwrite _tm(4) , 1 , Pind , 3
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

Settime:
   #if debg = 1
      print "Settime - event"
   #endif
Return

Getdatetime:
   #if debg = 1
      print "Getdatetime - event"
   #endif
Return

Setdate:
   #if debg = 1
      print "Setdate - event"
   #endif
Return

sub i2c_scan()
   local b as byte
   print "devs:";
   For B = 0 To 254 Step 2                                     'for all odd addresses
      I2cstart                                                 'send start
      I2cwbyte B                                               'send address
      If Err = 0 Then
         print hex(b)  ; ":";
      End If
      I2cstop                                                   'free bus
   Next
   print "end"
end sub

function i2c_devices_check(byval arg1 as byte)as byte
   local b as byte
   local tmp as byte
   tmp = 1
   For B = 0 To 254 Step 2                                     'for all odd addresses
      I2cstart                                                 'send start
      I2cwbyte B                                               'send address
      If Err = 0 Then
         if b = arg1 then : tmp = 0 : end if
         print hex(b)  ; " - " ; hex(arg1)
      End If
      I2cstop                                                   'free bus
   Next
   i2c_devices_check = tmp
end function

sub io_data_write (byval arg1 as byte ,byval arg2 as byte, byval io_power_en as byte)
   local wd as byte
   reset Watchdog
   #if Loaderchip = 64
      portb = arg1
   #endif

   #if Loaderchip = 328
      wd = not arg1
      I2cstart
      I2cwbyte arg2
      I2cwbyte wd
      I2cwbyte &HFF
      I2cstop
   #endif
   if io_power_en = 0 then : reset io_en : else : set io_en : end if
end sub

function io_data_read () as byte
   #if Loaderchip = 64
      io_data_read = not pinc
   #endif
   reset Watchdog
   #if Loaderchip = 328
      local rd as byte
      I2cstart
      I2cwbyte EXP_R
      I2crbyte Rd , Ack
      I2crbyte Rd , Nack
      I2cstop
      io_data_read = not rd
   #endif
end function

function readADC(byval pga as byte , byval adc_ch As Byte) as string*6
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
   Waitms 15
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

function serial_read() as string
   $timeout = 100000
   Input S Noecho
   serial_read = s '+ "<" + str(len(s))
end function

Pcint27_isr:
print "pcint27"
return


end