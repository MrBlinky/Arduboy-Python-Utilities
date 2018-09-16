print("\nArduboy flash cart backup v1.12 by Mr.Blinky May-Sep. 2018\n")

#requires pyserial to be installed. Use "python -m pip install pyserial" on commandline

import sys
import time
import os
from serial.tools.list_ports import comports
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

manufacturers = {
  0x01 : "Spansion",
  0x14 : "Cypress",
  0x1C : "EON",
  0x1F : "Adesto(Atmel)",
  0x20 : "Micron",
  0x37 : "AMIC",
  0x9D : "ISSI",
  0xC2 : "General Plus",
  0xC8 : "Giga Device",
  0xBF : "Microchip",
  0xEF : "Winbond"
}

PAGESIZE = 256
BLOCKSIZE = 4096
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
  
def getVersion():
  bootloader.write("V".encode())
  return int(bootloader.read(2))

def getJedecID():
  bootloader.write("j".encode())
  jedec_id = bootloader.read(3)
  time.sleep(0.5)  
  bootloader.write("j".encode())
  jedec_id2 = bootloader.read(3)
  if jedec_id2 != jedec_id :
    print("No flash cart detected.")
    delayedExit()
  return bytearray(jedec_id)
  
def bootloaderExit():
  global bootloader
  bootloader.write("E".encode())
  bootloader.read(1)
  
################################################################################
 
bootloaderStart()

#check version
if getVersion() < 13:
  print("Bootloader has no flash cart support\nWrite aborted!")
  delayedExit()

## detect flash cart ##
jedec_id = getJedecID()
if jedec_id[0] in manufacturers.keys():
  manufacturer = manufacturers[jedec_id[0]]
else:
  manufacturer = "unknown"
capacity = 1 << jedec_id[2]
print("\nFlash cart JEDEC ID    : {:02X}{:02X}{:02X}".format(jedec_id[0],jedec_id[1],jedec_id[2]))
print("Flash cart Manufacturer: {}".format(manufacturer))
print("Flash cart capacity    : {} Kbyte\n".format(capacity // 1024))

filename = time.strftime("flashcart-backup-image-%Y%m%d-%H%M%S.bin", time.localtime())
print('Writing flash image to file: "{}"\n'.format(filename))

oldtime=time.time()
blocks = capacity // BLOCKSIZE
with open(filename,"wb") as binfile:
  for block in range (0, blocks):

    sys.stdout.write("\rReading block {}/{}".format(block + 1,blocks))

    blockaddr = block * BLOCKSIZE // PAGESIZE

    bootloader.write("A".encode())
    bootloader.write(bytearray([blockaddr >> 8, blockaddr & 0xFF]))
    bootloader.read(1)

    blocklen = BLOCKSIZE

    bootloader.write("g".encode())
    bootloader.write(bytearray([blocklen >> 8, blocklen & 0xFF]))

    bootloader.write("C".encode())
    contents=bootloader.read(blocklen)
    binfile.write(contents)

bootloaderExit()
print("\n\nDone in {} seconds".format(round(time.time() - oldtime,2)))
delayedExit()
