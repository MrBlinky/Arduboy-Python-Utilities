# Python utilities for Arduboy

For Windows, Linux and OSX

### Dependencies

* Requires Python 2.7.x with PySerial installed

## Uploader

.Hex file and .Arduboy uploader for Arduboy

### Features

* Supports uploading to Arduboy, DevKit, and homemade Arduboys
* Uploads .hex files, .hex files in .zip and .arduboy files
* Protects unprotected bootloaders from being overwritten by large hex files
* Supports on the fly patching for SSD1309 displays
* Supports on the fly RX and TX LED polarity patching for Arduino /Genuino Micro

### Usage:

* Right click a .hex file, .arduboy file or .zip file containing a hex file
  and choose *Send To* Arduboy uploader
* Drag and drop .hex, .zip or .arduboy files on the **uploader.py** file
* Command line: uploader.py [filetoupload]

### Install

* Download and install python 2.7.x from https://www.python.org/downloads/ if it is not already installed
* Make sure the option 'Add python.exe to path' is checked on install options (Windows)
* After install run 'python -m pip install pyserial' from command line. For OSX run 'easy_install pyserial' from terminal.
* Double click the **uploader-create-send-to-shortcut.vbs** (Windows only)

## SSD1309 display support

To patch Arduboy hex files for use on Homemade Arduboys with SSD1309 displays,
make a copy of **uploader.py** and rename it to **uploader-1309.py** Also make
sure you run the **uploader-create-send-to-shortcut.vbs** again to create a
**Send To** shortcut for it. Files will be patched on fly, original files will not be altered.

## reverse RX and TX LED polarity support

To patch Arduboy hex files for use with Homemade Arduboys based on Arduino / Genuino Micro,
make a copy of **uploader.py** and rename it to **uploader-micro.py** and run the
**uploader-create-send-to-shortcut.vbs** again to create a **Send To** shortcut for it.

## EEPROM backup

You can backup your Arduboys EEPROM by double clicking the **eeprom-backup.py**  python script.
The backup is saved to a time stamped file in the format **eeprom-backup.py-YYYYMMDD-HHMMSS.bin**

## EEPROM restore

You can restore a previously made EEPROM backup simply by dragging the **eeprom-backup.py-YYYYMMDD-HHMMSS.bin** file onto the **eeprom-restore.py** python script

## EEPROM erase

Erases the EEPROM content (An erased EEPROM contains all 0xFF's).

## Erase sketch

Erases the application/sketch startup page to keep the bootloader mode active indefinitely. This solves problematic (time sensitive) uploads using Arduino IDE.

## Flash cart writer

Writes a binary flash image to a flash cart connected to (a modified) Arduboy with expansion connector (Cathy3K v1.3 bootloader required). make a copy of **flashcart-writer.py** and rename it to **flashcart-writer-1309.py** to Apply SSD1309 patch to the 
