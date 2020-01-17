#!/usr/bin/python
from AppKit import NSWorkspace
from Foundation import NSProcessInfo
import os
import signal 
import re

records = {
    "com.apple.systempreferences": {
        "alertMessage": "hello"
    }
}

def parseConfig(config):
    availableOptionKeys = {
        "allowedGroups": list,
        "allowedUsers": list,
        "customAlert": {
            "message": str,
            "informativeText": str,
            "iconPath": str
            "proceedButton": str
        },
        "deleteBlockedApplication": bool
    }

    # Every blocked app
    keyErrors = []
    for blockedApp in config:
        # Every key in blocked app entry
        for key in blockedApp.keys():
            # Is key type right?
            if key in availableOptionKeys.keys() and type(key) is availableOptionKeys[key] and type(key) is not dict:
                pass
            elif type(key) is dict and key is "customAlert":
                # for key in custom alert
                for _key in key.keys():
                    if _key in availableOptionKeys.keys():
                        pass
                    else:
                        return # FAIL
            else:
                return # FAIL
                    
        
    # for key in options.keys():
    #     if key in availableOptionKeys.keys() and type(key) is availableOptionKeys[key]:
    #         pass
    #     else:
    #         return False

regex = r"(com.jamfsoftware.*)"

violations = []

def takeAction(_violationInfo):    
    # Add the app to the queue
    violations.append(_violationInfo)

    # Kill the process
    os.kill(_violationInfo['processIdentifier'], signal.SIGKILL)

    # Extract the options
    options = records[_violationInfo['matchedRegex']]

def killRunningApps():
    workspace = NSWorkspace.sharedWorkspace()
    running_apps = workspace.runningApplications()
    for app in running_apps:
        match = re.match(regex, str(app.bundleIdentifier()))
        if match:
            _index = match.lastindex - 1
            exactBundleIDOrWildcard = re.sub(r"\(|\)", '', regex).split("|")[_index]
            
            # We call the takeaction method, with the additions below
            violationInfo = {
                "matchedRegex": exactBundleIDOrWildcard,
                "userName": NSProcessInfo.processInfo().userName(),
                "appName": app.localizedName(),
                "bundleIdentifier": app.bundleIdentifier(),
                "processIdentifier": app.processIdentifier(),
                "appPath...": 0
            }
           
            # Take action upon the app
            takeAction(violationInfo)

## BETA TESTING
if __name__ == "__main__":
    killRunningApps()
