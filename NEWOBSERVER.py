#!/usr/bin/python

import objc
from Foundation import NSObject, NSKeyValueObservingOptionNew, NSKeyValueChangeNewKey

import Foundation
from AppKit import NSWorkspace

from PyObjCTools import AppHelper

class Observer(NSObject):
    def observeValueForKeyPath_ofObject_change_context_(self, path, object, changeDescription, context):
        print 'path "%s" was changed to "%s".' % (path, changeDescription[NSKeyValueChangeNewKey])

observer = Observer.new()


workspace = Foundation.NSWorkspace.sharedWorkspace() # For runnning apps
#3nc = workspace.notificationCenter()

workspace.addObserver_forKeyPath_options_context_(observer, 'runningApplications', NSKeyValueObservingOptionNew, 0)

AppHelper.runConsoleEventLoop()
