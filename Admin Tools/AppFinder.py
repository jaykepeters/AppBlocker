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

## FUNCTIONS
def getBinaryPlistKey(plist, key):
    out = subprocess.Popen(['defaults', 'read', plist, key], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    return stdout.strip(), stderr

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
    "CFBundleName": "someName",
    "CFBundleExecutable": "executableName",
    "CFBundleShortVersionString": "appVersion",
    "LSApplicationCategoryType": "category"
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
    
    # Assuming we got a valid, readable plist
    # Get the CFBundleIdentifier, or not
    try: 
        bundleID = _plist['CFBundleIdentifier']
    except:
        appsWithErrors['noCFBundleIdentifier'].append(app)

    # Ok, so we got the bundle id, let's get some more info 
    applicationDB[bundleID] = {}
    applicationDB[bundleID]['appPath'] = app
    for key in addtionalKeys.keys():
        if key in _plist.keys():
            value = _plist[key]
            applicationDB[bundleID][addtionalKeys[key]] = value

# Try to get the binary plist keys (WORKAROUND) SEE DOCS
for app in appsWithErrors['noCFBundleIdentifier']:
    plist = '/'.join([app, 'Contents/Info'])
    cmdOut = getBinaryPlistKey(plist, 'CFBundleIdentifier')
    if not 'not' in cmdOut[0]:
        print(cmdOut[0])

# Output our findings to 2 files
writeDict(applicationDB, appDBJSON)
writeDict(appsWithErrors, 'appfinder_errors.json')

# Let the user know some things :)
print("Total Apps Found: "+str(len(apps)))
print("Total Bundle Identifiers found: "+str(len(applicationDB)))
print("The application database has been exported to: "+appDBJSON)
print("Any apps with errors can be found in appErrors.json")
