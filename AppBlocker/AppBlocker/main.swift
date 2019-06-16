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
        print("Initializing Observer")
        nc.addObserver(self, selector: #selector(notificationDidTrigger), name: NSWorkspace.willLaunchApplicationNotification, object: nil)
    }
    
    @objc func notificationDidTrigger(notification: Notification) {
        print("Notification triggered ", notification.userInfo)
    }
}

// Create a new observer
let obj = Observer()

// Keep the app running
CFRunLoopRun()
