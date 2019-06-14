#!/usr/bin/env python
import Foundation
import signal
import re
import os
import sys
import shutil
from AppKit import *
from PyObjCTools import AppHelper

# List of all blocked bundle identifiers. Can use regexes.
blockedBundleIdentifiers = {
	"com.apple.InstallAssistant.Sierra": {
		"alertUser": True,
		"alertMessage": "macOS Sierra is blocked.",
		"deleteBlockedApplication": True
	},
	"com.apple.Terminal": {
		"deleteBlockedApplication": True,
		"alertUser": True,
		"alertMessage": "Only Jayke is allowed to use the terminal."
	},
	"com.google.Chrome":{},
	"com.microsoft.Word":{}
}

blockedBundleIdentifiers.update({'com.apple.Console':{}})
print(blockedBundleIdentifiers.keys())

## Defaults
deleteBlockedApplication = False

# Whether the user should be alerted that the launched applicaion was blocked
alertUser = True

# Message displayed to the user when application is blocked
alertMessage = "The application \"{appname}\" has been blocked by IT"
alertInformativeText = "Contact your administrator for more information"

# Use a custom Icon for the alert. If none is defined here, the Python rocketship will be shown.
alertIconPath = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns"

# Define callback for notification
class AppLaunch(NSObject):
	def appLaunched_(self, notification):

		# Store the userInfo dict from the notification
		userInfo = notification.userInfo

		# Get the laucnhed applications bundle identifier
		bundleIdentifier = userInfo()['NSApplicationBundleIdentifier']

		# Check if launched app's bundle identifier matches any 'blockedBundleIdentifiers'
		if re.match(blockedBundleIdentifiersCombined, bundleIdentifier):

			## OPTIONS
			options = blockedBundleIdentifiers[bundleIdentifier]

			# Get path of launched app
			path = userInfo()['NSApplicationPath']

			# Get PID of launchd app
			pid = userInfo()['NSApplicationProcessIdentifier']

			# Quit launched app
			os.kill(pid, signal.SIGKILL)

			if 'deleteBlockedApplication' in options:
				if options['deleteBlockedApplication']:
					try:
						shutil.rmtree(path)
					except OSError, e:
						print ("Error: %s - %s." % (e.filename,e.strerror))

			# Alert user
			if 'alertUser' in options:
				if options['alertUser']:
					if 'alertMessage' in options:
						alert(options['alertMessage'], alertInformativeText, ["OK"])
			else:
				alert(alertMessage.format(appname=userInfo()['NSApplicationName']), alertInformativeText, ["OK"])

# Define alert class
class Alert(object):

	def __init__(self, messageText):
		super(Alert, self).__init__()
		self.messageText = messageText
		self.informativeText = ""
		self.buttons = []

	def displayAlert(self):
		alert = NSAlert.alloc().init()
		alert.setMessageText_(self.messageText)
		alert.setInformativeText_(self.informativeText)
		alert.setAlertStyle_(NSInformationalAlertStyle)
		for button in self.buttons:
			alert.addButtonWithTitle_(button)

		if os.path.exists(alertIconPath):
			icon = NSImage.alloc().initWithContentsOfFile_(alertIconPath)
			alert.setIcon_(icon)

		# Don't show the Python rocketship in the dock
		NSApp.setActivationPolicy_(1)

		NSApp.activateIgnoringOtherApps_(True)
		alert.runModal()

# Define an alert
def alert(message="Default Message", info_text="", buttons=["OK"]):	   
	ap = Alert(message)
	ap.informativeText = info_text
	ap.buttons = buttons
	ap.displayAlert()

# Combine all bundle identifiers and regexes to one
blockedBundleIdentifiersCombined = "(" + ")|(".join(blockedBundleIdentifiers.keys()) + ")"

# Register for 'NSWorkspaceDidLaunchApplicationNotification' notifications
nc = Foundation.NSWorkspace.sharedWorkspace().notificationCenter()
AppLaunch = AppLaunch.new()
nc.addObserver_selector_name_object_(AppLaunch, 'appLaunched:', 'NSWorkspaceWillLaunchApplicationNotification',None)

# Launch "app"
AppHelper.runConsoleEventLoop()
