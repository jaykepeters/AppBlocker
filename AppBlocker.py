#!/usr/bin/python
# Next version, use categorify.org to extract bundle id info, block categories...
# Users that should have gaming access
"""
SOMETHING LIKE THIS, NOT EXACTLY...
dscl . -create /Groups/gaming RealName "Gaming Users"
dseditgroup -o edit -a jaykepeters -t user gaming
"""
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
config = "/Users/os/.AppBlocker.json"
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
	global whitelisted

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
## Probably stop for sake of battery life...
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
			## OPTIONS
			try:
				# Verbatim Identifier
				options = blockedBundleIdentifiers[bundleIdentifier]
			except:
				# Regex Identifier
				print(matched.group()) ## BUG and NOT WORKING?
				options = matchIdentifier(blockedBundleIdentifiers, matched.group())
				print(options)

			## ABSOLUTE PATH
			def takeAction():
				# Get path of launched app
				path = userInfo()['NSApplicationPath']
				print(path)

				# Get PID of launchd app
				pid = userInfo()['NSApplicationProcessIdentifier']

				# Quit launched app
				try:
					os.kill(pid, signal.SIGKILL)
				except:
					print("Error, some other process killed the app first...")
					
				# Delete launched app
				if 'deleteBlockedApplication' in options:
					if options['deleteBlockedApplication']:
						try:
							shutil.rmtree(path)
						except OSError, e:
							print ("Error: %s - %s." % (e.filename,e.strerror))

				# Alert user
				if 'alertMessage' in options:
					alert(options['alertMessage'], alertInformativeText, ["OK"])
				## REMEMBER THAT ALERTUSER IS NOW DEPRECATED. THE PRESENCE OF THE ALERT MESSAGE IS THE TRIGGER

			## ALLOWED USERS/GROUPS/FILEPATHS
			if 'allowedUsers' in options:
				if options['allowedUsers']:
					if currentuser not in options['allowedUsers']:
						takeAction()
			elif 'allowedGroups' in options:
				if options['allowedGroups']:
					groups = get_groups(currentuser)
					membercount = 0
					for group in groups:
						if group in options['allowedGroups']:
							membercount += 1
					if not membercount >= 1:
						takeAction()
			elif 'allowedPath' in options:
				if options['allowedPath'] and options['allowedPath'] != userInfo()['NSApplicationPath']:
					print(userInfo()['NSApplicationPath'])
					print(options['allowedPath'])
					whitelisted = False #experimental
				 	takeAction()# Maybe convert option path to that of path launched... Making sure compares no matter what...
			else:
				takeAction()

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
