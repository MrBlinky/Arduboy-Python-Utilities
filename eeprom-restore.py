#!/usr/bin/env python3
print("\nArduboy EEPROM restore v1.0 by Mr.Blinky April 2018")

#requires pyserial to be installed. Use "pip install pyserial" on commandline

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
 #Adafruit ItsyBitsy 5V
 "VID:PID=239A:000E", "VID:PID=239A:800E",
]

bootloader_active = False

def delayedExit():
  time.sleep(2)
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
        if verbose : print("Found {} at port {}".format(device[1],port))
        return port
  if verbose : print("Arduboy not found.")

def bootloaderStart():
  global bootloader
  ## find and connect to Arduboy in bootloader mode ##
  port = getComPort(True)
  if port is None : delayedExit()
  if not bootloader_active:
    print("Selecting bootloader mode...")
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
  bootloader.write(b"E")
  bootloader.read(1)

################################################################################

if len(sys.argv) != 2 :
  print("\nUsage: {} eepromfile.bin\n".format(os.path.basename(sys.argv[0])))
  delayedExit()

filename = sys.argv[1]
if not os.path.isfile(filename) :
  print("File not found. [{}]".format(filename))
  delayedExit()

print('Reading EEPROM data from file "{}"'.format(filename))
f = open(filename,"rb")
eepromdata = bytearray(f.read())
f.close

if len(eepromdata) != 1024:
  print("File does not contain 1K (1024 bytes) of EEPROM data\nRestore aborted")
  delayedExit()

## restore ##
bootloaderStart()
print("Restoring EEPROM data...")
bootloader.write(b"A\x00\x00")
bootloader.read(1)
bootloader.write(b"B\x04\x00E")
bootloader.write(eepromdata)
bootloader.read(1)
bootloaderExit()
print("Done")
delayedExit()
