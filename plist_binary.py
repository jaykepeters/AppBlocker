#!/usr/bin/env python
### Binary Plist checker
import subprocess 
import json
applicationDB = {}
apps = [
    "/Applications/Utilities/Adobe Flash Player Install Manager.app", 
    "/Users/os/Desktop/Apps/iMovie.app", 
    "/Applications/iTunes.app", 
    "/Applications/Microsoft Word.app", 
    "/Applications/Microsoft Outlook.app", 
    "/Applications/GarageBand.app", 
    "/Applications/Microsoft Excel.app", 
    "/Applications/Microsoft PowerPoint.app", 
    "/Applications/Microsoft OneNote.app", 
    "/Applications/Adobe InDesign CS6/Adobe InDesign CS6.app", 
    "/Library/Application Support/Microsoft/MAU2.0/Microsoft AutoUpdate.app", 
    "/Applications/Game Maker Lite.app"
]


def getBinaryPlistKey(plist, key):
    process = subprocess.Popen(['defaults', 'read', plist, key], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output = process.stdout.readline()

    if process.poll() is None:
        return output.strip()
    else:
        return None

addtionalKeys = {
    "CFBundleDisplayName": "appName",
    "CFBundleName": "someName",
    "CFBundleExecutable": "executableName",
    "CFBundleShortVersionString": "appVersion",
    "LSApplicationCategoryType": "category",
    "INVALID": "INVALID"
}

for app in apps:
    plist = '/'.join([app, 'Contents/Info.plist'])
    bundleID = getBinaryPlistKey(plist, 'CFBundleIdentifier')
    if bundleID != None:
        ##appsWithErrors['binaryPlist'].remove(app)
        applicationDB[bundleID] = {}
        applicationDB[bundleID]['appPath'] = app
        for key in addtionalKeys.keys():
            value = getBinaryPlistKey(plist, key)
            if value != None:
                applicationDB[bundleID][addtionalKeys[key]] = value

print json.dumps(applicationDB, indent=4, sort_keys=True)
