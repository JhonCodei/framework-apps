"""
@author: jalcarraz
This module implements email functionality.

Modification History
date-author-description


pip install pymysql
pip install sshtunnel

"""
__version__ = '20190823'

# ===============================================================================
# SQLLITE Driver
# ===============================================================================
import sqlite3

class DBSQLLite(object):

    def __init__(self, cs, logger, encode=str):
        self.conn_str = cs
        self.db_conn  = None
        self.log      = logger
        self.encode   = encode
        self.sep      = ','

    # Returns 0 if successful
    def conn_to_db(self):
        ret = 1
        try:
            # self.dbConn = sqlite3.connect(self.connStr,isolation_level=None)
            self.db_conn = sqlite3.connect(self.conn_str)
            self.db_conn.text_factory = self.encode
            self.log.debug(f'Connecting to {self.conn_str}')
            ret = 0

        except:
            self.log.error(f'Except Connect String {self.conn_str}')
            self.log.error(f'Except {sys.exc_info()}')

        finally:
            return ret

    # Use this query for select options
    # s     : list of BINDING VARIABLES, that need to be passed to the SQL Engine
    #    def runQry(self,qryStr,s=[]):
    #
    #        if(type(s) != list) :
    #            s = [s,]
    #
    #        resLst =[]
    #        if (self.dbConn == None):
    #            self.logger.error("self.dbConn has not been set")
    #            return resLst
    #
    #        try:
    #            cursor = self.dbConn.cursor()
    #            res = cursor.execute(qryStr,s)
    #            for row in res:
    #                   resLst.append(row)
    #        except sqlite3.OperationalError, msg:
    #        #except:
    #            print("==>> EO OPEr EXCEP IN RUNQRY %s " % msg)
    #            raise sqlite3.OperationalError, msg
    #
    #
    #        finally:return resLst
    #

    # Use this query for select options
    # s     : list of BINDING VARIABLES, that need to be passed to the SQL Engine
    def run_qry(self, qry_str, s=[]):

        if (type(s) != list):
            s = [s, ]

        res_lst = None
        if self.db_conn is None:
            self.log.error(f'self.dbConn has not been set')
            return res_lst

        try:
            tmp    = []
            cursor = self.db_conn.cursor()
            res    = cursor.execute(qry_str, s)
            for row in res:
                tmp.append(row)

        except sqlite3.OperationalError:
            self.log.error(f'Except {sys.exc_info()}')

        else:
            res_lst = tmp
        finally:
            return res_lst

    #   DEBUG ONLY
    #    def runQry(self,qryStr,s=[]):
    #
    #        if(type(s) != list) :
    #            s = [s,]
    #
    #        resLst =[]
    #        if (self.dbConn == None):
    #            self.logger.error("self.dbConn has not been set")
    #            return resLst
    #        cursor = self.dbConn.cursor()
    #        res = cursor.execute(qryStr,s)
    #        for row in res:
    #            resLst.append(row)
    #
    #        return resLst

    # Use this method for DML insert, update, delete
    # qryStr: SQL command to execute
    # s     : list of BINDING VARIABLES, that need to be passed to the SQL Engine

    def exe_qry(self, qry_str, s=[]):
        rc = -1

        if (type(s) != list or type(s) != tuple):
            s = list(s)

        if (self.db_conn == None):
            self.log.error(f'self.dbConn has not been set')
            return 1

        try:
            cursor = self.db_conn.cursor()
            # cursor.execute(qry_str, s)
            cursor.executemany(qry_str, s)
            rc = cursor.rowcount
            self.db_conn.commit()
            self.log.info(f'rc is {rc}')
            return rc

        # IntegrityError columns are not unique
        # ProgrammingError: Incorrect number of bindings supplied
        except sqlite3.OperationalError:
            # self.dbConn.rollback()
            # raise sqlite3.OperationalError
            self.log.error(f'Except OperationalError  {sys.exc_info()}')

        except sqlite3.IntegrityError:
            # self.dbConn.rollback()              # EO might help in DB lock issue.
            # raise sqlite3.IntegrityError, msg
            self.log.error(f'Except IntegrityError {sys.exc_info()}')

        except:
            self.log.error(f'Except OperationalError  {sys.exc_info()}')
        finally:
            self.db_conn.rollback()  # WIll get in here only
            return rc

    #   DEBUG ONLY
    # def exe_qry(self,qryStr,s = []) :
    #            print( "\n\n==============Qry = %s " % qryStr)
    #            rc = -1
    #            cursor = self.db_conn.cursor()
    #            # cursor.execute(qryStr,s)
    #            cursor.executemany(qryStr, s)
    #            rc = cursor.rowcount
    #            self.db_conn.commit()
    #            print("exeQry: rc is %s " % rc)
    #            return rc

    def close_db_conn(self):
        if (self.db_conn != None):
            self.db_conn.commit()
            self.log.debug(f'Closing Conn {self.conn_str}')
            self.db_conn.close()

