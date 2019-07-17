print("\nArduboy Flashcart image builder v1.05 by Mr.Blinky Jun 2018 - Jul 2019\n")

# requires PILlow. Use 'python -m pip install pillow' to install

import sys
import time
import os
import csv
import math
try:
  from PIL import Image
except:
  print("The PILlow module is required but not installed!")
  print("Use 'python -m pip install pillow' from the commandline to install.")
  sys.exit()

ID_LIST  = 0
ID_TITLE = 1
ID_TITLESCREEN = 2
ID_HEXFILE = 3
ID_DATAFILE = 4
ID_SAVEFILE = 5

def DelayedExit():
    time.sleep(3)
    sys.exit()

def DefaultHeader():
    return bytearray("ARDUBOY".encode() + (b'\xFF' * 249))

def LoadTitleScreenData(filename):
    if not os.path.isabs(filename):
      filename = path + filename
    if not os.path.isfile(filename) :
        print("Error: Title screen '{}' not found.".format(filename))
        DelayedExit()
    img = Image.open(filename).convert("1")
    width, height  = img.size
    if (width != 128) or (height != 64) :
        print("Error: Title screen '{}' is not 128 x 64 pixels.".format(filename))
        DelayedExit()
    pixels = list(img.getdata())
    bytes = bytearray(int((height // 8) * width))
    i = 0
    b = 0
    for y in range (0,height,8):
        for x in range (0,width):
            for p in range (0,8):
                b = b >> 1  
                if pixels[(y + p) * width + x] > 0:
                    b |= 0x80
            bytes[i] = b
            i += 1
    return bytes
    
def LoadHexFileData(filename):
    if not os.path.isabs(filename):
      filename = path + filename
    if not os.path.isfile(filename) :
        return bytearray()
    f = open(filename,"r")
    records = f.readlines()
    f.close()
    bytes = bytearray(b'\xFF' * 32768)
    flash_end = 0
    for rcd in records :
        if rcd == ":00000001FF" : break
        if rcd[0] == ":" :
            rcd_len  = int(rcd[1:3],16)
            rcd_typ  = int(rcd[7:9],16)
            rcd_addr = int(rcd[3:7],16)
            rcd_sum  = int(rcd[9+rcd_len*2:11+rcd_len*2],16)
            if (rcd_typ == 0) and (rcd_len > 0) :
                flash_addr = rcd_addr
                checksum = rcd_sum
                for i in range(1,9+rcd_len*2, 2) :
                    byte = int(rcd[i:i+2],16)
                    checksum = (checksum + byte) & 0xFF
                    if i >= 9:
                        bytes[flash_addr] = byte
                        flash_addr += 1
                        if flash_addr > flash_end:
                            flash_end = flash_addr
                if checksum != 0 :
                    print("Error: Hex file '{}' contains errors.".format(filename))
                    DelayedExit()
    flash_end = int((flash_end + 255) / 256) * 256
    return bytes[0:flash_end]

def LoadDataFile(filename):
    if not os.path.isabs(filename):
      filename = path + filename
    if not os.path.isfile(filename) :
        return bytearray()

    with open(filename,"rb") as file:
        bytes = bytearray(file.read())
        pagealign = bytearray(b'\xFF' * (256 - len(bytes) % 256))
        return bytes + pagealign
        
################################################################################


if len(sys.argv) != 2 :
    print("\nUsage: {} flashcart-index.csv\n".format(os.path.basename(sys.argv[0])))
    DelayedExit()
    
previouspage = 0xFFFF    
currentpage = 0
nextpage = 0
csvfile = os.path.abspath(sys.argv[1])
path = os.path.dirname(csvfile)+os.sep
if not os.path.isfile(csvfile) :
    print("Error: CSV-file '{}' not found.".format(csvfile))
    DelayedExit()
TitleScreens = 0
Sketches = 0
filename = path + os.path.basename(csvfile).lower().replace("-index","").replace(".csv","-image.bin")
with open(filename,"wb") as binfile:
    with open(csvfile,"r") as file:
        data = csv.reader(file, quotechar='"', delimiter = ";")
        next(data,None)
        print("Building: {}\n".format(filename))
        print("List Title                     Curr. Prev. Next  ProgSize DataSize SaveSize")
        print("---- ------------------------- ----- ----- ----- -------- -------- --------")
        for row in data:
            while len(row) < 7: row.append('') #add missing cells
            header = DefaultHeader()
            title = LoadTitleScreenData(row[ID_TITLESCREEN])
            program = LoadHexFileData(row[ID_HEXFILE])
            programsize = len(program)
            datafile = LoadDataFile(row[ID_DATAFILE])
            datasize = len(datafile)
            slotsize = ((programsize + datasize) >> 8) + 5
            programpage = currentpage + 5
            datapage    = programpage + (programsize >> 8)
            nextpage += slotsize
            header[7] = int(row[ID_LIST]) #list number
            header[8] = previouspage >> 8
            header[9] = previouspage & 0xFF
            header[10] = nextpage >> 8
            header[11] = nextpage & 0xFF
            header[12] = slotsize >> 8
            header[13] = slotsize & 0xFF
            header[14] = programsize >> 7 #program size in 128 byte pages
            if programsize > 0:
                header[15] = programpage >> 8
                header[16] = programpage & 0xFF
                if datasize > 0:
                    program[0x14] = 0x18
                    program[0x15] = 0x95
                    program[0x16] = datapage >> 8
                    program[0x17] = datapage & 0xFF
            if datasize > 0:
                header[17] = datapage >> 8
                header[18] = datapage & 0xFF
            binfile.write(header)
            binfile.write(title)
            binfile.write(program)
            binfile.write(datafile)
            if programsize == 0:
              print("{:4} {:25} {:5} {:5} {:5}".format(row[ID_LIST],row[ID_TITLE],currentpage,previouspage,nextpage))
            else:
              print("{:4}  {:24} {:5} {:5} {:5} {:8} {:8} {:8}".format(row[ID_LIST],row[ID_TITLE][:24],currentpage,previouspage,nextpage,programsize,datasize,0))
            previouspage = currentpage
            currentpage = nextpage
            if programsize > 0:
                Sketches += 1
            else:
                TitleScreens += 1
        print("---- ------------------------- ----- ----- ----- -------- -------- --------")
        print("                                Page  Page  Page    Bytes    Bytes    Bytes")
                
print("\nImage build complete with {} Title screens, {} Sketches, {} Kbyte used.".format(TitleScreens,Sketches,(nextpage+3) / 4))
DelayedExit
