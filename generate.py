#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2021 Maximilian Azendorf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# The resolution at which the models will be rendered; not recommended to change that.
RESOLUTION = 5000

# The output directory names
OUT_DIR = "output"
OUT_DIR_FULL = OUT_DIR + "/full"
OUT_DIR_X64 = OUT_DIR + "/x64"

# The script will render all STL files that match one of the regular expressions in the 
# subdirs list EXCEPT the ones that also match the regular expressions in the blacklist 
# list.
subdirs = [
    "ships/amarr/.+", 
    "ships/ore/.+", 
    "ships/caldari/.+", 
    "ships/gallente/.+", 
    "ships/minmatar/.+", 

    "ships/triglavian/.+",
    "ships/upwell/.+",
    "ships/concord/.+",

    "ships/pirate/angel cartel/.+",
    "ships/pirate/blood raiders/.+",
    "ships/pirate/mordus legion/.+",
    "ships/pirate/sanshas nation/.+",
    "ships/pirate/soct/.+",
    "ships/pirate/soe/.+",

    "ships/special_edition/zephyr",
    ]

blacklist = [
    "af8_t1",
    "mf4_t2c",
    ".+_old",
    ".+ \\(old\\)",
]

###########################################################################################

from pathlib import Path
from shutil import copyfile
import contextlib
import subprocess
import tempfile
import math
import json
import re
import os

tempPng = OUT_DIR + "/.temp"
tempScad = OUT_DIR + "/.temp"
orientation = json.loads(open("orientation.json", 'r').read())
warned_about = set()


# Convert a number string to an int or a float.
def num(s):
    try:
        try:
            return int(s)
        except ValueError:
            return float(s)
    except ValueError:
        return s


# Invoke openscad with the given resolution, orientation and distance. Input file is infile, 
# output file is outfile.
def openscad(shipkey, res, dist, infile, outfile):
    file = open(tempScad + ".scad", "w")
    file.write(f"import(\"{infile}\");")
    file.close()

    orientation_str = orientation.get(shipkey)
    if orientation_str is None:
        if shipkey not in warned_about:
            print(f"  WARNING: No orientation given for the model '{shipkey}'. Consider adding it to orientation.json.")
            warned_about.add(shipkey)
        orientation_str = "90,-90,-90"

    cmd = ["openscad", 
        f"--camera=0,0,0,{orientation_str},{dist}", 
        f"--imgsize={res},{res}", 
        "--projection=o",
        "-o", outfile + ".png",
        tempScad + ".scad"
    ]

    subprocess.run(cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
    )


# Runs the given command and returns its stdout.
def getstdout(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('UTF-8')


# Runs convert (from image magick) and returns the number it printed.
def im_convert(cmd):
    return num(getstdout(["convert"] + cmd))


# Runs identify (from image magick) and returns the number it printed.
def im_identify(cmd):
    return num(getstdout(["identify"] + cmd))


def getborder(shipkey, dist, infile):
    resolution = 64
    w = resolution
    h = resolution

    openscad(shipkey, resolution, dist, infile, tempPng)
    left = im_convert([f"{tempPng}.png[1x{h}+0+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
    top = im_convert([f"{tempPng}.png[{w}x1+0+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
    right = im_convert([f"{tempPng}.png[1x{h}+{w-1}+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
    bottom = im_convert([f"{tempPng}.png[{w}x1+0+{h-1}]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])

    colors = im_identify(["-format", "%k", tempPng + ".png"])
    border = left + top + right + bottom

    return border, colors

# Finds the appropriate distance for the given file.
def finddist(shipkey, infile):
    mind = 0.0
    maxd = 2.0
    maxdev = 0.1

    dist = maxd
    startmax = maxd
    while (maxd - mind) / dist > maxdev:
        dist = (maxd + mind) / 2
        border, colors = getborder(shipkey, dist, infile)        
        bad = border < 3.97056 or colors <= 1

        print(f"  (scale) dist={dist:.3f} gives a border of {border}, k={colors} ({'+' if not bad else '-'} {(maxd - mind) / dist:.2f})")
        if not bad:
            maxd = dist
        else:
            mind = dist
            if maxd == startmax:
                mind = 0.0
                maxd *= 5
                startmax = maxd

    print("  (scale) using dist=" + str(maxd))
    return maxd


if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)
if not os.path.exists(OUT_DIR_FULL):
    os.mkdir(OUT_DIR_FULL)    
if not os.path.exists(OUT_DIR_X64):
    os.mkdir(OUT_DIR_X64)

positive = '|'.join((".*" + x + "\\.stl") for x in subdirs)
negative = '|'.join(("^" + x + "$") for x in blacklist)

paths = []

for path in Path('./models/').rglob('*.stl'):
    filename = str(path.stem)
    fullpath = str(path.resolve())
    if not re.match(positive, fullpath) or re.match(negative, filename):
        continue
    paths.append(path)

if len(paths) == 0:
    print("No models to render. Check if the models subdirectory is not empty and that subdirs actually matches something.")

for i in range(len(paths)):
    path = paths[i]
    filename = str(path.stem).replace("_final", "")
    fullpath = str(path.resolve())
    print(f"({i+1}/{len(paths)}) Rendering {fullpath}...")
    dist = finddist(filename, fullpath)

    outfile =  OUT_DIR + "/" + filename
    openscad(filename, RESOLUTION, dist, fullpath, outfile)
    im_convert([outfile + ".png", 
        "-trim", 
        "-fx", "(r+g+b)/3",
        "-normalize", 
        outfile + ".pnm"])
    os.remove(outfile + ".png")
    subprocess.run(["potrace", "-s", "-k", "0.99", outfile + ".pnm"])
    os.remove(outfile + ".pnm")

    fullSvgFile = OUT_DIR_FULL + "/" + filename + ".svg"
    x64SvgFile = OUT_DIR_X64 + "/" + filename + ".svg"
    copyfile(outfile + ".svg", fullSvgFile)
    copyfile(outfile + ".svg", x64SvgFile)
    os.remove(outfile + ".svg")

    subprocess.run(["sed", "-i" ,"-E", "s/(width|height)=\"[^\"]+\"//g", fullSvgFile])
    subprocess.run(["sed", "-i" ,"-E", "s/(width|height)=\"[^\"]+\"/\\1=\"64px\"/g", x64SvgFile])
    subprocess.run(["sed", "-i" ,"-E", "s/fill=\"[^\"]*\"//g", x64SvgFile])

with contextlib.suppress(FileNotFoundError):
    os.remove(tempPng + ".png")
with contextlib.suppress(FileNotFoundError):
    os.remove(tempScad + ".scad")