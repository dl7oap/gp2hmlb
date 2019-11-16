#!/usr/bin/env python3

'''
Author  : Andreas Puschendorf, DL7OAP
Version : 004
Date    : 2019-11-16

This script is plugged between gpredict and hamlib based on python 3.7
It is listing on port 4532 for gpredict frequencies
and it is sending frequencies and startsequences for ic9700 to port 4572 for hamlib

Usage: python3 gp2hmlb.py [type_of_satellite] [band_of_uplink]
gp2hmlb.py hast to be called with 2 parameter
first parameter is type of satellite. you can choose between FM, SSB, SIMPLEX, CW
second parameter is type of uplink. You can choose between 2M, 70CM, 23CM

1t step:    starting hamlib daemon on port 4572
    Linux:      rigctld -m 381 -r /dev/ic9700a -s 19200 -t 4572
    Windows:    rigctld -m 381 -r COM5 -s 19200 -t 4572
2t step:    starting gp2hmlb.py pythonscript
    Linux:      python3 gp2hmlb.py FM 70CM
    Windows:    python3 gp2hmlb.py FM 70CM
3t step:    start gepredict with a duplex trx on port 4532 and MAIN/SUB
'''


# TODO: when FM, then enable AFC on downlink, when not FM disable AFC (will be U AFC 1/0)
# TODO: when possible, disable in general start sequence DUP (hamlib command is missing)
#       fe fe a2 00 0F 10 fd  set DUP off (R None)
# TODO: are there satellites with USB uplink? when yes we have to split SSB parameter into LSB and USB


import socket
import time
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT_SERVER = 4532  # Port to listen on (non-privileged ports are > 1023)
PORT_CLIENT = 4572  # Port to listen on (non-privileged ports are > 1023)
SLEEP_TIME = 0.02   # Sleeping time for hamlib tcp connect. hamlib can not handle to much commands.


def sendCommandToHamlib(sock_hamlib, command):
    sock_hamlib.send(command)
    time.sleep(SLEEP_TIME)
    return sock_hamlib.recv(100).decode('utf-8')


def setStartSequenceGeneral(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'L SQL 0\n')
    sendCommandToHamlib(sock_hamlib, b'L AF 0\n')
    #sendCommandToHamlib(sock_hamlib, b'R None\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'L SQL 0\n')
    sendCommandToHamlib(sock_hamlib, b'L AF 0.15\n')


