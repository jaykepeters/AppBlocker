#!/usr/bin/env python
# AppFinder (InfoReader)
import json

with open('appdb.json') as json_file:
    data = json.load(json_file)

for bundleID in data:
    print(bundleID)
    if type(data[bundleID]) == list:
        counter = 0
        for appInfo in data[bundleID]:
            counter += 1
            print("\tInstance "+str(counter))
            for key in appInfo.keys():
                print("\t\t"+appInfo[key])
    else:
        for key in data[bundleID].keys():
            print("\t"+key+": "+data[bundleID][key])
