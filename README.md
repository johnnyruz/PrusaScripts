# PrusaScripts
Collection of Post-Processor Scripts for Prusa GCode


## Post Process MMU Temp Fix
This script searches through GCODE files generate for the Prusa MMU and locates any temperature changes that occur between filament changes. It then moves these temperature commands after any cooling moves take place.

**Background**

PrusaSlicer (from 2.0.0 up to at least 2.9.7) performs the temperature change before any cooling moves take place. This causes issues as the hotend will heat up or cool down while the previous filament is still in the chamber. My fix for this is to edit the GCODE to request the temperature change after all cooling moves just before the current filament is extracted from the hot end. Ususally there is still plenty of time to get the hotend to the desired temperature (or very close) by the time the MMU loads the next filament to the hotend.

**Details**

The script works on each toolchange block, from the `; CP TOOLCHANGE UNLOAD` marker (or, for older GCODE without the marker, from an M104 that directly follows a retract `G1 E-...`) to the `T<n>` command. It moves every M104 of the block right after the last G4 command of the block, which is the configured delay to wait before unloading (usually 0). Blocks with no G4 after the M104 are left unchanged.

PrusaSlicer 2.9.7 emits the M104 after a `G4 S0` that follows the ramming, not right after the retract, so the previous version of this script left the GCODE unchanged.

**Usage**

Python 3 is required. In PrusaSlicer, Print Settings > Output options > Post-processing scripts:
```
/usr/bin/env python3 /path/to/postprocess_mmutempchange.py;
```
The GCODE file is edited in place.

Therefore this:
```
G1 E-15.0000 F6000
G1 E-24.5000 F1200
G1 E-7.0000 F600
G1 E-3.5000 F360
M104 S200 ;TEMP CHANGE
G1 Y144.940 ;START OF COOLING MOVES
G1 X229.250 E20.0000 F488
G1 X178.820 E-20.0000 F434
G1 X229.250 E20.0000 F380
G1 X178.820 E-20.0000 F326
G1 E-35.0000 F2000
G1 Y144.800 F2400
G4 S0 ;DELAY 0s
T4 ;CHANGE TO EXTRUDER #4
```

Would become:
```
G1 E-15.0000 F6000
G1 E-24.5000 F1200
G1 E-7.0000 F600
G1 E-3.5000 F360
G1 Y144.940 ;START OF COOLING MOVES
G1 X229.250 E20.0000 F488
G1 X178.820 E-20.0000 F434
G1 X229.250 E20.0000 F380
G1 X178.820 E-20.0000 F326
G1 E-35.0000 F2000
G1 Y144.800 F2400
G4 S0 ;DELAY 0s
M104 S200 ;TEMP CHANGE
T4 ;CHANGE TO EXTRUDER #4
```
