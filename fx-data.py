#FX data make tool version 1.00 by Mr.Blinky May2021 

VERSION = '1.00'

import sys
import os
import time
import re

bytes = bytearray()
symbols = []
label = ''
blkcom = False

try: 
  from PIL import Image
except:
  print("The PILlow module is not installed.")
  delayedExit(("type 'python -m pip install pillow' on commandline to install"))

def delayedExit(msg):
  print(msg)
  time.sleep(3)
  sys.exit()

def rawData(filename):
  global path
  with open(path + filename,"rb") as file:
    bytes = bytearray(file.read())
    file.close()
    return bytes
  
def imageData(filename):
  global path
  filename = path + filename
  
  ## parse filename ## FILENAME_[WxH]_[S].[EXT]"
  spriteWidth = 0
  spriteHeight = 0
  spacing = 0  
  elements = os.path.basename(os.path.splitext(filename)[0]).split("_")
  lastElement = len(elements)-1
  #get width and height from filename
  i = lastElement
  while i > 0:
    if "x" in elements[i]:
      spriteWidth = int(elements[i].split("x")[0])
      spriteHeight = int(elements[i].split("x")[1])
      if i < lastElement:
        spacing = int(elements[i+1])
      break
    else: i -= 1  
  else:
    i = lastElement
  #get sprite name (may contain underscores) from filename
  name = elements[0]
  for j in range(1,i):
    name += "_" + elements[j] 
  spriteName = name.replace("-","_")
  #load image
  img = Image.open(filename).convert("RGBA")
  pixels = list(img.getdata())
  #check for transparency
  transparency = False
  for i in pixels:
   if i[3] < 255:
    transparency = True
    break
  
  # check for multiple frames/tiles
  if spriteWidth > 0:
    hframes = (img.size[0] - spacing) // (spriteWidth + spacing)
  else:
    spriteWidth = img.size[0] - 2 * spacing 
    hframes = 1
  if spriteHeight > 0:
    vframes = (img.size[1] - spacing) // (spriteHeight + spacing)
  else:
    spriteHeight = img.size[1] - 2* spacing
    vframes = 1
  
  #create byte array for bin file
  size = (spriteHeight+7) // 8 * spriteWidth * hframes * vframes
  if transparency:
    size += size
  bytes = bytearray([spriteWidth >> 8, spriteWidth & 0xFF, spriteHeight >> 8, spriteHeight & 0xFF])
  bytes += bytearray(size)
  i = 4
  b = 0
  m = 0
  #headerfile.write("constexpr uint8_t {}Width = {};\n".format(spriteName, spriteWidth))
  #headerfile.write("constexpr uint8_t {}Height = {};\n".format(spriteName,spriteHeight))
  fy = spacing
  frames = 0
  for v in range(vframes):
    fx = spacing
    for h in range(hframes):
      for y in range (0,spriteHeight,8):
        line = "  "
        for x in range (0,spriteWidth):
          for p in range (0,8):
            b = b >> 1  
            m = m >> 1
            if (y + p) < spriteHeight: #for heights that are not a multiple of 8 pixels
              if pixels[(fy + y + p) * img.size[0] + fx + x][1] > 64:
                b |= 0x80 #white pixel
              if pixels[(fy + y + p) * img.size[0] + fx + x][3] > 64:
                m |= 0x80 #opaque pixel
              else:
                b &= 0x7F #for transparent pixel clear possible white pixel 
          bytes[i] = b
          i += 1
          if transparency:
            bytes[i] = m 
            i += 1
      frames += 1  
      fx += spriteWidth + spacing
    fy += spriteHeight + spacing
  return bytes  

################################################################################

if len(sys.argv) != 2 :
  DelayedExit("\nUsage: {} flashcart-index.csv\n".format(os.path.basename(sys.argv[0])))

filename = os.path.abspath(sys.argv[1])
path = os.path.dirname(filename)+os.sep

