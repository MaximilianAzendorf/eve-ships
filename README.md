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

## License

The script itself is licensed under the MIT license. Not however that the models used by this script (which are not part of this repository) are property of CCP.

---
### CCP Copyright Notice

EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. CCP is in no way responsible for the content on or functioning of this website, nor can it be liable for any damage arising from the use of this website.