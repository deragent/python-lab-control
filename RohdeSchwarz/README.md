# Rohde & Schwarz Interface Scripts

## RTM3000
This directory contains an interface class `RTM3000` for the class of Rohde & Schwarz with the same name. This class support connection to an RTM device over TCP/IP, by using a raw IP socket. This means that PyVisa is not needed for interfacing the instrument. The RTM device is controlled via SCPI commands (see the RTM3000 manual).

The directory also contains the `RTM3000Acquire.py` script for acquiring the data from the RTM device, each time a trigger is received. The command line paramters of this script are as follows:

    usage: RTM3000Acquire.py [-h] -o OUTPUT [-i IP] [-p PORT]
                             [-c {1,2,3,4} [{1,2,3,4} ...]]

    Acquire a waveform on every trigger.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output Folder, needs to exist! (default: None)
      -i IP, --ip IP        IP of the RTM device. (default: 192.168.1.2)
      -p PORT, --port PORT  SCPI / Remote command port of the RTM device.
                            (default: 5025)
      -c {1,2,3,4} [{1,2,3,4} ...], --channels {1,2,3,4} [{1,2,3,4} ...]
                            The channels for which the data should be downloaded
                            from the RTM device. (default: [1, 2])

The script does not do any channel configuration on the oscilloscope, so the necessary channels need to be activated and configured by hand. The data is downloaded and saved in TAB separated data files, in the folder provided by the `-o` argument.

**Notes:**
  - The output folder needs to exist / is not created by the script.
  - Data files will be overwritten if the script is called multiple times with the same output folder.
  - If a channel is specified (using the `-c` argument) which is not active, the download will hang forever.

### Dependencies
- python3
- numpy
