#!/usr/bin/python
# Next version, use categorify.org to extract bundle id info, block categories...
# Get current user every minute, and then see if the user is in the list, etc..
# For example, people of group x can use app x...
# Or users x, y, and z are allowed and others are not.
print("Status: Starting AppBlocker")
import Foundation
import signal
import re
import os
import sys
import shutil
from AppKit import *
from PyObjCTools import AppHelper
from SystemConfiguration import SCDynamicStoreCopyConsoleUser # For getting the currently logged in user
import json
import threading
import hashlib

## Current User Function
# A more "Apple Approved" way
def current_user():
    username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0] 
    username = [username,""][username in [u"loginwindow", None, u""]]
    return username

def get_groups(user):
    import grp, pwd 
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)
    return groups

## CONFIG FILE ##
config = "/private/var/root/.AppBlocker.json"
## CONFIG FILE ##

## MD5 File Hasher
def hashfile(file):
    hasher = hashlib.md5()
    try:
        with open(file, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except:
        print("Error: Could not hash config file")

## CONFIG LOAD FUNCTIONS
def loadConfig():
    global filehash
    global currentuser
    global blockedBundleIdentifiers
    global blockedBundleIdentifiersCombined

    # Get the current user
    currentuser = current_user()

    # Load the config
    if config:
        filehash = hashfile(config)
        try:
            with open(config) as config_file:
                blockedBundleIdentifiers = json.load(config_file)
        except: 
            print("Error: could not open or parse config file")
            exit(1)
    else:
        print("Error: Config file does not exist!")
        exit(1)

    # Combine the bundle identifiers
    blockedBundleIdentifiersCombined = "(" + ")|(".join(blockedBundleIdentifiers.keys()) + ")"

## Configuration refresher
## No more reloading the agent :)
def refreshConfig():
    threading.Timer(15, refreshConfig).start()

    global blockedBundleIdentifiers
    global blockedBundleIdentifiersCombined

    # Hash check the config
    if hashfile(config) != filehash:
        print("Status: Config file hash changed")
        # We should refresh the configuration file
        loadConfig()

## Load the Config Now...
loadConfig()

print("Status: AppBlocker Ready")
## Match Regex Identifier Options
def matchIdentifier(dictionary, substr):
    result = {}
    for key in dictionary.keys():
        if re.match(key, substr):
            result = dictionary[key]
            break
    return results

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
		matched = re.match(blockedBundleIdentifiersCombined, bundleIdentifier)
		if matched:
			print("Match Found: " + matched.group())            
		
			## OPTIONS
			try:
				# Verbatim Identifier
				options = blockedBundleIdentifiers[bundleIdentifier]
			except:
				# Regex Identifier
				print(matched.group())
				options = matchIdentifier(blockedBundleIdentifiers, matched.group())
				print(options)

			# Get path of launched app
			path = userInfo()['NSApplicationPath']

			# Get PID of launchd app
			pid = userInfo()['NSApplicationProcessIdentifier']

			# Quit launched app
			os.kill(pid, signal.SIGKILL)

            # Delete launched app
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
            # Alerting is now disabled by default.
			#else:
				#alert(alertMessage.format(appname=userInfo()['NSApplicationName']), alertInformativeText, ["OK"])

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

# Start the refreshConfig function
refreshConfig()

# Register for 'NSWorkspaceDidLaunchApplicationNotification' notifications
nc = Foundation.NSWorkspace.sharedWorkspace().notificationCenter()
AppLaunch = AppLaunch.new()
nc.addObserver_selector_name_object_(AppLaunch, 'appLaunched:', 'NSWorkspaceWillLaunchApplicationNotification',None)

# Launch "app"
AppHelper.runConsoleEventLoop()
