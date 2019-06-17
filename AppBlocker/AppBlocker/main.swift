//
//  main.swift
//  AppBlocker
//
//  Created by jayke on 6/16/19.
//  Copyright © 2019 Jayke Peters. All rights reserved.
//

import Foundation
import AppKit

// New Shared Notification Center Object
let nc = NSWorkspace.shared.notificationCenter

// Observer class
class Observer {
    init() {
        nc.addObserver(self, selector: #selector(notificationDidTrigger), name: NSWorkspace.willLaunchApplicationNotification, object: nil)
    }
  
    // Blacklisted Process Names
    let blackListedProcessNames = ["com.apple.AppStore", "com.apple.Terminal"]
    
    // Kill Process Method
    private func killProcess(_ processId: Int) {
        if let process = NSRunningApplication.init(processIdentifier: pid_t(processId)) {
            print("Killing \(processId): \(String(describing: process.localizedName!))")
            process.forceTerminate()
        }
    }
    
    // Application Launch Method
    @objc func notificationDidTrigger(notification: Notification) {
        // NOTIFICATION USER INFORMATION
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

// Create a new observer
let obj = Observer()

// Keep the tool running
CFRunLoopRun()
