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

from apps.mksbase      import _MksBaseApp
from statements.ventas import _SQLVentas


current_date = datetime.now().strftime('%Y%m%d')

class Ventas(_MksBaseApp):

    def __init__(self):

        super(Ventas, self).__init__()
        self.exitOnError = False

        # config vars CFG file
        self.ssh_host = None
        self.ssh_user = None
        self.ssh_pwsd = None
        self.ssh_port = None
        self.ssh_rmip = None
        self.ssh_rmpt = None
        self.db_host  = None
        self.db_user  = None
        self.db_pswd  = None
        self.db_name  = None
        self.db_port  = None
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
            'ssh_host': '',
            'ssh_user': '',
            'ssh_pwsd': '',
            'ssh_port': '',
            'ssh_rmip': '',
            'ssh_rmpt': '',
            'db_host' : '',
            'db_user' : '',
            'db_pswd' : '',
            'db_name' : '',
            'db_port' : '',
        }

        self.callqry = _SQLVentas()
        # Allowable commands for this application
        self.cmdStep = {
                        'X': self.example2,
                        }
    # Use only for configuration values that need some manipulations/checks.
    def set_config_vars(self):

        self.ssh_host = self.config_vars['ssh_host']
        self.ssh_user = self.config_vars['ssh_user']
        self.ssh_pwsd = self.config_vars['ssh_pwsd']
        self.ssh_port = su.to_int_zero(self.config_vars['ssh_port'])
        self.ssh_rmip = self.config_vars['ssh_rmip']
        self.ssh_rmpt = su.to_int_zero(self.config_vars['ssh_rmpt'])
        self.db_host  = self.config_vars['db_host' ]
        self.db_user  = self.config_vars['db_user' ]
        self.db_pswd  = self.config_vars['db_pswd' ]
        self.db_name  = self.config_vars['db_name' ]
        self.db_port  = su.to_int_zero(self.config_vars['db_port'])

        self.conn_ssh_str = {
            "ssh_host": self.ssh_host,
            "ssh_user": self.ssh_user,
            "ssh_pwsd": self.ssh_pwsd,
            "ssh_port": self.ssh_port,
            "ssh_rmip": self.ssh_rmip,
            "ssh_rmpt": self.ssh_rmpt
        }
        self.conn_db_str = {
            "host"   : self.db_host,
            "user"   : self.db_user,
            "passwd" : self.db_pswd,
            "db"     : self.db_name,
            "port"   : self.db_port,
            "charset": "utf8mb4"
        }

        self.set_querys()

        return 0

    def set_querys(self):

        self.qry1 = self.callqry._QryTest

    def example(self):
        print(self.qry1)

        data = []

        #db = DBMYSQLOVERSSH(self.conn_ssh_str, self.conn_db_str, self.log)
        db = DBMYSQL(self.conn_db_str, self.log)

        # self.evt = {
        #     'type' : self.typeSQL,
        #     'query': self.qry1,
        #     'vars' : []
        # }



        rc = db.conn_to_db()
        if rc != 0:
            return rc

        rows = db.run_qry(self.qry1, self.vars)

        # print(f"row => {rows}")
        db.close_db_conn()
        for r in rows:
            data.append(f'{r[0]},{r[1]},{r[2]},{r[3]}\n')

        fnn = r'D:\Projects\python\debug\data\output\xx.csv'
        ret = fu.create_file(fnn, data, self.log)

        if ret == 0:
            self.log.info(f'Wrote File {fnn} with {len(rows)} rows')

        return ret

    def BVC_TEST(self):
        rt  = []
        fn  = r'D:\Projects\python\debug\data\input\BVC.xls'
        fnn = r'D:\Projects\python\debug\data\output\xx2.csv'

        xls = fu.read_excel_file(fn, self.log)

        for x in xls:

            if len(x[1]) != 0:
                fecha = x[0]
                if len(x[1]) == 1:
                    fecha = su.float_to_full_date(self.log, x[0])

                rt.append(f"{fecha},{x[1]},{x[2]},{x[3]},{x[4]},{x[5]},{x[6]},{x[7]}\n")

        ret = fu.create_file(fnn, rt, self.log)

        return ret

def main(Args):

    a = Ventas()
    rc = a.main(Args)
    return rc

if __name__ == '__main__':

    rc = main(sys.argv)
    sys.exit(rc)
