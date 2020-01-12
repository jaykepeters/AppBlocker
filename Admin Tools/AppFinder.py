#!/usr/bin/env python
import subprocess # for running the commmand
import plistlib # for getting bundle identifiers
import json # for formatting the dict

# Initialize Necessary Types
applicationDB = {}
appsWithNoBundleID = []
appDBJSON = "appdb.json"

# Get all apps on this computer
command="mdfind kind:application"
apps = subprocess.check_output(command, shell=True).strip().split("\n")

# Iterate over every application, checking for a CFBundleIdentifier and more!
for app in apps:
    # Set the plist path
    plist = '/'.join([app, 'Contents/Info.plist'])
    
    try:
        bundleID = plistlib.readPlist(plist)['CFBundleIdentifier']
        # Add to applicationsDB
        applicationDB[bundleID] = {'applicationPath': app}
    except:
        # Add to appsWithNoBundleID
        appsWithNoBundleID.append(app)

# Output our findings to a file
with open(appDBJSON, "w") as applicationDatabase:
    json.dump(applicationDB, applicationDatabase, indent=4, sort_keys=True)

# Let the user know some things :)
print("Total Apps Found: "+str(len(apps)))
print("Total Bundle Identifiers found: "+str(len(applicationDB)))
print("The application database has been exported to: "+appDBJSON)
