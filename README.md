Author  : Andreas Puschendorf, DL7OAP
Date    : 2019-11-24


# General

This script is plugged between gpredict and hamlib based on python 3.7.
It is listing on port 4532 for gpredict frequencies
and it is sending frequencies and startsequences for ic9700 to port 4572 for hamlib

The main reason for this plugin is to solve https://github.com/csete/gpredict/issues/181
so i can use ICOM ic9700 with gepredict and linux. The script is a alphaversion and should
help to get a better understanding how the startsequence and the loop have to be develop
so gpredict can be fixed for ic9700. It is also a testplattform to change fast the
used hamlib commands to play around with the behavior of the ic9700 and hamlib.

And it fix not only the problem with ic9700 but also with ic9100 and ic910.
https://github.com/csete/gpredict/issues/42
So reports for ic9100 and ic910 are also welcome.
First users already give feedback for ic910. the script works for them, too.
On 22th November there was a bigger update of hamlib https://github.com/Hamlib/Hamlib/pull/143
which enables a lot of hamlib commands for all three icom transceivers. So only the "split-problem" for
all three transceivers with hamlib has left and will be fixed hopefully soon.

# Usage details

gp2hmlb.py has to be called with 2 parameter

Usage: python3 gp2hmlb.py [type_of_satellite] [band_of_uplink]

1. Parameter is type of satellite. You can choose between FM, SSB, USB, SIMPLEX, CW
2. Parameter is type of uplink. You can choose between 2M, 70CM, 23CM


# Hints

Update rate in gpredict:
- For SIMPLEX and FM satellites i use an update rate of 10 seconds in gpredict. This is more then enough for FM.
This script will turn on AFC function for FM  on the downlink of ic9700, this eleminate, too, the doppler effect.
But a update rate of ~180ms in gpredict will work for FM and SIMPLEX.


- For SSB/CW i use an update rate between 250ms and 800ms. So cw signals will be ok with 500ms.
When you using the main dail to change the frequency 2000ms feels a little bit long. Because you have
to wait until gpredict have catch the new downlink frequency and the new matching update frequency is
send to ic9700. You have to play around with this :)
But a update rate of ~30ms in gpredict will work for SSB/CW, too, with this script.

The pythonscript will only send necessary updates, to calm down the display.
Only frequency shift greater then 10 Hz will be send to the transceiver.

At start the script always set:
* with parameter SSB the uplink in LSB and the downlink in USB. Most common satellites should work with this
* with parameter USB it will set uplink to USB and downlink to LSB
* with parameter FM subtone 670 will be activated on uplink
* starting with CW the uplink is mode CW and the downlink will be USB
* the script try to turn of repeater shifts (DUP+, DUP-)
* it sets SQL to open on uplink and downlink
* it will set AF level to 0 on TX and to 0.09 on RX


# Requirements

* gpredict version 2.3.* (older should also possible)
* hamlib 3.3 (i'm using 4.0 daily snapshot of 22th Nov 2019 http://n0nb.users.sourceforge.net)
* python 3.7 (python 2.* will not work)


# Starting order

1. starting hamlib daemon on port 4572
    * Linux:      rigctld -m 381 -r /dev/ic9700a -s 19200 -t 4572
    * Windows:    rigctld -m 381 -r COM5 -s 19200 -t 4572
2. starting gp2hmlb.py pythonscript
    * Linux:      python3 gp2hmlb.py FM 70CM
    * Windows:    python3 gp2hmlb.py FM 70CM
3. start gpredict with a duplex trx on port 4532 and MAIN/SUB