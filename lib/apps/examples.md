self.evt = {
        'type' : self.typeSQL,
        'query': self.qry1,
        'vars' : []
    }


db = DBMYSQLOVERSSH(self.conn_ssh_str, self.conn_db_str, self.log)
db = DBMYSQL(self.conn_db_str, self.log)
