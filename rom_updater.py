#!/usr/bin/env python3
"""
Tool to match and copy select ROMs from a new romset using either an existing destination directory
of old ROMs or a CSV file of ROM filenames. Filenames are used to match ROMs and similar filename
matches are sought when a perfect match cannot be obtained.
"""

# Liam Bates - January 31, 2019 (Python 3.7.2)

import sys
import os
import shutil
import csv
import difflib
import argparse


# Select the filetype for the ROMs
ROMTYPE = '.zip'


def main():
    """
    Main script.
    """
    # Takes command line arguments using the argparse library to build help files and check paths
    parser = argparse.ArgumentParser(description="""Tool to match and copy select ROMs from a new
    romset using either an existing destination directory of old ROMs or a CSV file of ROM filenames.
    Filenames are used to match ROMs and similar filename matches are sought when a perfect match 
    cannot be obtained.""")
    parser.add_argument("source", type=check_dir, help="Source directory of new ROMs.")
    parser.add_argument("target", type=check_dir, help="""Destination directory where ROMs will be
    matched and transferred to unless a CSV file is loaded. ROMs in this directory will be 
    overwritten by matches in the source directory.""")
    parser.add_argument('-ns', '--nosuggest', action='store_true', help='Disable similar ROM filename suggestion function.')
    parser.add_argument('-c', '--csv', type=check_csv, help="""CSV of
    ROM filenames to be transferred from the source to the target directory. One filename per row.""")
    args = parser.parse_args()


    # Call function to store ROM filenames in source directory in list
    new_list = dir_to_list(args.source, ROMTYPE)

    # Call function to store ROM filenames in the CSV or target directory if no CSV provided
    if args.csv:
        old_list = csv_to_list(args.csv)
        delete_originals = False
    else:
        old_list = dir_to_list(args.target, ROMTYPE)
        # Create CSV backup of existing ROM filenames in target directory
        list_to_csv(old_list, 'original_roms.csv', args.target)
        delete_originals = True

    # Call function to show matches and errors
    match_list, unmatched_list, delete_list = match_rom(old_list, new_list, delete_originals, args.nosuggest)

    # Print summary of the ROM matching process. Show warning message if any unmatched
    print('\n***Match Summary***')
    print('Total new source ROMs discovered:', len(new_list))
    print('Total target ROMs discovered:', len(old_list))
    print('Total new source ROMs matched to target ROMs:', len(match_list))
    if unmatched_list:
        print('\x1b[0;49;91m', end='')
        print('Total original ROMs unable to be matched:', len(unmatched_list))
        print('\x1b[0m', end='')
    else:
        print('All original ROMs matched!')

    # Prompt user to confirm whether they would like to proceed to replacing ROMs
    if input('\nWould you like to proceed to replacement (y/n)?').lower() == 'y':
        print('')
        # Call function to move matches from source directory to target directory
        copied = copy_rom(match_list, delete_list, args.target, args.source)
        # Print summary of ROM replacement
        print('\n***Copy Summary***')
        print('Total new ROMs matched and copied:', copied)
    else:
        print('No changes made.')

    # Create CSVs to show matched and unmatched ROMs
    if match_list:
        list_to_csv(match_list, 'matched_roms.csv', args.target)
    if unmatched_list:
        list_to_csv(unmatched_list, 'unmatched_roms.csv', args.target)

    # Exit with success code
    sys.exit(0)


def check_dir(directory):
    """
    Function to verify that the directory path passed to it exists and is a directory.
    """
    if not os.path.isdir(directory):
        msg = "{0} is not a directory".format(directory)
        raise argparse.ArgumentTypeError(msg)
    else:
        return os.path.abspath(os.path.realpath(os.path.expanduser(directory)))


def check_csv(file):
    """
    Function to verify that the filename passed to it is a valid CSV file.
    """
    if not os.path.isfile(file) or not file.endswith('.csv'):
        msg = msg = "%r is not a valid CSV file" % file
        raise argparse.ArgumentTypeError(msg)
    else:
        return file


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


def csv_to_list(csv_file):
    """
    Function to read a csv file and convert the entries on each row to a list.
    """
    csv_list = []
    # Create a CSV containing a list of all of the old ROM filenames
    with open(csv_file, 'r', newline='') as input_file:
        input_reader = csv.reader(input_file)
        # Write each old ROM filename to a row in the CSV
        for row in input_reader:
            csv_list.append(row[0])

    return csv_list


def list_to_csv(csvlist, filename, path):
    """
    Create a CSV containing from a list of filenames.
    """
    with open(path + filename, 'w', newline='') as output_file:
        output_writer = csv.writer(output_file)
        # Write each old ROM filename to a row in the CSV
        for rom in csvlist:
            output_writer.writerow([rom])
    print(filename + ' created in target directory')


def match_rom(old_file_list, new_file_list, delete_list, no_suggest):
    """
    Function to match ROM filenames in two lists of original ROMs and new ROMs.
    If no match is found similar filenames (if any) are shown to the user to
    select the best match or skipped as unmatched.
    Can also optionally create a delete list for original ROMs that have new
    filenames discovered by the user.
    Returns a list of matched ROM filenames, unmatched ROM filenames and delete list.
    """
    # lists to store matched, unmatched and to be deleted filenames
    matches = []
    unmatched = []
    delete = []

    for old_file in old_file_list:
        # Boolean to check whether a match has been found
        match = False
        # Iterate over the new files in the new file list
        for new_file in new_file_list:
            # Check if the old and new ROM filenames match
            if old_file == new_file:
                print('New source ROM matched: ' + new_file)
                matches.append(new_file)
                match = True
                break
        # If no match was found print an error message and add to error counter
        if not match:
            print('\x1b[0;49;91m', end='')
            print('Error! Unable to locate a source ROM: ' + old_file)
            # Check if no-suggest flag given
            if not no_suggest:
                # Find close filename matches (max of 3, min of 0)
                close = difflib.get_close_matches(old_file, new_file_list, n=5)
                # If any found inform the user and prompt them to choose or skip
                if close:
                    print('\x1b[0;49;96m', end='')
                    print(len(close), 'Close ROM filename/s found:\n0 : Skip')
                    close_no = 1
                    for closefiles in close:
                        print(close_no, ': Copy', closefiles)
                        close_no += 1
                    # Ensure correct choice is provided
                    while True:
                        choice = int(input('Choice: '))
                        if 0 <= choice <= len(close):
                            break
                    # Skip if user chooses or append close user choice to the match list
                    if choice == 0:
                        print(old_file, 'skipped')
                        unmatched.append(old_file)
                    else:
                        matches.append(close[choice - 1])
                        print('New source ROM matched:', close[choice - 1])
                        if delete_list:
                            delete.append(old_file)
                            print('Original ROM to be deleted:', old_file)
            else:
                unmatched.append(old_file)
            print('\x1b[0m', end='')
    return matches, unmatched, delete


def copy_rom(match_file_list, delete_file_list, old_dir, new_dir):
    """
    Function to take a list of matching ROM filenames in two directories (old
    ROMs and new ROMs) and copies these files. A delete list is also taken to
    remove ROMs that have been renamed.
    """
    copied = 0
    for match_file in match_file_list:
        shutil.copy(new_dir + '/' + match_file, old_dir + '/' + match_file)
        print('New ROM copied and replaced Old ROM: ' + match_file)
        copied += 1
    for delete_file in delete_file_list:
        os.unlink(old_dir + '/' + delete_file)
    return copied


if __name__ == "__main__":
    main()
