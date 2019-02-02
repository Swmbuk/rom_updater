# rom_updater
Command line script to replace curated folders of ROM files and save the lists
as CSVs.

### Summary

I created the script to make the task of updating ROM files in my RetroPie setup
easier. Personally I prefer to only keep my favorite ROMs together as opposed to
storing every ROM from a set and having to scroll through a lot of bloat.

This creates a problem when you wish to update your ROM set as you will need to
manually curate the ROMs again. This script therefore takes your old ROMs in a
directory and uses this to find replacements in a new directory of a full new ROM
set.

### Usage

The script was created for Python 3 and should be used to point to two directories:

* Original ROMs directory
* New ROMs (presumably an entire new ROM set) directory

Usage: ``` python rom_updater.py [Original ROMs] [New ROMS]```

When running the script it will search to ensure a match is found using the filename
of each ROM. Once concluded it will inform you of the ROMs matched and those it
was unable to find in the new ROM directory. If you wish to proceed with the
replacement process you will then need to confirm.

Additionally the script creates a CSV file with a list of all of the original ROM
filenames to act as a backup for your collection.

### Considerations

* Be careful! This script will replace any files listed in the original directory with those with the identical filename located in the new directory
* The script is set to only match and replace .zip files. You can update the script on line 17 to work with other file extensions.
* The script was created with the presumption that you will be using matching ROM sets, which typically have identical file names. Occasionally ROM sets update some filenames, which will require reading of the script readout and a couple manual movements of ROMs.