def setStartSequenceSSB(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M LSB 2400\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M USB 2400\n')


def setStartSequenceCW(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M CW 500\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M USB 2400\n')


def setStartSequenceFM(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')
    sendCommandToHamlib(sock_hamlib, b'U AFC 0\n')

    sendCommandToHamlib(sock_hamlib, b'C 670\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 1\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 0\n')
    sendCommandToHamlib(sock_hamlib, b'U AFC 1\n')


def setStartSequenceSimplex(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOB\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')
    sendCommandToHamlib(sock_hamlib, b'U AFC 0\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 0\n')
    sendCommandToHamlib(sock_hamlib, b'S 1 Main\n')
    sendCommandToHamlib(sock_hamlib, b'U AFC 1\n')


def loopSSBandFMandCW(sock_hamlib, up, dw):

    # set uplink frequency
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    b = bytearray()
    b.extend(map(ord, 'F ' + up + '\n'))
    sendCommandToHamlib(sock_hamlib, b)

    # set downlink frequency
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    b = bytearray()
    b.extend(map(ord, 'F ' + dw + '\n'))
    sendCommandToHamlib(sock_hamlib, b)


def loopSIMPLEX(sock_hamlib, up, dw):

    # only update of frequencies if PTT off
    if sendCommandToHamlib(sock_hamlib, b't\n')[0] == '0':

        # set uplink frequency
        sendCommandToHamlib(sock_hamlib, b'V VFOB\n')
        b = bytearray()
        b.extend(map(ord, 'F ' + up + '\n'))
        sendCommandToHamlib(sock_hamlib, b)

        # set downlink frequency
        sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
        b = bytearray()
        b.extend(map(ord, 'F ' + dw + '\n'))
        sendCommandToHamlib(sock_hamlib, b)


def getBandFromFrequency(frequency):
    band = '2M'
    if int(frequency) > 150000000:
        band = '70CM'
    if int(frequency) > 470000000:
        band = '23CM'
    return band


def activateCorrectUplinkBandInMain(sock_hamlib, type_of_uplink_band):
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    main_frequency = sendCommandToHamlib(sock_hamlib, b'f\n')
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sub_frequency = sendCommandToHamlib(sock_hamlib, b'f\n')

    if type_of_uplink_band == getBandFromFrequency(main_frequency):  # is uplink band in main -> nothing to do
        return
    elif type_of_uplink_band == getBandFromFrequency(sub_frequency):  # is uplink band in sub -> switch bands
        sendCommandToHamlib(sock_hamlib, b'G XCHG\n')
    else:  # is uplink band not in main and sub -> set band in main
        sendCommandToHamlib(sock_hamlib, b'V Main\n')
        if type_of_uplink_band == '23CM':
            sendCommandToHamlib(sock_hamlib, b'F 1295000000\n')
        if type_of_uplink_band == '70CM':
            sendCommandToHamlib(sock_hamlib, b'F 435000000\n')
        if type_of_uplink_band == '2M':
            sendCommandToHamlib(sock_hamlib, b'F 145900000\n')


def main():

    uplink = '0'
    downlink = '0'
    last_uplink = '0'
    last_downlink = '0'

    ###############################################
    # start sockets for gpredict und hamlib
    ###############################################

    # start tcp client
    try:
        sock_hamlib = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_hamlib.connect((HOST, PORT_CLIENT))
    except socket.error as e:
        print('Problem: ', e)
        print('INFO: connection refused error is most of the time that rigctld is not started on port 4572')
        print('use command "rigctl -m 381 -r /dev/ic9700a -s 19200 -t 4572"')

    # start tcp server
    sock_gpredict = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_gpredict.bind((HOST, PORT_SERVER))
    sock_gpredict.listen(1)

    ###############################################
    # satellite start sequence
    ###############################################

    if (len(sys.argv) == 3):
        type_of_satellite = sys.argv[1].upper()
        type_of_uplink_band = sys.argv[2].upper()

        if type_of_uplink_band not in ['70CM', '2M', '23CM']:
            print('ERROR: unknown uplink band type "' + type_of_uplink_band + '". Only 2M, 70CM and 23CM possible.')
            return

        activateCorrectUplinkBandInMain(sock_hamlib, type_of_uplink_band)

        if type_of_satellite == 'SSB':
            setStartSequenceSSB(sock_hamlib)
        elif type_of_satellite == 'CW':
            setStartSequenceCW(sock_hamlib)
        elif type_of_satellite == 'FM':
            setStartSequenceFM(sock_hamlib)
        elif type_of_satellite == 'SIMPLEX':
            setStartSequenceSimplex(sock_hamlib)
        else:
            print('ERROR: unkown satellite type "' + type_of_satellite + '". Only SSB, FM, SIMPLEX or CW possible.')
            return
        setStartSequenceGeneral(sock_hamlib)

    else:
        print('Usage: gp2hmlb.py [type_of_satellite] [band_of_uplink]')
        print('INFO: gp2hmlb.py hast to be called with 2 parameter')
        print('first parameter is type of satellite. you can choose between FM, SSB, SIMPLEX, CW')
        print('second parameter is type of Uplink. you can choose between 2M, 70CM')
        print('example: python3 gp2hmlb.py SSB 2M')
        return

    ###############################################
    # main loop
    ###############################################

    while True:
        conn, addr = sock_gpredict.accept()
        print('Connected by', addr)
        while 1:
            data = conn.recv(1000)
            print('### gpredict says : ' + data.decode('utf-8').replace('\n', ''))
            if not data: break
            if data[0] in [70, 73]:  # I, F
                # get downlink and uplink from gpredict
                cut = data.decode('utf-8').split(' ')
                if data[0] == 70:  # F
                    downlink = cut[len(cut)-1].replace('\n', '')
                if data[0] == 73:  # I
                    uplink = cut[len(cut)-1].replace('\n', '')
                print('last  = ' + last_uplink + ' / ' + last_downlink)
                print('fresh = ' + uplink + ' / ' + downlink)
                # only if uplink or downlink changed >0 10Hz Column, then update
                if (last_uplink[0:8] != uplink[0:8]) or (last_downlink[0:8] != downlink[0:8]):
                    if type_of_satellite in ['SSB', 'CW', 'FM']:
                        loopSSBandFMandCW(sock_hamlib, uplink, downlink)
                    if type_of_satellite == 'SIMPLEX':
                        loopSIMPLEX(sock_hamlib, uplink, downlink)

                    last_uplink = uplink
                    last_downlink = downlink
                conn.send(b'RPRT 0')  # Return Data OK to gpredict
            elif data[0] in [102, 105]:
                if type_of_satellite in ['SIMPLEX']:
                    conn.send(b'RPRT')
                else:
                    if data[0] == 102:  # f downlink
                        actual_sub_frequency = sendCommandToHamlib(sock_hamlib, b'f\n').replace('\n', '')
                        downlink = actual_sub_frequency
                        last_downlink = actual_sub_frequency
                        print('dial down: ' + actual_sub_frequency)
                        b = bytearray()
                        b.extend(map(ord, actual_sub_frequency + '\n'))
                        conn.send(b)
                    elif data[0] == 105:  # i uplink
                        # sendCommandToHamlib(sock_hamlib, b'V Main\n')
                        # actual_main_frequency = sendCommandToHamlib(sock_hamlib, b'f\n').replace('\n', '')
                        # #last_uplink = actual_main_frequency
                        # sendCommandToHamlib(sock_hamlib, b'V Sub\n')
                        # print('dial up: ' + actual_main_frequency)
                        # b = bytearray()
                        # b.extend(map(ord, actual_main_frequency + '\n'))
                        # conn.send(b)
                        conn.send(b'RPRT')
            elif data[0] == 116:  # t ptt
                conn.send(b'0')
            else:
                conn.send(b'RPRT 0')  # Return Data OK to gpredict
        print('connect closed')
        conn.close()


main()

