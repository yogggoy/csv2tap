#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" csv to JTAG TAP """

import logging, sys

class JTAG_TAP(object):
    def __init__(self, init_state=1):

        self.logging = logging.getLogger('main.'+self.__class__.__name__)
        self.TAP_STATE = {
            1  : 'Test_Logic_Reset',
            2  : 'Run_Test_IDLE',
            3  : 'Select_DR_Scan',
            4  : 'Capture_DR',
            5  : 'Shift_DR',
            6  : 'Exit1_DR',
            7  : 'Pause_DR',
            8  : 'Exit2_DR',
            9  : 'Update_DR',
            10 : 'Select_IR_Scan',
            11 : 'Capture_IR',
            12 : 'Shift_IR',
            13 : 'Exit1_IR',
            14 : 'Pause_IR',
            15 : 'Exit2_IR',
            16 : 'Update_IR',
        }
        # event - tms state         0                1
        self.event = {
            'Test_Logic_Reset' : ('Run_Test_IDLE', 'Test_Logic_Reset' ),
            'Run_Test_IDLE'    : ('Run_Test_IDLE', 'Select_DR_Scan'   ),
            'Select_DR_Scan'   : ('Capture_DR',    'Select_IR_Scan'   ),
            'Capture_DR'       : ('Shift_DR',      'Exit1_DR'         ),
            'Shift_DR'         : ('Shift_DR',      'Exit1_DR'         ),
            'Exit1_DR'         : ('Pause_DR',      'Update_DR'        ),
            'Pause_DR'         : ('Pause_DR',      'Exit2_DR'         ),
            'Exit2_DR'         : ('Shift_DR',      'Update_DR'        ),
            'Update_DR'        : ('Run_Test_IDLE', 'Select_DR_Scan'   ),
            'Select_IR_Scan'   : ('Capture_IR',    'Test_Logic_Reset' ),
            'Capture_IR'       : ('Shift_IR',      'Exit1_IR'         ),
            'Shift_IR'         : ('Shift_IR',      'Exit1_IR'         ),
            'Exit1_IR'         : ('Pause_IR',      'Update_IR'        ),
            'Pause_IR'         : ('Pause_IR',      'Exit2_IR'         ),
            'Exit2_IR'         : ('Shift_IR',      'Update_IR'        ),
            'Update_IR'        : ('Run_Test_IDLE', 'Select_DR_Scan'   ),
        }

        self.data_tdi = ''
        self.data_tdo = ''

        self.tdi_endian = 1
        self.tdo_endian = 1
        self.display_all_state = 0 # print every TMS, include duplicate
        self.display_only_data = 0 # print only data and I\D register state

        self.log_prefix = '' # prefix for output string

        self.state = self.TAP_STATE[init_state]
        self.logging.info(' . ' + str(self.get_state()))

    def TRST_state(self):
        ''' reset TAP controller '''
        self.data_tdi = ''
        self.data_tdo = ''
        self.state = 'Test_Logic_Reset'

    def set_endian(self, tdi_e, tdo_e):
        ''' set MSB/LSB type data display
            tdi_e, tdo_e - bool or int[1/0]
         '''
        self.tdi_endian = tdi_e
        self.tdo_endian = tdo_e

    def set_display_all_state(self, var):
        ''' display all TAP states, include repeated
            var - 1 - yes; 0 -no
        '''
        self.display_all_state = var

    def set_display_only_data(self, var):
        ''' print only data and I\D register state
            var - 1 - yes; 0 -no
        '''
        self.display_only_data = var

    def next_state(self, event):
        ''' display TAP state.
            event - TMS value
        '''
        _prev_state = self.state
        self.state = self.event[self.state][event]
        if (_prev_state != self.state) or (self.display_all_state):
            self.logging.info(self.log_prefix + str(self.get_state()))

    def next_state_vect(self, vect):
        ''' display TAP state and SHIFT I/D registers
        vect - {
            'SimTime'  : SimTime,
            'JTAG_TRST_N' : JTAG_TRST_N,
            'JTAG_TCK' : JTAG_TCK,
            'JTAG_TMS' : JTAG_TMS,
            'JTAG_TDI' : JTAG_TDI,
            'JTAG_TDO' : JTAG_TDO,
            'SERV_RSTI_N' : SERV_RSTI_N
        }
        '''
        _prev_state = self.state
        if vect['JTAG_TCK']:
            if not (vect['JTAG_TRST_N'] or vect['SERV_RSTI_N']):
                self.TRST_state()
                return

            ret = self.log_data_shift(vect)
            self.state = self.event[self.state][vect['JTAG_TMS']]

            if (self.display_only_data) and (not ret):
                return

            if (_prev_state != self.state) or (self.display_all_state):
                self.logging.info(self.log_prefix + str(self.get_state()))

    def log_data_shift(self, vect):
        ''' SHIFT I/D display '''

        tdi = vect['JTAG_TDI']
        tdo = vect['JTAG_TDO']

        if self.state in ('Shift_IR', 'Shift_DR'):
            self.data_tdi = (str(tdi) + self.data_tdi) if self.tdi_endian else (self.data_tdi + str(tdi))
            self.data_tdo = (str(tdo) + self.data_tdo) if self.tdo_endian else (self.data_tdo + str(tdo))

        if self.state in ('Exit1_DR', 'Exit1_IR'):
            self.logging.info('SimTime: '+vect['SimTime'])
            self.logging.info('TDI(' + str(len(self.data_tdi)) + '): ' + str(self.data_tdi))
            self.logging.info('TDO(' + str(len(self.data_tdo)) + '): ' + str(self.data_tdo))
            self.data_tdi = ''
            self.data_tdo = ''
            return 1
        return 0

    def get_state(self):
        ''' '''
        return self.state


if __name__ == '__main__':

    formatter = '%(levelname)-6s: %(lineno)-4d: %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=formatter)
    logger = logging.getLogger('main')

    tap = JTAG_TAP()

    x = [1,0,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0]
    for s in x:
        tap.next_state(s)
