# Python .Hex file and .Arduboy uploader for Arduboy

### Features

* Supports uploading to Arduboy, DevKit, and homemade Arduboys
* Uploads .hex files, .hex files in .zip and .arduboy files
* Protects unprotected bootloaders from being overwritten by large hex files
* Supports on the fly patching for SSD1309 displays

### Usage:

* Right click a .hex file, .arduboy file or .zip file containing a hex file
  and choose *Send To* Arduboy uploader
* Drag and drop .hex, .zip or .arduboy files on the **uploader.py** file
* Command line: uploader.py [filetoupload]

### Dependencies

* Requires Python 2.7.x with PySerial installed
* Windows or linux

### Install

* Download and install python 2.7.x from https://www.python.org/downloads/ if it is not already installed
* Make sure the option 'Add python.exe to path' is checked on install options
* After install run 'pip install pyserial' from command line.
* Double click the **uploader-create-send-to-shortcut.vbs**

## SSD1309 display support

To patch Arduboy hex files for use on Homemade Arduboys with SSD1309 displays,
make a copy of **uploader.py** and rename it to **uploader-1309.py** Also make
sure you run the **uploader-create-send-to-shortcut.vbs** again to create a
**Send To** shortcut for it. Files will be patched on fly, original files will not be altered.

## EEPROM backup

You can backup your Arduboys EEPROM by double clicking the **eeprom-backup.py**  python script.
The backup is saved to a time stamped file in the format **eeprom-backup.py-YYYYMMDD-HHMMSS.bin**

## EEPROM restore

You can restore a previously made EEPROM backup simply by dragging the **eeprom-backup.py-YYYYMMDD-HHMMSS.bin** file onto the **eeprom-restore.py** python script
