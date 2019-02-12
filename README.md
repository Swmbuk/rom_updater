# rom_updater

Command line tool to copy ROMs from an updated romset using either an existing target directory of curated ROMs or a CSV file.

## Summary

I created the tool to make the task of updating ROM files in my RetroPie setup easier. Personally I prefer to only keep my favorite ROMs together as opposed to storing every ROM from a full romset and having to scroll through a lot of bloat.

This creates a problem when you wish to update your ROM set as you will need to manually curate the ROMs again. This tool therefore takes your existing ROM filenames in a directory and uses this to find replacements in a new source directory of a full new romset.

As ROMs frequently change names the tool will attempt to find similarly named ROMs in the new source romset directory and outline close suggestions it has found. You may then choose to select a suggestion or skip the ROM. This option may be turned off if it is undesirable.

The tool can also take a CSV file of ROM filenames as opposed to searching an existing target directory of ROM filenames. This is useful for backup purposes or sharing curated lists.

The tool will also create CSV files for the original target directory ROM filenames, matched ROM filenames and unmatched ROM filenames.

## Usage

The tool was created for Python 3 and can take a number of arguments at the command line:

Usage: ```python3 rom_updater.py [-h] [-ns] [-c CSV] source target```

### Mandatory arguments

* ```source``` Source directory of new ROMs.
* ```target``` Destination directory where ROMs will be matched and transferred to unless a CSV file is loaded. ROMs in this directory will be overwritten by matches in the source directory.

### Optional arguments

* ```-h``` Show help message
* ```-ns``` Disable similar ROM filename suggestion function.
* ```-c``` CSV of ROM filenames to be transferred from the source to the target directory. One filename per row in a single column.

When running the tool it will search to ensure a match is found using the filename of each ROM or suggest a similar filename. Once the matching process has concluded you will be prompt if you wish to proceed with the replacement process, whereby the original ROMs in the target directory will be replaced.

Throughout the process the tool will create CSVs in the target directory showing the original ROM filenames, matched filenames and unmatched filenames.

### Considerations

* Be careful! This tool will replace any files listed in the original target directory with those with the identical filename located in the new source directory. Remember to backup any files you care about.
* The tool is set to only match and replace .zip ROMs. You can update the tool on line 19 to work with other file extensions.
* The tool was created with the presumption that you will be using matching romsets, which typically have identical or similar filenames.
* As of the time of writing I am new to development and there may be some inefficiencies in the code. I will periodically come back and update the tool as I learn more. Feel free to make any suggestions!
