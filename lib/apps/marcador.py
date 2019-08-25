"""
@author: eocampo
 This program
    1) Checks connectivity to the biometric clock. (ping)
    2) Resets the biometric clock.
    3) Actions : reboot      :  Generate Config File, invoke reboot prog.
                 get_data:   :  Generate Config File, invoke get_data prog.
                 ping_reboot :  if pings fail. reboot and get_data.
    4) This module only works with SQLLite, some minor changes to work with other DB engines.
"""
__version__ = '20181113'

import sys
import os
import time

from datetime import datetime

import proc.process    as p
import utils.fileutils as fu
import utils.netutils  as nu
import utils.strutils  as su

from datastore.dbutil  import DBMYSQLOVERSSH
from datastore.dbutil  import DBMYSQL

from apps.mksbase        import _MksBaseApp
from statements.marcador import _SQLMarcador
from dependences.zkutils import ZKUtil


current_date = datetime.now().strftime('%Y%m%d')

class Marcador(_MksBaseApp):

    def __init__(self):

        super(Marcador, self).__init__()
        self.exitOnError = False

        # config vars CFG file
        self.db_dsn  = ''
        self.db_host = ''
        self.db_port = ''
        self.db_user = ''
        self.db_pswd = ''
        self.db_name = ''

        self.mail_sender  = ''
        self.mail_passwd  = ''
        self.mail_targets = ''

        self.company    = ''
        self.out_fn     = ''
        self.ip         = ''
        self.machine    = ''
        self.sleep_time = ''
        self.out_path   = ''
        self.path_move  = ''
        self.move_set   = ''
        self.end_time   = ''
        # config vars CFG file

        # Environmental variables:
        self.env_vars     = {}
        self.conn_ssh_str = {}
        self.conn_db_str  = {}

        self.typeSQL = 'gt-dt'
        self.evt     = {}
        self.vars    = []

        # Configuration variables:
        self.config = {
            'db_dsn'      :'',
            'db_host'     :'',
            'db_port'     :'',
            'db_user'     :'',
            'db_pswd'     :'',
            'db_name'     :'',
            'mail_sender' :'',
            'mail_passwd' :'',
            'mail_targets':'',
            #Machines
            'company-1'     :'',
            'out_fn-1'      :'',
            'ip-1'          :'',
            'machine-1'     :'',
            'sleep_time-1'  :'',
            'out_path-1'    :'',
            'path_move-1'   :'',
            'move_set-1'    :'',
            'end_time-1'    :'',
        }

        self.callqry  = _SQLMarcador()
        self._appbase = _AppBase()

        # Allowable commands for this application
        self.cmdStep = {
                        # 'G': self.get_attendance  ,
                        # 'C': self.clear_attendance,
                        # 'L': self.live_attendance ,
                        # 'R': self.reboot_machine  ,
                        'X': self.example0
                        }

    # Use only for configuration values that need some manipulations/checks.
    def set_config_vars(self):

        self.db_dsn  = self.config_vars['db_dsn']
        self.db_host = self.config_vars['db_host']
        self.db_port = su.to_int_zero(self.config_vars['db_port'])
        self.db_user = self.config_vars['db_user']
        self.db_pswd = self.config_vars['db_pswd']
        self.db_name = self.config_vars['db_name']

        self.mail_sender  = self.config_vars['mail_sender']
        self.mail_passwd  = self.config_vars['mail_passwd']
        self.mail_targets = self.config_vars['mail_targets'].split(',')

        if len(self.runSeq2) == 0: return 0

        self.company    = self.config_vars[f'company-{self.runSeq2}'   ]
        self.out_fn     = self.config_vars[f'out_fn-{self.runSeq2}'    ]
        self.ip         = self.config_vars[f'ip-{self.runSeq2}'        ]
        self.machine    = self.config_vars[f'machine-{self.runSeq2}'   ]
        self.sleep_time = self.config_vars[f'sleep_time-{self.runSeq2}']
        self.out_path   = self.config_vars[f'out_path-{self.runSeq2}'  ]
        self.path_move  = self.config_vars[f'path_move-{self.runSeq2}' ]
        self.move_set   = self.config_vars[f'move_set-{self.runSeq2}'  ]
        self.end_time   = self.config_vars[f'end_time-{self.runSeq2}'  ]

        self.conn_db_str = {
            "host"   : self.db_host,
            "user"   : self.db_user,
            "passwd" : self.db_pswd,
            "db"     : self.db_name,
            "port"   : self.db_port,
            "charset": "utf8mb4"
        }

        return 0
    def example0():

        xx = self._appbase._set_dir_project()
        print(xx)

    def get_data_test(self):#complete

        ret = 1

        cn = ZKUtil(self.log, self.ip)
        cn.conn_machine()
        ret = cn._zk_data_test()
        cn._zk_disconnect()

        print(ret)

    def get_attendance(self):#complete
        ret = 0

        zu = ZKUtil(self.log, self.ip)
        zu._zk_connect()

        res = zu._zk_get_attendance()

        zu._zk_disconnect()

        print(res)

        return ret

    def clear_attendance(self):#complete
        ret = 0

        print(f"clear_attendance,detail => {self.runSeq2}")
        return ret

    def live_attendance(self):
        ret = 0

        zu = ZKUtil(self.log, self.ip)
        zu._zk_connect()
        zu._zk_reboot_machine()
        zu._zk_disconnect()
        return ret

    def reboot_machine(self):
        ret = 0

        zu = ZKUtil(self.log, self.ip)
        zu._zk_connect()
        zu._zk_reboot_machine()
        zu._zk_disconnect()
        return ret

def main(Args):

    a = Marcador()
    rc = a.main(Args)
    return rc

if __name__ == '__main__':

    rc = main(sys.argv)
    sys.exit(rc)
