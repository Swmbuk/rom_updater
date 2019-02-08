#!/usr/bin/env python3
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
import difflib

# Select the filetype for the ROMs
ROMTYPE = '.zip'

def main():
    """
    Main script.
    """
    # Check if 2 arguments / paths were provided at command line
    if len(sys.argv) != 3:
        print('Error! Usage: python rom_updater.py <Old ROMs Directory> <New ROMs Directory>')
        sys.exit(1)

    # Store file path command line arguments as constants
    old_dir = check_dir(sys.argv[1])
    new_dir = check_dir(sys.argv[2])

    # Call function to store all ROMs in the new and old directories in lists
    old_list = dir_to_list(old_dir, ROMTYPE)
    new_list = dir_to_list(new_dir, ROMTYPE)

    # Create a CSV containing a list of all of the old ROM filenames
    with open(old_dir + '/oldlist.csv', 'w', newline='') as output_file:
        output_writer = csv.writer(output_file)
        # Write each old ROM filename to a row in the CSV
        for rom in old_list:
            output_writer.writerow([rom])
    print('oldlist.csv created in old ROM directory')

    # Call function to show matches and errors
    match_list, errors = match_rom(old_list, new_list)

    # Print summary of the ROM matching process. Show warning message if any unmatched
    print('\n***Match Summary***')
    print('Total New ROMs discovered:', len(new_list))
    print('Total Old ROMs discovered:', len(old_list))
    print('Total New ROMs matched to old ROMs:', len(match_list))
    if errors > 0:
        print('\x1b[0;49;91m', end='')
        print('WARNING!! Total Old ROMs unable to be matched:', errors)
        print('\x1b[0m', end='')
    else:
        print('Total Old ROMs unable to be matched:', errors)

    # Prompt user to confirm whether they would like to proceed to replacing ROMs
    if input('\nWould you like to proceed to replacement (y/n)?').lower() == 'y':
        print('')
        # Call function to move matches from old directory to new directory
        copied = copy_rom(match_list, old_dir, new_dir)
        # Print summary of ROM replacement
        print('\n***Copy Summary***')
        print('Total New ROMs Matched and Copied:', copied)
        print('Total Old ROMs Unable to be matched:', errors)
    else:
        print('No changes made.')

    # Exit with success code
    sys.exit(0)

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
        if file.endswith(filetype) and not file.startswith('.'):
            filenamelist.append(file)
    return sorted(filenamelist)

def match_rom(old_file_list, new_file_list):
    """
    Function to match ROM filenames in two lists of old ROMs and new ROMs.
    Returns a tuple of a list of matched filenames in both directories and an
    integer of unmatched old ROM errors respectively.
    """
    # list to store matched filenames and variable to store unmatched old ROMs
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
            # Find close filename matches (max of 3, min of 0)
            close = difflib.get_close_matches(old_file, new_file_list)
            if close:
                print(len(close), 'close filename/s found:')
                for closefiles in close:
                    print(closefiles)
            print('\x1b[0m', end='')
            errors += 1
    return matches, errors

def copy_rom(match_file_list, old_dir, new_dir):
    """
    Function to take a list of matching ROM filenames in two directories (old
    ROMs and new ROMs) and copies these files.
    """
    copied = 0
    for match_file in match_file_list:
        shutil.copy(new_dir + '/' + match_file, old_dir + '/' + match_file)
        print('New ROM copied and replaced Old ROM: ' + match_file)
        copied += 1
    return copied

if __name__ == "__main__":
    main()