with open(filename,"r") as file:
  lines = file.readlines()
  file.close()

for lineNr in range(len(lines)):
  parts = [p for p in re.split("( |[\\\"'].*[\\\"'])", lines[lineNr]) if p.strip()]
  for i in range (len(parts)):
    part = parts[i]
    #strip unwanted chars
    if part[:1]  == '\t' : part = part[1:]
    if part[:1]  == '{' : part = part[1:]
    if part[-1:] == '\n': part = part[:-1]
    if part[-1:] == ';' : part = part[:-1]
    if part[-1:] == '}' : part = part[:-1]
    if part[-1:] == ';' : part = part[:-1]
    if part[-1:] == ',' : part = part[:-1]
    if part[-2:] == '[]': part = part[:-2]
    #handle comments
    if blkcom == True:
      p = part.find('*/',2)
      if p >= 0:
        part = part[p+2:]
        blkcom = False
    else:
      if   part[:2] == '//':
        break
      elif part[:2] == '/*':
        p = part.find('*/',2)
        if p >= 0: part = part[p+2:]
        else: blkcom = True;
      #handle types
      elif part == 'int8_t'  : t = 1
      elif part == 'uint8_t' : t = 1
      elif part == 'int16_t' : t = 2
      elif part == 'uint16_t': t = 2
      elif part == 'int24_t' : t = 3
      elif part == 'uint24_t': t = 3
      elif part == 'int32_t' : t = 4
      elif part == 'uint32_t': t = 4
      elif part == 'image_t' : t = 5
      elif part == 'raw_t'   : t = 6
      #handle labels
      elif (part == '=') and (label !='') : 
        symbols.append((label,len(bytes)))
        label =''
      #handle strings  
      elif (part[:1] == "'") or (part[:1] == '"'):
        if  part[:1] == "'": part = part[1:part.rfind("'")]
        else:  part = part[1:part.rfind('"')]
        if   t == 1: bytes += part.encode()
        elif t == 5: bytes += imageData(part)
        elif t == 6: bytes += rawData(part)
        else:
          delayedExit('ERROR in line {}: unsupported string for type'.format(lineNr))
      #handle values
      elif part[:1].isnumeric():
        n = int(part,0)
        bytes.append((n >> 0) & 0xFF)    
        if t == 2: bytes.append((n >> 8) & 0xFF)    
        if t == 3: bytes.append((n >> 16) & 0xFF)    
        if t == 4: bytes.append((n >> 24) & 0xFF)    
      #handlelabels
      elif part[:1].isalpha():
        for j in range(len(part)):  
          if part[j] == '=':
            symbols.append((label,len(bytes)))
            label = ''
            part = part[j+1:]
            parts.insert(i+1,part)
            break
          elif part[j].isalnum() or part[j] == '_':
            label += part[j]
          else:
            delayedExit('ERROR in line {}: Bad label: {}'.format(lineNr,label))
      elif len(part) > 0: 
        delayedExit('ERROR unable to parse {} in element: {}'.format(part,str(parts)))
        
with open(os.path.splitext(filename)[0] + '.bin',"wb") as file:
  file.write(bytes)
  file.close()

with open(os.path.splitext(filename)[0] + '.h',"w") as file:
  file.write('#pragma once\n\n')
  file.write('/**** FX data header generated by fx-data.py tool version {} ****/\n\n'.format(VERSION))
  file.write('using uint24_t = __uint24;\n\n')
  file.write('// Initialize FX hardware using  FX::begin(FX_DATA_PAGE); in the setup() function.\n\n')
  file.write('constexpr uint16_t FX_DATA_PAGE  = 0x{:04x};\n'.format(65536 - (len(bytes) + 255) // 256 ))
  file.write('constexpr uint24_t FX_DATA_BYTES = {};\n\n'.format(len(bytes)))
  for symbol in symbols:
    file.write('constexpr uint24_t {} = 0x{:06X};\n'.format(symbol[0],symbol[1]))
  file.close()
