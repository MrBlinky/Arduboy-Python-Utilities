print "\nArduboy python sketch eraser v1.0 by Mr.Blinky May 2018"

#requires pyserial to be installed. Use "pip install pyserial" on commandline

#rename this script filename to 'uploader-1309.py' to patch uploads on the fly
#for use with SSD1309 displays

import sys
import time
import os
from serial.tools.list_ports  import comports
from serial import Serial

compatibledevices = [
 #Arduboy Leonardo
 "VID:PID=2341:0036", "VID:PID=2341:8036",
 "VID:PID=2A03:0036", "VID:PID=2A03:8036",
 #Arduboy Micro
 "VID:PID=2341:0037", "VID:PID=2341:8037",
 "VID:PID=2A03:0037", "VID:PID=2A03:8037",
 #Genuino Micro
 "VID:PID=2341:0237", "VID:PID=2341:8237",
 #Sparkfun Pro Micro 5V
 "VID:PID=1B4F:9205", "VID:PID=1B4F:9206",
]

bootloader_active = False
caterina_overwrite = False

flash_addr = 0
flash_data = bytearray(chr(0xFF) * 32768)
flash_page       = 1
flash_page_count = 0
flash_page_used  = [False] * 256

def delayedExit():
  time.sleep(3)
  #raw_input()  
  sys.exit()

def getComPort(verbose):
  global bootloader_active
  devicelist = list(comports())
  for device in devicelist:
    for vidpid in compatibledevices:
      if  vidpid in device[2]:
        port=device[0]
        bootloader_active = (compatibledevices.index(vidpid) & 1) == 0
        if verbose : print "Found {} at port {}".format(device[1],port)
        return port
  if verbose : print "Arduboy not found."

def bootloaderStart():
  global bootloader
  ## find and connect to Arduboy in bootloader mode ##
  port = getComPort(True)
  if port is None : delayedExit()
  if not bootloader_active:
    print "Selecting bootloader mode..."
    bootloader = Serial(port,1200)
    bootloader.close()
    #wait for disconnect and reconnect in bootloader mode
    while getComPort(False) == port :
      time.sleep(0.1)
      if bootloader_active: break        
    while getComPort(False) is None : time.sleep(0.1)
    port = getComPort(True)
  
  time.sleep(0.1)	
  bootloader = Serial(port,57600)
  
def bootloaderExit():
  global bootloader
  bootloader.write("E")
  bootloader.read(1)
  
################################################################################

bootloaderStart()      
      
## Erase ##
print "\nErasing sketch startup page"
bootloader.write("A\x00\x00") #select page 0
bootloader.read(1)
bootloader.write("B\x00\x00F") #writing 0 length block will erase page only
bootloader.read(1)
bootloader.write("A\x00\x00") #select page 0
bootloader.read(1)
bootloader.write("g\x00\x80F")# read 128 byte page
if bytearray(bootloader.read(128)) == bytearray("\xff"* 128):
    print "\nErase successful"
else :
    print "\nErase failed"
bootloaderExit()      
delayedExit()