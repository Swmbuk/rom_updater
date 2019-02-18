#!/usr/bin/env python3
"""
Tool to match and copy select ROMs from a new romset using either an existing
destination directory of old ROMs or a CSV file of ROM filenames. Filenames are
used to match ROMs and similar filename matches are sought when a perfect match
cannot be obtained.
"""

# Liam Bates - February 12, 2019 (Python 3.7.2)

import argparse
import csv
import difflib
import os
import shutil
import sys

# Select the filetype for the ROMs
ROMTYPE = '.zip'


def main():
    """Main script"""
    # Collect command line argument values from function
    args = get_args()

    # Call function to store ROM filenames in source directory in list
    source_list = dir_to_list(args.source, ROMTYPE)

    # Call function to store ROM filenames in the CSV if one given
    if args.csv:
        target_list = csv_to_list(args.csv)
        delete_originals = False
    # Call function to store ROM filenames in target directory
    else:
        target_list = dir_to_list(args.target, ROMTYPE)
        # Create CSV backup of existing ROM filenames in target directory
        list_to_csv(target_list, 'original_roms.csv', args.target)
        delete_originals = True

    # Call function to show matches and errors
    match_list, unmatched_list, delete_list = match_rom(
        target_list, source_list, delete_originals, args.nosuggest)

    # Print summary of the ROM matching process. Show warning for unmatched
    print('\n***Match Summary***')
    print('Total new source ROMs discovered:', len(source_list))
    print('Total target ROMs discovered:', len(target_list))
    print('Total new source ROMs matched to target ROMs:', len(match_list))
    if unmatched_list:
        print('\x1b[0;49;91m', end='')
        print('Total original ROMs unable to be matched:', len(unmatched_list))
        print('\x1b[0m', end='')
    else:
        print('All original ROMs matched!')

    # Prompt user to confirm whether to proceed to replacing ROMs
    if input('\nProceed to replacement (y/n)?').lower() == 'y':
        print('')
        # Call function to copy matches from source to target directory
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


def get_args():
    """
    Function to ensure appropriate arguments have been provided for the tool and
    to provide help messaging based on the required and optional arguments.
    If appropriate arguments are provided the values are returned.
    """
    # General description of the program
    parser = argparse.ArgumentParser(description="""Tool to match and copy
    select ROMs from a new romset using either an existing destination directory 
    of old ROMs or a CSV file of ROM filenames. Filenames are used to match ROMs
    and similar filename matches are sought when a perfect match cannot be
    obtained.""")
    # Add two mandatory directory arguments, with dir checks function calls
    parser.add_argument(
        "source", type=check_dir, help="Source directory of new ROMs.")
    parser.add_argument(
        "target",
        type=check_dir,
        help="""Destination directory where ROMs will be matched and transferred
         to unless a CSV file is loaded. ROMs in this directory will be
         overwritten by matches in the source directory.""")
    # Add two optional arguments, with CSV check function calls
    parser.add_argument(
        '-ns',
        '--nosuggest',
        action='store_true',
        help='Disable similar ROM filename suggestion function')
    parser.add_argument(
        '-c',
        '--csv',
        type=check_csv,
        help="""CSV of ROM filenames to be transferred from the source to the
        target directory. One filename per row.""")
    # Assuming no issues return the argument values
    return parser.parse_args()


def check_dir(directory):
    """
    Function to verify that the directory path passed to it exists and is a
    valid directory.
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
    filenamelist = set()
    for file in os.listdir(directory):
        if file.endswith(filetype) and not file.startswith('.'):
            filenamelist.add(file)
    return sorted(filenamelist)


def csv_to_list(csv_file):
    """
    Function to read a csv file and convert the entries on each row to a list.
    """
    csv_list = set()
    # Open CSV file for reading as provided to the function
    with open(csv_file, 'r', newline='') as input_file:
        input_reader = csv.reader(input_file)
        # Read each row in the csv and save to a list
        for row in input_reader:
            csv_list.add(row[0])
    # Return CSV contents as list
    return sorted(csv_list)


def list_to_csv(csvlist, filename, path):
    """
    Create a CSV containing from a list of filenames.
    """
    with open(path + '/' + filename, 'w', newline='') as output_file:
        output_writer = csv.writer(output_file)
        # Write each old ROM filename to a row in the CSV
        for rom in csvlist:
            output_writer.writerow([rom])
    print(filename + ' created in target directory')


def match_rom(target_file_list, source_file_list, delete_list, no_suggest):
    """
    Function to match ROM filenames in two lists of original ROMs and new ROMs.
    If no match is found similar filenames (if any) are shown to the user to
    select the best match or skipped as unmatched.
    Can also optionally create a delete list for original ROMs that have new
    filenames discovered by the user.
    Returns a list of matched ROM filenames, unmatched ROM filenames and delete
    list.
    """
    # lists to store matched, unmatched and to be deleted filenames
    matches = []
    unmatched = []
    delete = []

    for target_file in target_file_list:
        # Check if target file in source file list
        if target_file in source_file_list:
            print('New source ROM matched: ' + target_file)
            matches.append(target_file)
        # If no match was found print an error message and try find similar
        else:
            print('\x1b[0;49;91m', end='')
            print('Error! Unable to locate a source ROM: ' + target_file)
            # Check if no-suggest flag given
            if not no_suggest:
                # Find close filename matches (max of 5, min of 0)
                close = difflib.get_close_matches(
                    target_file, source_file_list, n=5)
                # If any found inform the user and prompt them to choose or skip
                if close:
                    print('\x1b[0;49;96m', end='')
                    print(len(close), 'close ROM filename/s found:\n0 : Skip')
                    close_no = 0
                    for close_files in close:
                        close_no += 1
                        print(close_no, ': Copy', close_files)
                    # Ensure correct choice is provided
                    while True:
                        choice = int(input('Choice: '))
                        if 0 <= choice <= len(close):
                            break
                    # Skip if user chooses 'skip' option
                    if choice == 0:
                        print(target_file, 'skipped')
                        unmatched.append(target_file)
                    # Otherwise add suggested choice to match list
                    else:
                        matches.append(close[choice - 1])
                        print('New source ROM matched:', close[choice - 1])
                        if delete_list:
                            delete.append(target_file)
                            print('Original ROM to be deleted:', target_file)
            else:
                unmatched.append(target_file)
            print('\x1b[0m', end='')
    return matches, unmatched, delete


def copy_rom(match_file_list, delete_file_list, target_dir, source_dir):
    """
    Function to take a list of matching ROM filenames in two directories (old
    ROMs and new ROMs) and copies these files. A delete list is also taken to
    remove any ROMs that have been renamed.
    """
    copied = 0
    for match_file in match_file_list:
        shutil.copy(source_dir + '/' + match_file,
                    target_dir + '/' + match_file)
        print('New ROM copied and replaced Old ROM: ' + match_file)
        copied += 1
    for delete_file in delete_file_list:
        os.unlink(target_dir + '/' + delete_file)
    return copied


if __name__ == "__main__":
    main()
