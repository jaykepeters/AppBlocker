//
//  main.swift
//  AppBlocker
//
//  Created by jayke on 6/16/19.
//  Copyright © 2019 Jayke Peters. All rights reserved.
//

// Add a get process path using pid method
// Add a delete applicationUsingPID method
// Combine both of these?
// Restrict certain apps to a specific launch path (system prefrences)
// Restrict certain apps to a set or group of users

import Foundation
import AppKit

// New Shared Notification Center Object
let nc = NSWorkspace.shared.notificationCenter

// Observer class
class Observer {
    init() {
        nc.addObserver(self, selector: #selector(notificationDidTrigger), name: NSWorkspace.willLaunchApplicationNotification, object: nil)
        killRunningApps()
    }
  
    // Blacklisted Process Names
    // BUNDLE IDENTIFIERS (CORRECTION)
    let blackListedProcessNames = [
        "com.apple.AppStore",
        "com.apple.Music",
        "com.apple.Mail",
        "com.apple.FaceTime",
        "com.apple.systempreferences"
    ]
    
    // Kill Process Method
    private func killProcess(_ processId: Int) {
        if let process = NSRunningApplication.init(processIdentifier: pid_t(processId)) {
            print("Killing \(processId): \(String(describing: process.localizedName!))")
            process.forceTerminate()
        }
    }
    
    // Kill Existing Applications Method
    private func killRunningApps() {
        let runningApplications = NSWorkspace.shared.runningApplications
        for currentApplication in runningApplications.enumerated() {
            let runningApplication = runningApplications[currentApplication.offset]
            
            if (runningApplication.activationPolicy == .regular) { // normal macOS application
                if (blackListedProcessNames.contains(runningApplication.bundleIdentifier!)) {
                    killProcess(Int(runningApplication.processIdentifier))
                }
            }
        }
    }
    
    // Application Launch Method
    @objc func notificationDidTrigger(notification: Notification) {
        // NOTIFICATION USER INFORMATION
        print("Launched:", notification)
        let userInfo = notification.userInfo
        
        if let processBundleIdentifier: String = notification.userInfo?["NSApplicationBundleIdentifier"] as? String {
            if let processId = userInfo?["NSApplicationProcessIdentifier"] as? Int {
                if (blackListedProcessNames.contains(processBundleIdentifier)) {
                    killProcess(processId)
                }
            }
        }
    }
}

//let thePath = getRootProcessPathUsingPID(546)

print(String(cString: getRootProcessPathUsingPID(546)))

// Create a new observer
let obj = Observer()

// Keep the tool running
CFRunLoopRun()
