#!/usr/bin/python
import sys
import re
import os

sourceFile=sys.argv[1]
previousLine = ""
tempLine = ""

# Read the ENTIRE g-code file into memory
with open(sourceFile, "r") as f:
    lines = f.readlines()

destFile = re.sub('\.gcode$','',sourceFile)
#os.rename(sourceFile,destFile+"_tempfix.bak")
destFile = re.sub('\.gcode$','',sourceFile)
destFile = destFile + '.gcode'

with open(destFile, "w") as of:
    for lIndex in xrange(len(lines)):
        oline = lines[lIndex]
        if oline[:4] == "M104":
           if previousLine[:5] == "G1 E-":
              tempLine = oline
           else:
               of.write(oline)
        elif oline[:5] == "G4 S0":
            of.write(oline)
            of.write(tempLine)
            tempLine = ""
        else:
            of.write(oline)
        
        previousLine = oline

of.close()
f.close()