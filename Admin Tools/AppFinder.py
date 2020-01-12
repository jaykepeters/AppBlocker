#!/usr/bin/env python
import subprocess # for running the commmand
import plistlib # for getting bundle identifiers
import json # for formatting the dict
import xml.parsers.expat # for error checking

# Initialize Necessary Types
applicationDB = {}
appsWithErrors = {
    "noCFBundleIdentifier": [],
    "binaryPlist": [],
    "noPlist": [],
    "unknown": []
}
appDBJSON = "appdb.json"

# Get all apps on this computer
command="mdfind kind:application"
apps = subprocess.check_output(command, shell=True).strip().split("\n")

# Additional plist keys to check for
addtionalKeys = {
    "CFBundleDisplayName": "appName",
    "CFBundleName": "someName",
    "CFBundleExecutable": "executableName",
    "CFBundleShortVersionString": "appVersion"
}

# Iterate over every application, checking for a CFBundleIdentifier and more!
for app in apps:
    # Set the plist path
    plist = '/'.join([app, 'Contents/Info.plist'])

    # Try to get the plist and/or bundle identifier
    try:    
        _plist = plistlib.readPlist(plist)
    except xml.parsers.expat.ExpatError:
        appsWithErrors['binaryPlist'].append(app)
    except IOError:
        appsWithErrors['noPlist'].append(app)
    finally:
        appsWithErrors['unknown'].append(app)
    
    # Assuming we got a valid, readable plist
    # Get the CFBundleIdentifier, or not
    try:
        bundleID = _plist['CFBundleIdentifier']
    except:
        appsWithErrors['noCFBundleIdentifier'].append(app)

    # Ok, so we got the bundle id, let's get some more info 
    applicationDB[bundleID] = {}
    for key in addtionalKeys.keys():
        if key in _plist.keys():
            value = _plist[key]
            applicationDB[bundleID][addtionalKeys[key]] = value
            
# Output our findings to a file
with open(appDBJSON, "w") as applicationDatabase:
    json.dump(applicationDB, applicationDatabase, indent=4, sort_keys=True)

# Let the user know some things :)
print("Total Apps Found: "+str(len(apps)))
print("Total Bundle Identifiers found: "+str(len(applicationDB)))
print("The application database has been exported to: "+appDBJSON)
