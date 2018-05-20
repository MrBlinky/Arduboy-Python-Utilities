print "\nArduboy flash cart writer v1.0 by Mr.Blinky May 2018\n"

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
]

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

def getJedecID():
  bootloader.write("j")
  jedec_id = bootloader.read(3)
  time.sleep(0.5)  
  bootloader.write("j")
  jedec_id2 = bootloader.read(3)
  if jedec_id2 != jedec_id :
    print "No flash cart detected."
    delayedExit()
  return jedec_id
  
def bootloaderExit():
  global bootloader
  bootloader.write("E")
  bootloader.read(1)
  
################################################################################

if len(sys.argv) != 2 :
  print "\nUsage: {} flashimage.bin\n".format(os.path.basename(sys.argv[0]))
  delayedExit()
  
filename = sys.argv[1]
if not os.path.isfile(filename) :
  print "File not found. [{}]".format(filename)
  delayedExit()

print 'Reading flash image from file "{}"'.format(filename)
f = open(filename,"rb")
flashimage = bytearray(f.read())
f.close

if len(flashimage) % 256 != 0:
  print "File must contain a multiple of 256 bytes data\nWrite aborted!"
  delayedExit()
  
## detect flashcart ##
bootloaderStart()
jedec_id = getJedecID()
print "\nFlash cart JEDEC ID: {:02X}{:02X}{:02X}\n".format(ord(jedec_id[0]),ord(jedec_id[1]),ord(jedec_id[2]))

## flash cart ##
blocks = (len(flashimage) + BLOCKSIZE - 1) / BLOCKSIZE
lastblock = blocks - 1
for block in range (0,blocks):
  print "\rWriting block {} of {}".format(block + 1,blocks),
  if block == lastblock :
    blocklen = len(flashimage) - lastblock * BLOCKSIZE
    print "\n"
  else :
    blocklen = BLOCKSIZE
  bootloader.write("A")
  bootloader.write(chr(block >> 8))
  bootloader.write(chr(block & 0xFF))
  bootloader.read(1)
  bootloader.write("B")
  bootloader.write(chr(blocklen >> 8))
  bootloader.write(chr(blocklen & 0xFF))
  bootloader.write("C")
  bootloader.write(flashimage[block * BLOCKSIZE : block * BLOCKSIZE + blocklen])
  bootloader.read(1)
  
bootloaderExit()
print "Done"
delayedExit()