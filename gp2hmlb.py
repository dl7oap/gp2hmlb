#!/usr/bin/env python3

'''
Author  : Andreas Puschendorf, DL7OAP
Version : 003
Date    : 2019-11-15

This script is plugged between gpredict and hamlib based on python 3.7
It is listing on port 4532 for gpredict frequencies
and it is sending frequencies and startsequences for ic9700 to port 4572 for hamlib

Usage: python3 gp2hmlb.py [type_of_satellite] [band_of_uplink]
gp2hmlb.py hast to be called with 2 parameter
first parameter is type of satellite. you can choose betwween FM, SSB, SIMPLEX, CW
second parameter is type of uplink. you can choose between 2M, 70CM

1t step:    starting hamlib daemon on port 4572
    Linux:      rigctld -m 381 -r /dev/ic9700a -s 19200 -t 4572
    Windows:    rigctld -m 381 -r COM5 -s 19200 -t 4572
2t step:    starting gp2hmlb.py pythonscript
    Linux:      python3 gp2hmlb.py FM 70CM
    Windows:    python3 gp2hmlb.py FM 70CM
3t step:    start gepredict with a duplex trx on port 4532 and MAIN/SUB
'''


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


def startSequenceSSB(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M LSB 2400\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M USB 2400\n')


def startSequenceCW(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M CW 500\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M CW 500\n')


def startSequenceFM(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    sendCommandToHamlib(sock_hamlib, b'C 670\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 1\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V Sub\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 0\n')


def startSequenceSimplex(sock_hamlib):

    # define uplink
    sendCommandToHamlib(sock_hamlib, b'V Main\n')
    sendCommandToHamlib(sock_hamlib, b'V VFOB\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'S 0 Main\n')

    # define downlink
    sendCommandToHamlib(sock_hamlib, b'V VFOA\n')
    sendCommandToHamlib(sock_hamlib, b'M FM 15000\n')
    sendCommandToHamlib(sock_hamlib, b'U TONE 0\n')
    sendCommandToHamlib(sock_hamlib, b'S 1 Main\n')


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


def main():

    uplink = '0'
    downlink = '0'
    last_uplink = '0'
    last_downlink = '0'
    type_of_satellite = 'FM'

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

        if type_of_uplink_band not in ['70CM','2M']:
            print('ERROR: unkown uplink band type "' + type_of_uplink_band + '". Only 2M and 70CM possible.')
            return

        # exchange 2m / 70cm when wrong band is active in main for uplink
        sendCommandToHamlib(sock_hamlib, b'V Main\n')
        actual_main_frequency = sendCommandToHamlib(sock_hamlib, b'f\n')
        if ((type_of_uplink_band == '70CM') and (actual_main_frequency[0:2] == '14'))  \
                or ((type_of_uplink_band == '2M') and (actual_main_frequency[0:1] == '4')):
            sendCommandToHamlib(sock_hamlib, b'G XCHG\n')

        if type_of_satellite == 'SSB':
            startSequenceSSB(sock_hamlib)
        elif type_of_satellite == 'CW':
            startSequenceCW(sock_hamlib)
        elif type_of_satellite == 'FM':
            startSequenceFM(sock_hamlib)
        elif type_of_satellite == 'SIMPLEX':
            startSequenceSimplex(sock_hamlib)
        else:
            print('ERROR: unkown satellite type "' + type_of_satellite + '". Only SSB, FM, SIMPLEX or CW possible.')
            return
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
                    downlink = cut[2].replace('\n', '')
                if data[0] == 73:  # I
                    uplink = cut[2].replace('\n', '')
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