# ===============================================================================
# MYSQL Driver OVER SSH - sshtunnel
# ===============================================================================
import pymysql as mysql
import sshtunnel
import sys

sshtunnel.SSH_TIMEOUT    = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

class DBMYSQLOVERSSH(object):

    def __init__(self, sshcs, dbcs, logger, encode=str):
        self.ssh_str  = sshcs
        self.conn_str = dbcs
        self.db_conn  = None
        self.log      = logger
        self.encode   = encode
        self.sep      = ','
        self.type     = None
        self.query    = None
        self.vars     = None

    def runQry(self, evt):

        rt = 0

        self.type  = evt['type' ]
        self.query = evt['query']
        self.vars  = evt['vars' ]

        try:
            with sshtunnel.SSHTunnelForwarder((self.ssh_str['ssh_host'],self.ssh_str['ssh_port']),ssh_password=self.ssh_str['ssh_pwsd'],ssh_username=self.ssh_str['ssh_user'],remote_bind_address=(self.ssh_str['ssh_rmip'], self.ssh_str['ssh_rmpt'])) as self.tunnel:

                self.start_ssh()
                self.log.info(f"Iniciando SSH, puerto {self.tunnel.local_bind_port}")

                self.conn_str.update([ ('port', self.tunnel.local_bind_port) ])

                try:
                    #self.db_conn = mysql.connect(**self.conn_str)
                    self.db_conn = mysql.connect(user=self.conn_str['user'],
                                         passwd=self.conn_str['passwd'],
                                         db=self.conn_str['db'],
                                         host=self.conn_str['host'],
                                         port=self.conn_str['port'],
                                         charset=self.conn_str['charset'])
                    self.log.info(f"db-> {self.db_conn}")
                    try:
                        self.log.info(f"iniciando => rq_sql")
                        rt = self.rq_sql()
                    except Exception as e:
                        self.log.error(f"Exception runQry => {e}")
                        self.log.error(f'Except {sys.exc_info()}')
                    finally:
                        return rt
                except Exception as e:
                    self.log.error(f"Error connexion db => {e}")
                    self.log.error(f'Except {sys.exc_info()}')
                finally:
                    self.close_db_conn()

        except Exception as e:
            self.log.error(f"Error connexion ssh=> {e}")
            self.log.error(f'Except {sys.exc_info()}')
        finally:
            self.stop_ssh()


    def rq_sql(self):

        rt = 0

        if len(self.type) == 0:
            self.log.error(f"fc: rq_sql - {self.type} -> Vacio!!")
            self.log.error(f'Except {sys.exc_info()}')

        self.log.info(f"fc: rq_sql -> Ejecutando {self.type}")

        if self.type == 'act-ls':

            if len(self.vars) == 0 :#need vars LS
                self.log.error(f"fc: rq_sql -> error variables {self.vars} vacias!!!")
                self.log.error(f'Except {sys.exc_info()}')

            try:
                cursor = self.db_conn.cursor()
                self.log.info(f"fc: rq_sql -> set cursor")
                cursor.executemany(self.query, self.vars)
                rc = cursor.rowcount
                self.db_conn.commit()
                rt = rc
            except mysql.ProgrammingError as error:
                self.log.error(f"{self.type}, failed, detail => {error}")
                self.log.error(f'Except {sys.exc_info()}')

        elif self.type == 'act-uni':

            try:
                cursor = self.db_conn.cursor()

                if len(self.vars) == 0:
                    cursor.execute(self.query)
                    self.log.info(f"fc: rq_sql -> Ejecutando query  sin  vars")
                else:
                    cursor.execute(self.query, (self.vars,))
                    self.log.info(f"fc: rq_sql -> Ejecutando query con  vars")

                rc = cursor.rowcount
                self.db_conn.commit()
                rt = rc
            except mysql.ProgrammingError as error:
                self.log.error(f"{self.type}, failed, detail => {error}")
                self.log.error(f'Except {sys.exc_info()}')

        elif self.type == 'gt-dt':

            # if (type(self.vars) != list):
            #     self.vars = [self.vars,]
            try:
                tmp    = []
                cursor = self.db_conn.cursor()#mysql.cursors.DictCursor)

                if len(self.vars) == 0 :
                    cursor.execute(self.query)
                    self.log.info(f"fc: rq_sql -> Ejecutando query  sin  vars")
                else:
                    if(type(self.vars) != list):
                        self.vars = [self.vars,]
                        self.log.info(f"fc: rq_sql -> Ejecutando query  con  vars")
                        cursor.execute(self.query, self.vars)

                res = cursor.fetchall()
                for row in res:
                    tmp.append(row)

                rt = tmp
            except mysql.ProgrammingError as error:
                self.log.error(f"{self.type}, failed, detail => {error}")
                self.log.error(f'Except {sys.exc_info()}')

        elif self.type == 'del-uni':

            try:
                cursor = self.db_conn.cursor()

                if len(self.vars) == 0:
                    self.log.info(f"fc: rq_sql:{self.type} -> Ejecutando query  sin  vars")
                    cursor.execute(self.query)
                    self.log.info(f"cursor: \n {cursor}")
                else:
                    self.log.info(f"fc: rq_sql:{self.type} -> Ejecutando query con  vars:\n {self.vars}")
                    cursor.execute(self.query, (self.vars,))
                    self.log.info(f"cursor: \n {cursor}")
                rc = cursor.rowcount
                self.db_conn.commit()
                rt = rc
            except mysql.ProgrammingError as e:
                self.log.error(f"{self.type}, delete failed, detail => {e}")
                self.log.error(f'Except {sys.exc_info()}')

        return rt

    def close_db_conn(self):
        if (self.db_conn != None):
            self.db_conn.commit()
            self.log.debug(f'Closing Conn {self.conn_str}')
            self.db_conn.close()

    def start_ssh(self):
        self.tunnel.start()
        self.log.info(" event ssh, iniciado.")
    def stop_ssh(self):
        self.tunnel.stop()
        self.log.info(" event ssh, detenido.")

