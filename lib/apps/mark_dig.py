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

import proc.process as p
import utils.fileutils as fu
import utils.netutils as nu
import utils.strutils as su

from datastore.dbutil import DBSQLLite

from apps.mksbase import _MksBaseApp

current_date = datetime.now().strftime('%Y%m%d')

MARK_SEL_QRY = """SELECT dni, fecha, hora, maquina
                  FROM marcador
                  WHERE fecha
                  BETWEEN datetime('now', '-15 days') AND datetime('now', 'localtime')
                  GROUP BY dni,fecha,hora
                  ORDER BY fecha ASC, dni ASC"""

MARK_INS_QRY = "INSERT INTO marcador(dni, fecha, hora, maquina, registro) VALUES(?, ?, ?, ?, ?)"

class MarkDig(_MksBaseApp):


    def __init__(self):

        super(MarkDig, self).__init__()
        self.exitOnError = False
        self.ips = ''
        self.machines = ''
        self.port = 0
        self.max_tries = 0
        self.txn_times = 0
        self.sleep_time = 0
        self.db_name = ''
        self.inp_mark_data = ''


        # Environmental variables:
        self.env_vars = {
        }

        # Configuration variables:
        self.config = {'IPs': '',
                       'Port': 0,
                       'Machines': '',
                       'Max_Tries': 0,
                       'Txn_Times': 4,
                       'Sleep_Time': 0,
                       'Reboot_Exe': '',
                       'Get_Data_Exe': '',
                       'Perc_Ping_Pass': 100,
                       'Db_Name': '',          # Tied to SQLITE. EO need to create an abstract connector.
                       'Inp_Mark_Data': '',    # Data from Digital Marker
                       'Out_Mark_Data': '',    # Data to write to SQLite
                       'Out_Base_File_Path': '',
        }

        # Allowable commands for this application
        self.cmdStep = {
                        'A': self.get_data,
                        'B': self.reboot_mark,
                        'C': self.ping_mark,
                        'D': self.ping_reboot,
                        'E': self.build_prn,
                        'F': self.ins_mark_sql,
                        'X': self.xd
                        }
    def xd(self):
        print(1)
    # Use only for configuration values that need some manipulations/checks.
    def set_config_vars(self):

        self.ips = self.config_vars['IPs'].split(",")
        self.machines = self.config_vars['Machines'].split(",")
        # self.port = if su.to_int(config['Port']) != None else 0

        self.port = su.to_int_zero(self.config_vars['Port'])
        self.max_tries = su.to_int_zero(self.config_vars['Max_Tries'])
        self.txn_times = su.to_int_zero(self.config_vars['Txn_Times'])
        self.sleep_time = su.to_int_zero(self.config_vars['Sleep_Time'])
        pp = su.to_int_zero(self.config_vars['Perc_Ping_Pass'])
        self.per_ping_pass = 100 if pp < 1 else pp

        if len(self.ips) < 1:
            self.log.error(f'Config: IPs len {len(self.ips)} and Machines len {len(self.machines)} need 1 or more elements')
            return 1

        if len(self.ips) != len(self.machines):
            self.log.error(f'Config: IPs and Machines do not have same element number!')
            return 2

        # Specific to SQLITE
        self.db_name = os.path.join(self.data_dir,self.config_vars['Db_Name'])
        ret = fu.file_exists(self.db_name)
        if ret is False:
            self.log.error('DB {self.db_name} does not exist')
            return 3

        self.log.debug(f'self.db_name = {self.db_name}')

        return 0

    # SE Sets name of external programs
    def set_global_exe(self):
        global get_data_exe, reboot_exe
        get_data_exe = os.path.join(self.script_dir, self.config_vars['Get_Data_Exe'])
        reboot_exe = os.path.join(self.script_dir, self.config_vars['Reboot_Exe'])

    # Create config file for consumer.
    def _write_config_file(self, ip, mach):
        fnp = os.path.join(self.script_dir, self.config_vars['Rem_Config_File'])
        data = f"IP = {ip}\nport = {self.config_vars['Port']}\nmachine = {mach}\n"
        ret = fu.create_file(fnp, data, self.log)
        if ret == 0:
            self.log.info(f'Wrote file {fnp}')

        return ret

    # Runs external program
    # prog (_get_data) = os.path.join(SCRIPT_DIR, CONFIG_VAR['Get_Data_Exe'])
    # prog (_reboot_mark) = os.path.join(SCRIPT_DIR, CONFIG_VAR['Reboot_Exe'])
    def _run_prog(self,ip, machine, prog):

        if not fu.file_exists(prog):
            self.log.error(f'program {prog} does not exist')
            return 2

        ret = self._write_config_file(ip, machine)

        if ret == 0:
            ret, rmsg = p.run_sync(prog, self.log)  # Invoke program Reboot

        if ret != 0:
            self.log.error(f'{prog} ret = {ret} rmsg={rmsg}')

        return ret

    def _get_data_text(self):

        ld = []
        tnow = su.get_today_str("%Y-%m-%d %H:%M:%S")
        inpfile = os.path.join(self.input_dir, self.config_vars['Inp_Mark_Data'])
        self.log.debug(f'inpfile {inpfile}')
        recs = fu.read_file_list(inpfile, self.log)
        if len(recs) < 1:
            self.log.error(f'Could not open {inpfile} or has 0 records')
            return ld

        self.log.info(f'file = {inpfile}  {len(recs)} recs ')
        for r in recs:
            sr = r.split(',')
            sr.append(tnow)
            ld.append(sr)
        return ld

    # Step methods defined here
    def get_data(self):

        i = 0
        ret = 0

        for ip in self.ips:
            r = self._run_prog(ip, self.machines[i], get_data_exe)
            if r == 0:
                self.log.info(f'ret = {r} for ip = {ip} machine = {self.machines[i]}')
            else:
                self.log.error(f'ret = {r} for ip = {ip} machine = {self.machines[i]}')
            ret += r
            i += 1

        return ret

    def reboot_mark(self):

        i = 0
        ret = 0

        for ip in self.ips:
            r = self._run_prog(ip, self.machines[i], reboot_exe)
            if r == 0:
                self.log.info(f'ret = {r} for ip = {ip} machine = {self.machines[i]}')
            else:
                self.log.error(f'ret = {r} for ip = {ip} machine = {self.machines[i]}')
            ret += r
            i += 1
        return ret

    def ping_mark(self):  #> 0
        ret = 0
        for ip in self.ips:
            r = nu.ping_server_per(ip, self.log, self.txn_times, self.per_ping_pass)
            if r == 0:
                self.log.info(f'ret = {r} for ip = {ip}')
            else:
                self.log.error(f'ret = {r} for ip = {ip}')
            ret += r
        return ret #FAIL > 0  # success = 0 always


    # This method  pings the host.
    # If ping fails it will go ahead and reboot and get the data
    def ping_reboot(self):
        ret = 0
        i = 0

        for ip in self.ips:
            # ret = nu.ping_server(ip, self.log, CONFIG_VAR['Max_Tries']) # for 100 %
            r = nu.ping_server_per(ip, self.log, self.txn_times, self.per_ping_pass)
            if r == 0:
                self.log.info(f'ping {ip} for machine {self.machines[i]} succeeded')
            else:  # If ping fails lets reboot r != 0.
                self.log.error(f'ping {ip} for machine {self.machines[i]} failed. Will reboot !')
                r = self._run_prog(ip, self.machines[i], reboot_exe)
                if r != 0:
                    self.log.error(f'Reboot {ip} failed for machine {self.machines[i]} ret = {r}')
                    ret += r
                    i += 1
                    continue
                else:
                    self.log.info(f"Rebooted {ip} for machine {self.machines[i]}."
                                  "Will sleep for {self.sleep_time} secs")

                time.sleep(self.sleep_time)

                r = nu.ping_server_per(ip, self.log, self.txn_times, self.per_ping_pass)
                if r != 0:
                    self.log.error(f"ping {ip} for machine {self.machines[i]} failed after reboot")
                    ret += r
                    i += 1
                    continue

                # If ping successful, lets get_data()
                r = self._run_prog(ip, self.machines[i], get_data_exe)
                if r != 0:
                    self.log.error(f"IP {ip} failed after get_data : ret = {ret}")
                    ret += r
                    i += 1
                    continue
                else:
                    self.log.info(f'get_data IP {ip} for machine {self.machines[i]} : ret = {ret}')

            i += 1

        return ret

    def build_prn(self):

        data = []

        if self.config_vars['Out_Base_File_Path'] == '':
            outfile = os.path.join(self.output_dir, self.config_vars['Out_Mark_Data'])
        else:
            outfile = self.config_vars['Out_Base_File_Path']

        self.log.debug(f'outfile {outfile}')

        db = DBSQLLite(self.db_name, self.log)
        rc = db.conn_to_db()
        if rc != 0:
            return rc

        rows = db.run_qry(MARK_SEL_QRY)

        for r in rows:
            data.append(f'{r[0]},{r[1]},{r[2]},{r[3]}\n')

        db.close_db_conn()

        ret = fu.create_file(outfile, data, self.log)

        if ret == 0:
            self.log.info(f'Wrote File {outfile} with {len(rows)} rows')

        return ret

    def ins_mark_sql(self):

        db = DBSQLLite(self.db_name, self.log)
        rc = db.conn_to_db()
        if rc != 0:
            return rc

        ld = self._get_data_text()
        if len(ld) < 1:
            return 1

        res = db.exe_qry(MARK_INS_QRY, ld)
        db.close_db_conn()
        self.log.info(f'recs read from file = {len(ld)}  insert into DB = {res} ')
        return len(ld) - res


def main(Args):

    a = MarkDig()
    rc = a.main(Args)
    return rc

if __name__ == '__main__':

    rc = main(sys.argv)
    sys.exit(rc)
