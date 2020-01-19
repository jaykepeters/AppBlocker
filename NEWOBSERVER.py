#!/usr/bin/python

import objc
from Foundation import NSObject, NSKeyValueObservingOptionNew, NSKeyValueChangeNewKey

"""
Getting help from: 
https://nshipster.com/key-value-observing/
https://svn.red-bean.com/pyobjc/branches/pyobjc-1.4-branch/Examples/00ReadMe.html
https://stackoverflow.com/questions/8317338/how-to-use-kvo-to-detect-when-an-application-gets-active
https://stackoverflow.com/questions/52710089/macos-detect-all-application-launches-including-background-apps

"""

import Foundation
import AppKit
from PyObjCTools import AppHelper

def takeaction(runningapp):
    print(runningapp.bundleIdentifier())
    
class Observer(NSObject):
    def observeValueForKeyPath_ofObject_change_context_(self, path, object, changeDescription, context):
        if NSKeyValueChangeNewKey == 'new':
            takeaction(object.runningApplications()[-1])
        #print changeDescription[NSKeyValueChangeNewKey]
        
    def willChangeValueForKey_(self, key):
        print "Changed"
        

observer = Observer.new()


workspace = Foundation.NSWorkspace.sharedWorkspace() # For runnning apps
#3nc = workspace.notificationCenter()

workspace.addObserver_forKeyPath_options_context_(observer, 'runningApplications', NSKeyValueObservingOptionNew, 0)

AppHelper.runConsoleEventLoop().run()
