#!/usr/bin/env python

from pathlib import Path
from shutil import copyfile
import subprocess
import tempfile
import math
import json
import re
import os

RESOLUTION = 5000
OUT_DIR = "output"

subdirs = [
    "amarr/.+", 
    "ore/.+", 
    "caldari/.+", 
    "gallente/.+", 
    "minmatar/.+", 
    "triglavian/.+",
    "pirate/angel cartel/.+",
    "pirate/blood raiders/.+",
    "pirate/mordus legion/.+",
    "pirate/sanshas nation/.+",
    "pirate/soct/.+",
    "pirate/soe/.+",
    "special_edition/zephyr"]

blacklist = [
    "af8_t1",
    "mf4_t2c",
    ".+_old",
]

#######################################################################

tempPng = OUT_DIR + "/.temp"
tempScad = OUT_DIR + "/.temp"
orientation = json.loads(open("orientation.json", 'r').read())

def num(s):
    try:
        try:
            return int(s)
        except ValueError:
            return float(s)
    except ValueError:
        return s

def openscad(shipkey, res, dist, infile, outfile):
    file = open(tempScad + ".scad", "w")
    file.write(f"import(\"{infile}\");")
    file.close()

    cmd = ["openscad", 
        f"--camera=0,0,0,{orientation[shipkey]},{dist}", 
        f"--imgsize={res},{res}", 
        "--projection=o",
        "-o", outfile + ".png",
        tempScad + ".scad"
    ]

    subprocess.run(cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL,
    )

def getstdout(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('UTF-8')

def im_convert(cmd):
    return num(getstdout(["convert"] + cmd))

def im_identify(cmd):
    return num(getstdout(["identify"] + cmd))

def finddist(shipkey, infile):
    resolution = 64
    dist = 1
    distf = 1.35
    cont = True
    w = 64
    h = 64

    while cont:
        openscad(shipkey, resolution, dist, infile, tempPng)
        left = im_convert([f"{tempPng}.png[1x{h}+0+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
        top = im_convert([f"{tempPng}.png[{w}x1+0+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
        right = im_convert([f"{tempPng}.png[1x{h}+{w-1}+0]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
        bottom = im_convert([f"{tempPng}.png[{w}x1+0+{h-1}]", "-scale", "1x1!", "-format", "%[fx:u]", "info:"])
        colors = im_identify(["-format", "%k", tempPng + ".png"])

        border = left + top + right + bottom
        print("  (scale) dist=" + str(dist) + " gives a border of " + str(border) + ", k=" + str(colors))
        cont = border < 3.97056 or colors <= 1
        if cont:
            dist = math.ceil(dist * distf)

    print("  (scale) using dist=" + str(dist))
    return dist


if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

positive = '|'.join((".*" + x + "\\.stl") for x in subdirs)
negative = '|'.join(("^" + x + "$") for x in blacklist)

paths = []

for path in Path('./models/ships/').rglob('*.stl'):
    filename = str(path.stem)
    fullpath = str(path.resolve())
    if not re.match(positive, fullpath) or re.match(negative, filename):
        continue
    paths.append(path)

for i in range(len(paths)):
    path = paths[i]
    filename = str(path.stem)
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
    copyfile(outfile + ".svg", outfile + "_64x64.svg")
    subprocess.run(["sed", "-i" ,"-E", "s/(width|height)=\"[^\"]+\"/\\1=\"64px\"/g", outfile + "_64x64.svg"])
    subprocess.run(["sed", "-i" ,"-E", "s/fill=\"[^\"]*\"//g", outfile + "_64x64.svg"])
