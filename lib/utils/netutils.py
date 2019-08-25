"""

@author: eocampo
This module manages Network operations.  All OS specfic should br handled here.

Modification History
date-author-description

"""
__version__ = '20181113'

import sys
import socket
import re
import proc.process    as p
import utils.strutils  as su
import utils.mathutils as mu

# -------------- Platform Specific Cmd :Start
if (sys.platform == 'win32'):
    PING_CMD = "ping %s -n %d"
    PING_RESP = "(0% loss)"
    PING_IDX_OFF = -1
else:
    PING_CMD = "ping %s -c %d"
    PING_RESP = " 0% packet loss"
    PING_IDX_OFF = 2
# -------------- Platform Specific Cmd :End

def is_valid_ip(addr):

    try:
        socket.inet_aton(addr)
        return True
    except socket.error: return False

# x = name@host.com
# Returns a list with the user and domain.
def domain_split(x):
  try:
    s = x.split("@")
    if len(s) == 2:
        return s
    return None

  except:
    return None


# addr Server Name or IP
# no   Number of times to execute the command.

def ping_server(addr, logger, txn = 5):
    rv = 1
    cmd = PING_CMD % (addr, txn)
    logger.debug(f'cmd = {cmd}')
    rc, msg = p.run_sync(cmd, logger)

    if rc == 0:
        rv = su.find_str(msg.decode('utf-8'), PING_RESP)
    return rv


# Helper function to get percent. msg format:
# UX  4 packets transmitted, 0 received, 100% packet loss, time 3065ms
# UX  4 packets transmitted, 4 received, 0% packet loss, time 3061ms
# WIN Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
# WIN Packets: Sent = 4, Received = 4, Lost = 0 (100% loss)
# msg response from ping
# per percent success
# txn transmitted packets

def _get_ping_per(msg, logger, txn, per_pass):
    logger.debug(f'msg = {msg} txn = {txn} per_pass = {per_pass}')
    resp = msg.split()
    recv = 0
    m = re.compile('recibidos|received', re.IGNORECASE)
    for r in resp:
        mat = re.match(m, r)
        if mat:
            idx = resp.index(r)
            rx = resp[idx + PING_IDX_OFF]
            logger.debug(f'idx = {idx} rx = {rx}')
            recv = su.to_int_zero(rx)
            break

    # If messages were received, let check if they pass the number required, based on %
    if recv > 0:
        recv_per = mu.get_perc_100(txn, recv)
        logger.debug(f' recv = {recv} recv_perc = {recv_per}')
        if recv_per < per_pass:
            logger.error(f'txn = {txn} recv = {recv} recv_per = {recv_per} per_pass = {per_pass}')
            return 1

    return 0


# addr Server Name or IP
# txn  Number of transmission(s)
# perc percent success rate.

def ping_server_per(addr, logger, txn=5, per_pass=100):
    rv = 1
    cmd = PING_CMD % (addr, txn)
    logger.debug("cmd = {cmd}")
    rc, msg = p.run_sync(cmd,logger)

    if rc == 0:
        rv = _get_ping_per(msg.decode('utf-8'), logger,  txn, per_pass)

    return rv
