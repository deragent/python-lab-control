#!/usr/bin/env python
#-*- coding:utf-8 –*-

import sys
import datetime
import numpy as np
import argparse

from RTM3000 import RTM3000

# Create the command line arguments
parser = argparse.ArgumentParser(
    description='Acquire a waveform on every trigger.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument("-o", "--output", required=True, help='Output Folder, needs to exist!')
parser.add_argument("-i", "--ip", default="192.168.1.2", help="IP of the RTM device.")
parser.add_argument("-p", "--port", type=int, default=5025, help="SCPI / Remote command port of the RTM device.")
parser.add_argument("-c", "--channels", type=int, nargs="+", default=[1, 2], choices=range(1,5), help="The channels for which the data should be downloaded from the RTM device.")
args = parser.parse_args()

# Init the RTM device connection
rtm = RTM3000(args.ip, args.port)

# Query for the RTM device ID
print(rtm.query("*IDN?", True))

# Configure all channels to record all the data in the buffer
for ch in args.channels:
    rtm.query("CHAN%i:DATA:POIN MAX"%(ch))

NFile = 0

# Write information to a log.txt file
with open(args.output + "/log.txt", 'a') as log:

    while True:
        # Wait for the next trigger on the RTM
        rtm.waitForTrigger()
        print("Trigger")

        # Log the approximate trigger time
        log.write("--------------------------------\n")
        log.write("Triggered at %s\n"%(str(datetime.datetime.now())))

        # Download all the data
        data = [None]
        for ch in args.channels:
            print("Download CH%i"%(ch))
            time, values = rtm.downloadChannel(ch)
            data.append(values)
        data[0] = time

        data = np.array(data)


        # Write the data to a file
        file = args.output + "/Data_%i.tsv"%(NFile)
        np.savetxt(file, data.T, delimiter='\t')

        NFile += 1

        log.write("Wrote data to file: [%s]\n"%(file))