# ===============================================================================
# MYSQL Driver
# ===============================================================================
#only connect to MYSQL
class DBMYSQL(object):

    def __init__(self, dbcs, logger, encode=str):
        self.conn_str = dbcs
        self.db_conn  = None
        self.log      = logger
        self.encode   = encode
        self.sep      = ','

    # Returns 0 if successful
    def conn_to_db(self):
        rt = 1

        try:
            self.log.info(f"conn_str : {self.conn_str}")
            #self.db_conn = mysql.connect(**self.conn_str)
            self.db_conn = mysql.connect(
                user=self.conn_str['user'],
                passwd=self.conn_str['passwd'],
                db=self.conn_str['db'],
                host=self.conn_str['host'],
                port=self.conn_str['port'],
                charset=self.conn_str['charset']
            )

            self.log.debug(f'Connecting to {self.conn_str}')
            rt = 0
        except Exception as e:
            self.log.error(f'Except Connect String {e}')
            self.log.error(f'Except {sys.exc_info()}')

        finally:
            self.log.debug(f"CONN DB -> {self.db_conn}")
            return rt

        #self.stop_ssh()


    # Use this query for select options
    # s     : list of BINDING VARIABLES, that need to be passed to the SQL Engine
    def run_qry(self, qry_str, s=[]):

        self.query = qry_str
        self.vars  = s

        res_lst = None
        if self.db_conn is None:
            self.log.error(f'self.dbConn has not been set')
            return res_lst

        try:
            tmp = []
            cursor = self.db_conn.cursor()#mysql.cursors.DictCursor)

            if len(self.vars) == 0 :
                cursor.execute(self.query)
                self.log.info(f"fc: rq_sql -> Ejecutando query  sin  vars")
            else:
                if(type(self.vars) != list):
                    self.vars = [self.vars,]
                    self.log.info(f"fc: rq_sql -> Ejecutando query  con  vars")
                    cursor.execute(self.query, self.vars)

            res = cursor.fetchall()
            for row in res:
                tmp.append(row)

        except mysql.ProgrammingError as error:
            self.log.error(f"{self.type}, failed, detail => {error}")
            self.log.error(f'Except {sys.exc_info()}')
        else:
            res_lst = tmp
        finally:
            return res_lst

    # Use this method for DML insert, update, delete
    # qryStr: SQL command to execute
    # s     : list of BINDING VARIABLES, that need to be passed to the SQL Engine
    def exe_qry(self, qry_str, s=[]):

        self.query = qry_str
        self.vars  = s

        rc = -1

        if (type(self.vars) != list or type(self.vars) != tuple):
            self.vars = list(self.vars)

        if (self.db_conn == None):
            self.log.error(f'self.dbConn has not been set')
            return 1

        try:
            cursor = self.db_conn.cursor()
            cursor.executemany(self.query, self.vars)

            rc = cursor.rowcount
            self.db_conn.commit()

            self.log.info(f'rc is {rc}')
            return rc

        # IntegrityError columns are not unique
        # ProgrammingError: Incorrect number of bindings supplied
        except mysql.ProgrammingError as e:
            self.log.error(f'Except ProgrammingError  {sys.exc_info()}')
        except:
            self.log.error(f'Except OperationalError  {sys.exc_info()}')
        finally:
            self.db_conn.rollback()  # WIll get in here only
            return rc


    def close_db_conn(self):
        if (self.db_conn != None):
            self.db_conn.commit()
            self.log.debug(f'Closing Conn {self.conn_str}')
            self.db_conn.close()
