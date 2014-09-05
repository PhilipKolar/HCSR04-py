HCSR04-py
=========

Data collector for the HC-SR04 ultrasonic sensor, for use with a Raspberry Pi. Should work with all 3 models of the RPi (A, B, B+) but has has only been tested on the model B.

The main script to see here is usonic.py. It will run for one sensor and write data to a file, as well as to screen if in verbose mode. To see all the options (e.g. Measurement rate, echo/trigger pins, time-to-run, etc.) for running the script you may execute:

    python usonic.py -h

There are also some other miscellaneous scripts that are unnecessary to the functionality of usonic.py. echo-monitor.py and trigger.py are used for manualling observing/looking at trigger and echo functions (useful for testing if two sensors interfere with each other, activate trigger.py on one and echo-monitor.py on the other). The other is analyse-data.py which will compute various statistics from the data dumps usonic.py generates and place them in a new folder named "analysis".

This set of scripts was part of the data collection I did for my 2014 Honours project, for which my main suite of programs can be found at https://github.com/PhilipKolar/SensorSuite.
