"""
Program to update a folder of ROMs (or any file) with identically named
replacements located in another folder. The purpose of this program was to
allow myself to update my curated lists of ROMs without a large amount of
manual work. The program also records a CSV file in the old ROM directory
with a list of all of the ROM filenames.
"""

# Liam Bates - January 31, 2019 (Python 3.7.2)

import sys
import os
import shutil
import csv

# Select the filetype for the ROMs
ROMTYPE = '.zip'

def check_dir(directory):
    """
    Function to verify that the directory path passed to it is valid, otherwise
    an error message is printed and the program is exited with error code 2.
    If the directory path is valid it is passed back.
    """
    if not os.path.isdir(directory):
        print('Error: ' + directory + ' is not a valid directory')
        sys.exit(2)
    else:
        return directory

def dir_to_list(directory, filetype):
    """
    Function to find a filetype in a directory and place the filename in a list
    that is returned.
    """
    filenamelist = []
    for file in os.listdir(directory):
        if file.endswith(filetype):
            filenamelist.append(file)
    return filenamelist


def match_rom(old_file_list, new_file_list):
    """
    Function to match ROM filenames in two lists of old ROMs and new ROMs.
    Returns a tuple of a list of matched filenames in both directories and an
    integer of unmatched old ROM errors respectively.
    """
    matches = []
    errors = 0

    for old_file in old_file_list:
        # Boolean to check whether a match has been found
        match = False
        # Iterate over the new files in the new file list
        for new_file in new_file_list:
            # Check if the old and new ROM filenames match
            if old_file == new_file:
                print('New ROM matched to Old ROM: ' + new_file)
                matches.append(new_file)
                match = True
        # If no match was found print an error message and add to error counter
        if not match:
            print('\x1b[0;49;91m', end='')
            print('Error! Unable to locate a New ROM: ' + old_file)
            print('\x1b[0m', end='')
            errors += 1
    return matches, errors

def copy_rom(match_file_list):
    """
    Function to take a list of matching ROM filenames in two directories (old
    ROMs and new ROMs) and copies these files.
    """
    copied = 0
    for match_file in match_file_list:
        shutil.copy(NEWDIR + '/' + match_file, OLDDIR + '/' + match_file)
        print('New ROM copied and replaced Old ROM: ' + match_file)
        copied += 1
    return copied

# Check if 2 arguments / paths were provided at command line
if len(sys.argv) != 3:
    print('Error! Usage: python rom_updater.py <Old ROMs Directory> <New ROMs Directory>')
    sys.exit(1)

# Store file path command line arguments as constants
OLDDIR = check_dir(sys.argv[1])
NEWDIR = check_dir(sys.argv[2])

# Call function to store all ROMs in the new and old directories in lists
OLDLIST = dir_to_list(OLDDIR, ROMTYPE)
NEWLIST = dir_to_list(NEWDIR, ROMTYPE)

# Create a CSV containing a list of all of the old ROM filenames
OUTPUTFILE = open(OLDDIR + '/oldlist.csv', 'w', newline='')
OUTPUTWRITER = csv.writer(OUTPUTFILE)
# Write each old ROM filename to a row in the CSV
for ROM in OLDLIST:
    OUTPUTWRITER.writerow([ROM])
# Close file
OUTPUTFILE.close()
print('oldlist.csv created in old ROM directory')

# Call function to show matches and errors
MATCHLIST, ERRORS = match_rom(OLDLIST, NEWLIST)

# Print summary of the ROM matching process. Show warning message if any unmatched
print('\n***Match Summary***')
print('Total New ROMs discovered:', len(NEWLIST))
print('Total Old ROMs discovered:', len(OLDLIST))
print('Total New ROMs matched to old ROMs:', len(MATCHLIST))
if ERRORS > 0:
    print('\x1b[0;49;91m', end='')
    print('WARNING!! Total Old ROMs unable to be matched:', ERRORS)
    print('\x1b[0m', end='')
else:
    print('Total Old ROMs unable to be matched:', ERRORS)

# Prompt user to confirm whether they would like to proceed to replacing ROMs
if input('\nWould you like to proceed to replacement (y/n)?').lower() == 'y':
    print('')
    # Call function to move matches from old directory to new directory
    COPIED = copy_rom(MATCHLIST)
    # Print summary of ROM replacement
    print('\n***Copy Summary***')
    print('Total New ROMs Matched and Copied:', COPIED)
    print('Total Old ROMs Unable to be matched:', ERRORS)
else:
    print('No changes made.')

# Exit with success code
sys.exit(0)
