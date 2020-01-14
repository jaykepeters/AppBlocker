#!/usr/bin/env python
## File Date Getter 
## DATE FORMAT: MMDDYYHHMM
def getOutputFileDate(filename):
    # Month map
    monthMap = {
        "01": "January", "02": "February", "03": "March",
        "04": "April", "05": "May", "06": "June",
        "07": "July", "08": "August", "09": "September",
        "10": "October", "11": "November", "12": "December"
    }

    # ERROR CHECKING
    timestamp = ''.join(i for i in filename if i.isdigit())
    if len(timestamp) is not 10:
        return

    # Extract data parameters, one by one
    month = monthMap[timestamp[0:2]]
    day = int(timestamp[2:4])
    year = str(20)+timestamp[4:6]
    time = ":".join([timestamp[6:8], timestamp[8:10]])

    # Some conditionals for suffixes
    if day is 1 or day is 31:
        suffix = "st"
    if day is 2:
        suffix = "nd"
    if day is 3:
        suffix = "rd"
    if day <= 30:
        suffix = "th"

    # DEFAULT
    ampm = "AM" # HOW ABOUT 12 AM?
    if int(time.split(":")[0]) >= 12:
        hours, minutes = time.split(":")
        hours = int(hours) - 12
        time = ":".join([str(hours), minutes])
        ampm = "PM"
    
    # Exact, on the dot
    if int(time.split(":")[0]) == 0:
        minutes = time.split(":")[1]
        time = ":".join([str(12), minutes])
    
    # Now, return a string
    return "{} {}{}, {} at {} {}".format(month, day, suffix, year, time, ampm)

if __name__ == "__main__":
   # print getOutputFileDate("0101202359") # January 1st, 2020 at 23:59
    print getOutputFileDate("appDB_0113202251.json")
    print getOutputFileDate("errors_0113202303.json")
    print getOutputFileDate("appDB_0114200030.json")
    print getOutputFileDate("errors_0114200032.json")
