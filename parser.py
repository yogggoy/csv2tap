#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" """

import os
import sys
import logging
from csv2tap import JTAG_TAP

class JTAG_Parser(object):
    '''
        parse CSV collumn:
        SimTime
        JTAG_TRST_N
        JTAG_TCK
        JTAG_TMS
        JTAG_TDI
        JTAG_TDO
        SERV_RSTI_N
    '''

    def __init__(self):
        '''  '''
        self.DEBUG = False
        self.logging = logging.getLogger('main.'+self.__class__.__name__)
        self.array = []
        self.tap = JTAG_TAP()

    def read_file(self, file_name='simvision.csv'):
        ''' read file to array '''

        if file_name == None:
            return self.array

        with open(file_name, 'r') as f:
            for l in f:
                x = l.split(',')

                SimTime     = x[0].strip()
                JTAG_TRST_N = x[1].strip()
                JTAG_TCK    = x[2].strip()
                JTAG_TMS    = x[3].strip()
                JTAG_TDI    = x[4].strip()
                JTAG_TDO    = x[5].strip()
                SERV_RSTI_N = x[6].strip()

                self.array.append(
                    (SimTime, JTAG_TRST_N, JTAG_TCK, JTAG_TMS, JTAG_TDI, JTAG_TDO, SERV_RSTI_N)
                )
        return self.array

    def clear_buf(self):
        self.array = []

    def get_vector(self, i):
        ''' '''
        vect = self.array[i]
        JTAG_TRST_N = 0 if (vect[1] in ('x', 'z', '0')) else 1
        JTAG_TCK    = 0 if (vect[2] in ('x', 'z', '0')) else 1
        JTAG_TMS    = 1 if (vect[3] in ('x', 'z', '1')) else 0
        JTAG_TDI    = 1 if (vect[4] in ('x', 'z', '1')) else 0
        JTAG_TDO    = vect[5]
        SERV_RSTI_N = 0 if (vect[6] in ('x', 'z', '0')) else 1

        return {
            'JTAG_TRST_N' : JTAG_TRST_N,
            'JTAG_TCK' : JTAG_TCK,
            'JTAG_TMS' : JTAG_TMS,
            'JTAG_TDI' : JTAG_TDI,
            'JTAG_TDO' : JTAG_TDO,
            'SERV_RSTI_N' : SERV_RSTI_N
        }

    def play(self, frame=None):
        if frame == None:
            _r = len(self.array)
        else:
            _r = frame

        for i in range(1,_r):
            prev_vect = self.get_vector(i-1)
            vect = self.get_vector(i)

            if vect['JTAG_TCK'] != prev_vect['JTAG_TCK']:
                self.tap.next_state_vect(vect)


if __name__ == '__main__':

    formatter = '%(levelname)-6s: %(lineno)-4d: %(message)s' # debug
    formatter = '%(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=formatter)
    logger = logging.getLogger('main')

    player = JTAG_Parser()
    if len(sys.argv) > 1:
        if (os.path.isfile(sys.argv[1])):
            player.read_file(sys.argv[1])
        else:
            logger.info("file not found : ["+ sys.argv[1]+"]")
    else:
        player.read_file()

    player.play()
    player.clear_buf()
