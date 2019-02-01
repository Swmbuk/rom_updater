# Liam Bates - January 31, 2019 (Python 3.7.2)

# Program to update a folder of ROMs (or any file) with identically named
# replacements located in another foler. The purpose of this program was to
# allow myself to update my curated lists of ROMs without a large amount of
# manual work. The program also records a CSV file in the old ROM directory
# with a list of all of the ROM filenames.

import sys, os, shutil, csv

# Select the filetype for the ROMs
ROMTYPE = '.zip'

# Function to find a filetype in a directory and place the filename in a list
# that is returned
def dir_to_list(dir, filetype):
    list = []
    for file in os.listdir(dir):
        if file.endswith(filetype):
            list.append(file)
    return list

# Function to match files in two lists. If the third argument is left False then
# the function will show matches only and count them. If True then the Function
# will copy the file from the new directory to the old directory
def match_copy(OldFilelist, NewFilelist, copy):
    # list to monitor matches and errors respectively (e.g. item 1 - matches)
    matcherror = [0, 0]

    for OldFile in OldFilelist:
        # Boolean to check whether a match has been found
        match = False
        # Iterate over the new files in the new file list
        for NewFile in NewFilelist:
            # Check if the old and new ROM filenames match
            if OldFile == NewFile:
                if copy == False:
                    print('New ROM matched to Old ROM: ' + NewFile)
                else:
                    shutil.copy(NewDir + '/' + NewFile, OldDir + '/' + OldFile)
                    print('New ROM copied and replaced Old ROM: ' + NewFile)
                matcherror[0] += 1
                match = True
        # If no match was found print an error message and add to error counter
        if match == False:
            print('\x1b[0;49;91m', end='')
            print('Error! Unable to locate a New ROM: ' + OldFile)
            print('\x1b[0m', end='')
            matcherror[1] += 1
    return matcherror

# Check if 2 command line arguments were provided in terminal
if len(sys.argv) != 3:
    print('Error! Usage: python ROM_Update.py "Old ROMs Location" "New ROMs Location"')
    sys.exit(1)

# Store command line arguments
OldDir = sys.argv[1]
NewDir = sys.argv[2]

# Call function to store all ROMs in the new and old directories in lists
OldList = dir_to_list(OldDir, ROMTYPE)
NewList = dir_to_list(NewDir, ROMTYPE)

# Create a CSV containing a list of all of the old ROM filenames
outputFile = open(OldDir + '/oldlist.csv', 'w', newline='')
outputWriter = csv.writer(outputFile)
# Write each old ROM filename to a row in the CSV
for ROM in OldList:
    outputWriter.writerow([ROM])
# Close file
outputFile.close()

# Call function to show matches and errors
matcherror = match_copy(OldList, NewList, False)

print('\n***Match Summary***')
print('Total New ROMs discovered:', len(NewList))
print('Total Old ROMs discovered:', len(OldList))
print('Total New ROMs matched to old ROMs:', matcherror[0])
if matcherror[1] > 0:
    print('\x1b[0;49;91m', end='')
    print('WARNING!! Total Old ROMs unable to be matched:', matcherror[1])
    print('\x1b[0m', end='')
else:
    print('Total Old ROMs unable to be matched:', matcherror[1])

# Prompt user to confirm whether they would like to proceed to replacing ROMs
if input('\nWould you like to proceed to replacement (y/n)?').lower() == 'y':
    print('')
    # Call function to move matches from old directory to new directory
    matcherror = match_copy(OldList, NewList, True)

    print('\n***Copy Summary***')
    print('Total New ROMs Matched and Copied:', matcherror[0])
    print('Total Old ROMs Unable to be matched:', matcherror[1])
else:
    print('No changes made.')

# Exit with success code
sys.exit(0)
