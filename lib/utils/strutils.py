"""

@author: eocampo
This module manages OS operations.  All OS specfic should br handled here.

Modification History
date-author-description

"""

__version__ = '20181113'

import re
import sys,os
import datetime


def float_to_full_date(log, s):

    log.info(f" set vars => {s}")
    s = to_float(s)
    try:
        temp  = datetime.datetime(1900, 1, 1)
        delta = datetime.timedelta(days=s)

        log.info(f" set time => {temp + delta}")
        return temp + delta

    except ValueError as e:
        return None
    except TypeError  as e:
        return None

def _to_date(log, s, dl='/'):

    rt = None
    ls = []
    y  = None
    m  = None
    d  = None

    try:
        if " " in s:
            s = s.split(" ")
            if len(s) != 2:
                return rt
            if dl in s[0]:
                ls = s.split(dl)
        else:
            if dl in s:
                ls = s.split(dl)
        if len(ls) != 3:
            return rt

        if dl == '-':
            y = ls[0]
            m = ls[1]
            d = ls[2]
            rt = f"{d}/{m}/{y}"

        elif dl == '/':
            y = ls[2]
            m = ls[1]
            d = ls[0]
            rt = f"{y}-{m}-{d}"
    except Exception as e:
        log.error(f"error _to_date, detail => {e}")
        log.error(f"error _to_date, out => {sys.exc_info()}")
    finally:
        return rt

def to_str(s):
    try:
        s = str(s)
        return s

    except ValueError: return None
    except TypeError : return None

def to_int(s):
    if type(s) is str: s = s.rstrip()
    try:
        i = int(s)
        return i

    except ValueError: return None
    except TypeError : return None

def to_int_zero(s):
    if type(s) is str: s = s.rstrip()
    try:
        i = int(s)
        return i

    except ValueError: return 0
    except TypeError : return 0

def to_float(s):
    if type(s) is str: s=s.rstrip()
    try:
        i = float(s)
        return i

    except ValueError: return None
    except TypeError : return None

def to_float_zero(s):
    if type(s) is str: s=s.rstrip()
    try:
        i = float(s)
        return i

    except ValueError: return 0.0
    except TypeError: return 0.0

def is_valid_email(email):

    regx = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

    if len(email) > 7:
        if re.match(regx, email) is not None:
            return True
    return False


def is_empty(s):
    if s and s.strip():
        return False
    return True

# l complete list
# n chunk size

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


# msg string to check
# stf string to find
# 0 if string was found.
def find_str(msg, stf):

    rc = 1
    if msg is None or len(msg) < 2:
        return rc
    fstr = re.compile(r"%s" % stf, re.IGNORECASE)
    resp = re.findall(fstr, msg)
    if resp:
        rc = 0
    return rc


# returns a date string based on fmt mask.
def get_today_str(fmt='%m/%d/%Y'):
    d = datetime.datetime.now()
    return d.strftime(fmt)


def build_query(log, sql, target=[], vars=[]):

    log.info("Construyendo Query fc:build_query")

    if len(target) != len(vars):

        log.error(f"no son iguales")
        log.error(f'Except {sys.exc_info()}')
    else:

        for tg in target:
            if tg in sql:
                pass
        else:
            log.error(f"{tg} no existe en \n {sql}")
            log.error(f'Except {sys.exc_info()}')
    x = 0
    for i in range(len(target)):
        if x == 0:
            rt = sql.replace(str(target[i]), str(vars[i]))
        else:
            rt = rt.replace(str(target[i]), str(vars[i]))
        x += 1

    return rt


def sql_target_to_ls(log, vars):
    rt = []

    if len(vars) == 0:
        log.error(f"fc: sql_target_to_ls => vars => vacio!! ")
        log.error(f'Except {sys.exc_info()}')

    v = vars.split(",")

    for d in v:
        rt.append(f":{d}")

    log.info(f"fc: ret => {rt}")
    return rt
