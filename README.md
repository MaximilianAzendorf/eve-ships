# EVE Ship SVG Generation Script

This is a python script that generates black SVG silouhettes of EVE Online ships (or other models) based on the 3D models provided and extracted [here](https://github.com/Kyle-Cerniglia/EvE-3D-Printing).

Configuration of the script is done at the beginning of the file.

## Requirements

This script (propably) only works on Linux (or other UNIX systems). If you are on Windows, try the Linux Subsystem.

You need:

* Python 3
* Image Magick
* OpenSCAD

## How to

1. Clone the repository: 
   ```
   git clone --recursive https://github.com/MaximilianAzendorf/eve-ships
   ```

2. Check the scripts configuration at the start of the script.
3. Run it:
   ```
   ./generate.py
   ```


