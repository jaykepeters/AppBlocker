# keysToRemove: remove duplicates, or ignore such as appPath... All other appInfo parameters same, remove dupes...
# exclude /Library/Widgets and /Library/Scripts, none have cfbids
# note that automator apps can be blocked by wildcarding com.apple.automator.*
# FIX REGEX: ORGIGINAL FROM ERICK ALREADY DID THAT!!!
Bundle ID Selection List
- "com.parallels.desktop.installer":{},
# Installing and Loading the Launch Daemon
1. Place net.jayke.AppBlocker.plist into /Library/LaunchDaemons/
2. `sudo chmod 644 /Library/LaunchDaemons/net.jayke.AppBlocker.plist`
3. `sudo chown root:wheel /Library/LaunchDaemons/net.jayke.AppBlocker.plist`
4. `sudo launchctl load -w /Library/LaunchDaemons/net.jayke.AppBlocker.plist`

# AppBlocker 2
Keeping your users on task!

