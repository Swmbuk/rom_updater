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


def match_copy(old_file_list, new_file_list, copy):
    """
    Function to match files in two lists. If the third argument is left False
    then the function will show matches only and count them. If True then the
    Function will copy the file from the new directory to the old directory
    """
    # list to monitor matches and errors respectively (e.g. item 0 - matches)
    matcherror = [0, 0]

    for old_file in old_file_list:
        # Boolean to check whether a match has been found
        match = False
        # Iterate over the new files in the new file list
        for new_file in new_file_list:
            # Check if the old and new ROM filenames match
            if old_file == new_file:
                if not copy:
                    print('New ROM matched to Old ROM: ' + new_file)
                else:
                    shutil.copy(NEWDIR + '/' + new_file, OLDDIR + '/' + old_file)
                    print('New ROM copied and replaced Old ROM: ' + new_file)
                matcherror[0] += 1
                match = True
        # If no match was found print an error message and add to error counter
        if not match:
            print('\x1b[0;49;91m', end='')
            print('Error! Unable to locate a New ROM: ' + old_file)
            print('\x1b[0m', end='')
            matcherror[1] += 1
    return matcherror

# Check if 2 arguments were provided at command line
if len(sys.argv) != 3:
    print('Error! Usage: python rom_updater.py <Old ROMs Directory> <New ROMs Directory>')
    sys.exit(1)

# Store command line arguments to constants
OLDDIR = sys.argv[1]
NEWDIR = sys.argv[2]

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

# Call function to show matches and errors
MATCHLIST = match_copy(OLDLIST, NEWLIST, False)

# Print summary of the ROM matching process. Show warning message if any unmatched
print('\n***Match Summary***')
print('Total New ROMs discovered:', len(NEWLIST))
print('Total Old ROMs discovered:', len(OLDLIST))
print('Total New ROMs matched to old ROMs:', MATCHLIST[0])
if MATCHLIST[1] > 0:
    print('\x1b[0;49;91m', end='')
    print('WARNING!! Total Old ROMs unable to be matched:', MATCHLIST[1])
    print('\x1b[0m', end='')
else:
    print('Total Old ROMs unable to be matched:', MATCHLIST[1])

# Prompt user to confirm whether they would like to proceed to replacing ROMs
if input('\nWould you like to proceed to replacement (y/n)?').lower() == 'y':
    print('')
    # Call function to move matches from old directory to new directory
    MATCHLIST = match_copy(OLDLIST, NEWLIST, True)
    # Print summary of ROM replacement
    print('\n***Copy Summary***')
    print('Total New ROMs Matched and Copied:', MATCHLIST[0])
    print('Total Old ROMs Unable to be matched:', MATCHLIST[1])
else:
    print('No changes made.')

# Exit with success code
sys.exit(0)
