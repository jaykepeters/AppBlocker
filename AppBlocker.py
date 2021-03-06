#!/usr/bin/env python
import Foundation
import signal
import re
import os
import sys
import shutil
import AppKit
from PyObjCTools import AppHelper
import re
import json
import inspect
from string import Template
import ast

# Get the current user and their groups
currentUser = Foundation.NSProcessInfo.processInfo().userName()

# The config file
config_file = "/Users/os/.AppBlocker2.json"

# The log file
log_file = "/Users/os/AppBlocker.log"

# Record violations queue
violations = []

# Key existence checker
def KeyExists(dict, key): 
    if key in dict.keys(): 
        return True 
    else: 
        return False

# Config file checker
def parseConfig(_config):
    # Read the JSON
    try:
        with open(_config) as json_file: # EVAL BOOLS????? REDO!!!!
            #config = ast.literal_eval(json.dumps(json.load(json_file))) # So yeah, UTF-8...
            config = json.load(json_file)
    except:
        exit("BAD CONFIG OR NO FILE")
    
    # List of errors
    errors = []
        
    # Current available options
    availableOptionKeys = {
        "allowedUsers": list,
        "customAlert": {
            "message": unicode,
            "informativeText": unicode,
            "iconPath": unicode,
            "proceedButton": list
        },
        "deleteBlockedApplication": bool,
        "allowedPath": unicode
    }
    
    # Traverse the config file :) Sad looking!
    for record in config:
        for key in config[record]:
            if KeyExists(availableOptionKeys, key):
                if type(config[record][key]) is availableOptionKeys[key]:
                    pass
                elif type(config[record][key]) is dict:
                    for subkey in config[record][key]:
                        if KeyExists(availableOptionKeys[key], subkey):
                            if type(config[record][key][subkey]) is availableOptionKeys[key][subkey]:
                                pass
                            else:
                                errors.append("Invalid subkey type, {} -> {} -> {}".format(record, key, subkey))
                        else:
                            errors.append("Invalid subkey, {} -> {} -> {}".format(record, key, subkey))
                else:
                    errors.append("Invalid key type, {} -> {}".format(record, key))
            else:
                errors.append("Invalid key, {} -> {}".format(record, key))
    
    # Were there any errors in the config?
    if len(errors) > 0:
        print("WARNING: INVALID CONFIG")
        print("\tThe configuration file located at {} has errors!".format("{CONFIG PATH}"))
        for error in errors:
            print("\tERROR:\t"+error)
        exit(1)
    else:
        print("STATUS: CONFIG OK")
        return config

# Function for killing apps
def killApp(_violationInfo):
    killed = True
    try:
        os.kill(_violationInfo['processIdentifier'], signal.SIGKILL)
    except:
        killed = False
        #print("ERROR: Someone else killed pid "+str(_violationInfo['processIdentifier']))
    return killed

# Performs actions on a per-app basis
def takeAction(_violationInfo):
    # Caller(s) for verbose logging
    caller = inspect.stack()[1][3]
    callers = {
        "killRunningApps": "EXG",
        "prepare": "NEW"
    }
    
    # We should assume the app killed
    kill  = True
    
    # Why was the app killed? Useful for debugging on the server
    _violationInfo['reasoning'] = {}
    
    # Extract the options
    options = config[_violationInfo['matchedRegex']]
    
    # AppBlocker Core Config Options
    if KeyExists(options, 'allowedPath'):
        if _violationInfo['appPath'] == options['allowedPath']:
            kill = False
        else:
            _violationInfo['reasoning']['pathMismatch'] = True
    if KeyExists(options, 'allowedUsers'):
        if currentUser in options['allowedUsers']:
            kill = False
        else:
            _violationInfo['reasoning']['userMismatch'] = True
       
    ## Should we kill the app?
    if kill == True:
        # Kill the app
        killedStatus = killApp(_violationInfo)
        
        # Add the app to the queue
        violations.append(_violationInfo)
        
        # Log the successful termination of violation
        k = str(killedStatus)[0] # For killed status
        if not KeyExists(config, _violationInfo['bundleIdentifier']):
            er = 'R'
        else:
            er = 'E'
        
        print("STATUS: K{}-{}-{}{} -> {}".format(k, callers[caller], _violationInfo['processIdentifier'], er, _violationInfo['bundleIdentifier']))

        # Are we going to delete the app?
        if KeyExists(options, 'deleteBlockedApplication'):
            if options['deleteBlockedApplication'] is True:
                try:
                    shutil.rmtree(_violationInfo['appPath'])
                except OSError, e:
                    print ("Error: %s - %s." % (e.filename,e.strerror))

        # Notify the user, if specified
        if KeyExists(options, 'customAlert'):
            ## DEFAULTS
            message = "The application \"{}\" has been blocked by IT".format(_violationInfo['appName'])
            informativeText = "Contact your administrator for more information"
            iconPath = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns"
            proceedButton = ["OK"]
            ## DEFAULTS
            
            ## ALERT FORMATTING ##
            class CustomAlertVars:
                def __init__(self):
                    # Approved Global Variables
                    approvedGlobals = ['currentUser']
                    for i in approvedGlobals:
                        setattr(self, i, eval(i))
                    
                    # Config Variables (Keys)
                    for key in options.keys():
                        setattr(self, key, options[key]) #arr = [str(r) for r in arr]
                                        
                    # Violation Information Parameters
                    for key in _violationInfo.keys():
                        setattr(self, key, _violationInfo[key])
                        
            MV = CustomAlertVars()
            ## ALERT FORMATTING ##
                        
            # So we don't call every time
            key = options['customAlert']
            if KeyExists(key, 'message'):
                _message = message
                try:
                    message = Template(key['message']).substitute(vars(MV))
                except KeyError:
                    message = _message
                    print "ERROR: There are invalid variables in your message contents!"
            else:
                message = message.format()
            if KeyExists(key, 'informativeText'):
                _informativeText = informativeText
                try:
                    informativeText = Template(key['informativeText']).substitute(vars(MV))
                except KeyError:
                    informativeText = _informativeText
                    print "ERROR: There are invalid variables in your informative text contents!"
            if KeyExists(key, 'iconPath') and os.path.exists(key['iconPath']):
                iconPath = key['iconPath']
            if KeyExists(key, 'proceedButton'):
                proceedButton = key['proceedButton']

            del MV
            alert(iconPath, message, informativeText, proceedButton)
        
