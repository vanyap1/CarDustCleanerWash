$regfile = "m328PBdef.dat"
$crystal = 16000000
$hwstack = 64
$swstack = 32
$framesize = 80
$baud = 500000
$version 1 , 2 , 98



Config Watchdog = 4096

can_en alias portd.4 : config can_en = output : set can_en
can_int alias pind.3 : config can_int = input  : set portd.3
ld19 alias portd.5 : config ld19 = output : reset ld19
ld20 alias portd.6 : config ld20 = output : reset ld20
out_en alias portd.7 : config out_en = output : set out_en

e_stop alias pine.3 : config e_stop = input

dim out_en_timeout as byte

Dim S As String * 255 , Ns As Byte , Rs As Byte , Color_tmp As String * 4
Config Serialin = Buffered , Size = 254
Declare Sub Getline(s_dan As String)
Declare Sub Flushbuf()



Config Timer1 = Timer , Prescale = 64
dim time_count as byte  , count as byte
On Timer1 Pulse:

Enable Interrupts
Enable Timer1



print "RUN"
do
   reset Watchdog
   If Ischarwaiting() = 1 Then
      Getline S
      Flushbuf
      if left(s , 1) = "f" then
         print "R"
         out_en_timeout = 10
      end if

   end if


   ld20 = e_stop
   'ld20 = not e_stop
   if out_en_timeout > 0 and e_stop = 0 then
      set out_en
   else
      reset out_en
   end if

loop


Pulse:
   if out_en_timeout > 0 then
      decr out_en_timeout
   end if
   print e_stop
   toggle ld19

return



Sub Getline(s As String)
   S = ""
   Ns = Inkey()
   If Ns <> 10 Then
      $timeout = 100000
      Input S Noecho
      If Ns <> 10 Then S = Chr(ns) + S
   End If
End Sub

Sub Flushbuf()
   Waitms 10
   Do
      Ns = Inkey()
   Loop Until Ns = 0
End Sub