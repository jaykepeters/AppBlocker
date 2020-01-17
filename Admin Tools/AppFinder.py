#!/usr/bin/env python
import subprocess # for running the commmand
import plistlib # for getting bundle identifiers
import json # for formatting the dict
import xml.parsers.expat # for error checking
from datetime import datetime

# Generate the outfile name
timestamp = datetime.now().strftime('%m%d%y%H%M')

# Initialize Necessary Types
applicationDB = {}
_applicationDB = {}
appsWithErrors = {
    "noCFBundleIdentifier": [],
    "binaryPlist": [],
    "noPlist": [],
    "unknown": []
}

## FUNCTIONS
def getBinaryPlistKey(plist, key):
    process = subprocess.Popen(['defaults', 'read', plist, key], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output = process.stdout.readline()

    if process.poll() is None:
        return output.strip()
    else:
        return None

def writeDict(_dict, file):
    with open(file, "w") as outfile:
        json.dump(_dict, outfile, indent=4, sort_keys=True)
## END OF FUNCTIONS

# Get all apps on this computer
command="mdfind kind:application"
apps = subprocess.check_output(command, shell=True).strip().split("\n")
# apps = [
#     "/Applications/Safari.app",
#     "/Applications/iMovie.app",
#     "/Applications/FaceTime.app"
#] error with /Applications/Utilities/Adobe Flash Player Install Manager.app/Contents/Info.plist? # first binary plist too...

# Additional plist keys to check for
addtionalKeys = {
    "CFBundleDisplayName": "appName",
    #"CFBundleName": "appName",
    "CFBundleExecutable": "executableName",
    "CFBundleShortVersionString": "appVersion",
    "LSApplicationCategoryType": "category"
}

# Iterate over every application, checking for a CFBundleIdentifier and more!
for app in apps:
    # Set the plist path
    plist = '/'.join([app, 'Contents/Info.plist'])

    # There are no errors, so far
    error = False # Resolved switching issue in dict...

    # Try to get the plist and/or bundle identifier
    try:    
        _plist = plistlib.readPlist(plist)
    except xml.parsers.expat.ExpatError:
        error = True
        appsWithErrors['binaryPlist'].append(app)
    except IOError:
        if not error: ### EXPERIMENTAL, HEREON
            error = True
            appsWithErrors['noPlist'].append(app)
    
    # Get the CFBundleIdentifier, or not
    try: 
        bundleID = _plist['CFBundleIdentifier']
    except:
        if not error:
            error = True
            appsWithErrors['noCFBundleIdentifier'].append(app)

    # Ok, so we got the bundle id, let's get some more info 
    if not error:
        appInfo = {}

        # GET THE APP DATA, DON'T ADD IT YET
        appInfo['appPath'] = app
        for key in addtionalKeys.keys():
            if key in _plist.keys():
                value = _plist[key]
                appInfo[addtionalKeys[key]] = value

        # NOW ADD THE DATA, CONDITIONALLY
        if not bundleID in applicationDB.keys():
            # NORMAL PROCEDURE FOR MOST APPS
            applicationDB[bundleID] = appInfo
        else: # MORE THAN ONE OCCURRENCE
            if type(applicationDB[bundleID]) is not list: # not a list, let's do some moving...
                originaldata = applicationDB[bundleID].copy()
                del applicationDB[bundleID]
                applicationDB[bundleID] = [originaldata, {}]
                applicationDB[bundleID][1] = appInfo
            else:
                applicationDB[bundleID].append(appInfo)

# Try to get the binary plist keys (WORKAROUND) SEE DOCS
counter = 0 #temp
for app in appsWithErrors['binaryPlist']:
    counter += 1 #temp
    plist = '/'.join([app, 'Contents/Info.plist'])
    bundleID = getBinaryPlistKey(plist, 'CFBundleIdentifier')

    if bundleID != None: # LIKE NORMAL, WE GOT A BUNDLE ID
        appInfo = {}
        appInfo['appPath'] = app
        for key in addtionalKeys.keys():
            value = getBinaryPlistKey(plist, key)
            if value != None:
                appInfo[addtionalKeys[key]] = value
        
        # NOW ADD THE DATA, CONDITIONALLY
        if not bundleID in applicationDB.keys():
            # NORMAL PROCEDURE FOR MOST APPS
            applicationDB[bundleID] = appInfo
        else: # MORE THAN ONE OCCURRENCE
            if type(applicationDB[bundleID]) is not list: # not a list, let's do some moving...
                originaldata = applicationDB[bundleID].copy()
                del applicationDB[bundleID]
                applicationDB[bundleID] = [originaldata, {}]
                applicationDB[bundleID][1] = appInfo
            else:
                applicationDB[bundleID].append(appInfo)

## Can't remove item each time for some reason... HOPE
if counter == len(appsWithErrors['binaryPlist']): #temp
    del appsWithErrors['binaryPlist'] #temp

# Output our findings to 2 files
writeDict(applicationDB, 'appDB_{}.json'.format(timestamp))
writeDict(appsWithErrors, 'errors_{}.json'.format(timestamp))

# Let the user know some key information ;)
print("Total Apps Found: "+str(len(apps)))
print("Total Bundle Identifiers found: "+str(len(applicationDB)))
print("The application database has been exported to: "+'appDB_{}.json'.format(timestamp))
print("Any apps with errors can be found in "+'errors_{}.json'.format(timestamp))