def killRunningApps(workspace):
    running_apps = workspace.runningApplications()
    for app in running_apps:
        match = re.match(blockedBundleIdentifiersCombined, str(app.bundleIdentifier()))
        if match:
            exactBundleIDOrWildcard = re.sub(r"\(|\)", '', blockedBundleIdentifiersCombined).split("|")[match.lastindex - 1]
            
            # We call the takeaction method, with the additions below
            violationInfo = {
                "matchedRegex": exactBundleIDOrWildcard,
                "userName": AppKit.NSProcessInfo.processInfo().userName(),
                "appName": app.localizedName(),
                "bundleIdentifier": app.bundleIdentifier(),
                "processIdentifier": app.processIdentifier(),
                "appPath": app.bundleURL().path() # Not NSURL
            }
            
            # Take action upon the app
            takeAction(violationInfo)

## BEFORE ANYTHING ELSE
# Attempt to parse the config
config = {}
if os.path.exists(config_file):
    config = parseConfig(config_file)
else:
    exit(1)
## BEFORE ANYTHING ELSE

## TESTING ##
def prepare(app):
    bundleIdentifier = app.bundleIdentifier()
    
    # Check if launched app's bundle identifier matches any 'blockedBundleIdentifiers'
    match = re.match(blockedBundleIdentifiersCombined, str(bundleIdentifier))
    
    if match:
        # Get the exact bundle identifier or regex that matched
        exactBundleIDOrWildcard = re.sub(r"\(|\)", '', blockedBundleIdentifiersCombined).split("|")[match.lastindex - 1]

            # Store the violation information
        violationInfo = {
            "matchedRegex": exactBundleIDOrWildcard,
            "userName": AppKit.NSProcessInfo.processInfo().userName(),
            "appName": app.localizedName(),
            "bundleIdentifier": app.bundleIdentifier(),
            "processIdentifier": app.processIdentifier(),
            "appPath": app.bundleURL().path() # Not NSURL
        }
                
        # Take action upon the application
        takeAction(violationInfo)

## TESTING ##


# Define callback for notification
class AppLaunch(AppKit.NSObject):
    #def appLaunched_(self, notification):
    def observeValueForKeyPath_ofObject_change_context_(self, path, object, changeDescription, context):
        if AppKit.NSKeyValueChangeNewKey == 'new':
            prepare(object.runningApplications()[-1])
                
# Define alert class
class Alert(object):

    def __init__(self, messageText):
        super(Alert, self).__init__()
        self.messageText = messageText
        self.informativeText = ""
        self.buttons = []

    def displayAlert(self):
        alert = AppKit.NSAlert.alloc().init()
        alert.setMessageText_(self.messageText)
        alert.setInformativeText_(self.informativeText)
        alert.setAlertStyle_(AppKit.NSInformationalAlertStyle)
        for button in self.buttons:
            alert.addButtonWithTitle_(button)

        if os.path.exists(self.alertIconPath):
            icon = AppKit.NSImage.alloc().initWithContentsOfFile_(self.alertIconPath)
            alert.setIcon_(icon)

        # Don't show the Python rocketship in the dock
        AppKit.NSApp.setActivationPolicy_(1)

        AppKit.NSApp.activateIgnoringOtherApps_(True)
        alert.runModal()

# Define an alert
def alert(iconPath, message="Default Message", info_text="", buttons=["OK"]):    
    ap = Alert(message)
    ap.alertIconPath = iconPath
    ap.informativeText = info_text
    ap.buttons = buttons
    ap.displayAlert()

# Combine all bundle identifiers and regexes to one
blockedBundleIdentifiersCombined = "(" + ")|(".join(config.keys()) + ")"

# Register for 'NSWorkspaceDidLaunchApplicationNotification' notifications
workspace = Foundation.NSWorkspace.sharedWorkspace() # For runnning apps
#nc = workspace.notificationCenter()
AppLaunch = AppLaunch.new()
#nc.addObserver_selector_name_object_(AppLaunch, 'appLaunched:', 'NSWorkspaceWillLaunchApplicationNotification',None) #NO MORE
workspace.addObserver_forKeyPath_options_context_(AppLaunch, 'runningApplications', AppKit.NSKeyValueObservingOptionNew, 0)

# Kill existing applications
killRunningApps(workspace)

# Launch "app" (kills newly launched apps)
try:
    print "PID OF THIS INSTANCE: "+str(AppKit.NSProcessInfo.processInfo().processIdentifier())
    AppHelper.runConsoleEventLoop().run() # RUN!
except KeyboardInterrupt:
    os.kill(AppKit.NSProcessInfo.processInfo().processIdentifier(), SIGNAL.KILL)
