#!/usr/bin/python
from AppKit import NSWorkspace
import os
import signal 

#blockedBundleIdentifiersCombined = "(" + ")|(".join(blockedBundleIdentifiers.keys()) + ")"
violationQueue = {}
regex = r"(com.microsoft.Word)|(com.apple.*)|(com.safeincloud.Safe-In-Cloud.OSX)"

def getBlockedApps():
    pass

def killRunningApps():
    ##
    workspace = NSWorkspace.sharedWorkspace()
    ##

    running_apps = workspace.runningApplications()
    for app in running_apps:
        import re
        matchedq = re.search(regex, str(app.bundleIdentifier()))
        if matchedq:
            _index = matchedq.lastindex - 1### WORKING
            
           # print(_index)
            print regex.replace('(', '').replace(')', '').split("|")[_index]

            
        # We call the takeaction method, with the additions below
        #if app.bundleIdentifier() in blockedApps: # if re.match(blockedBundleIdentifiersCombined, app.bundleIdentifier()): # does the bundle identifier match?\
            violationInfo = {
                "name": app.localizedName(),
                "bundleIdentifier": app.bundleIdentifier(),
                "processIdentifier": app.processIdentifier()
            }
            print(violationInfo)
            #NSRUNNINGAPPLICATION
           # violationQueue.append(violationInfo)
            # Kill the PID of the app!
            #os.kill(app.processIdentifier(), signal.SIGKILL)
            #app.hide() soft block

## BETA TESTING
if __name__ == "__main__":
    killRunningApps()
