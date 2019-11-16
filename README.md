Author  : Andreas Puschendorf, DL7OAP
Date    : 2019-11-15


General 
#######

This script is plugged between gpredict and hamlib based on python 3.7.
It is listing on port 4532 for gpredict frequencies
and it is sending frequencies and startsequences for ic9700 to port 4572 for hamlib

the main reason for this plugin is to solve https://github.com/csete/gpredict/issues/181 
so i can use ICOM ic9700 with gepredict and linux. the script is a alphaversion and should 
help to get a better understanding how the startsequence and the loop have to be develop
so gpredict can be fixed for ic9700. it is also a testplattform to change fast the 
used hamlib commands to play around with the behavior of the ic9700 and hamlib.

And it should not fix only the problem with ic9700 but also with ic9100 and ic910.
https://github.com/csete/gpredict/issues/42
so reports for ic9100 and ic910 are also welcome.


Detail
######

Usage: python3 gp2hmlb.py [type_of_satellite] [band_of_uplink]

gp2hmlb.py hast to be called with 2 parameter
first parameter is type of satellite. you can choose between FM, SSB, SIMPLEX, CW
second parameter is type of uplink. you can choose between 2M, 70CM


Hints
#####
for SIMPLEX and FM satellits i use an update rate of 10000ms in gpredict. this is enough.
you can turn on the AFC function of ic9700, this can also eleminate a lot of the doppler effect.

for SSB/CW i use an update rate between 800ms and 2000ms. so cw signals will be ok with 2000ms. 
when you using the main dail to change the frequency 2000ms feels a little bit long. because you have
to wait until gepredict have catch the new downlink frequency and the new matching update frequency is
send to ic9700. you have to play around with this :)

this script always starts the uplink in LSB and the downlik in USB. i think most of the common satellites
can be worked with this, but when not we have to enhance the parameter set.


Requirements
############

- gepredict version 2.3.* (older should also possible)
- hamlib 3.3 (i'm using 4.0 daily snapshot of 9th Nov 2019 http://n0nb.users.sourceforge.net)
- python 3.7 (python 2.* should not work correct)


Starting
########

1t step:    starting hamlib daemon on port 4572
    Linux:      rigctld -m 381 -r /dev/ic9700a -s 19200 -t 4572
    Windows:    rigctld -m 381 -r COM5 -s 19200 -t 4572
2t step:    starting gp2hmlb.py pythonscript
    Linux:      python3 gp2hmlb.py FM 70CM
    Windows:    python3 gp2hmlb.py FM 70CM
3t step:    start gepredict with a duplex trx on port 4532 and MAIN/SUB
'''gp2hmlib.py is a plugin between gpredict and hamlib to use and test ic9700 with gpredict





