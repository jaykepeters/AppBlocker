#!/usr/bin/python
from AppKit import NSWorkspace
import os
import signal 

workspace = NSWorkspace.sharedWorkspace()
running_apps = workspace.runningApplications()
for app in running_apps:
    print(app)
    # Bundle Identifier
    #bundleIdentifier = app.bundleIdentifier()
    #if bundleIdentifier == "com.apple.Terminal":
        #print("Terminal is blocked :(")
        # Application Name
    print app.localizedName()

        # Application Path
    print app.bundleURL().path()

        # PID
    pid = app.processIdentifier()

        # Launch Date
    launchDate = app.launchDate()

    #if not app.forceTerminate():
        #os.kill(pid, signal.SIGKILL)


"""
import Foundation

proci = Foundation.NSProcessInfo.processInfo()
print(proci.userName())
print(proci.environment())
"""


