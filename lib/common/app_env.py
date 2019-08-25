"""
@author: eocampo

Modification History
date-author-description

"""
__version__ = '20181113'

import os
import sys

def get_env_vars(e_vars, logger):
    ret = 0
    err = []

    if len(e_vars) == 0:
        logger.info('No env vars to load')
        return 0

    for ev, v in e_vars.items():
        logger.debug(f'{v} = os.environ[{ev}]')

    for ev, v in e_vars.items():
        try:
            print(f'---------- ev = {ev} v = {v}')
            x = os.environ[ev]
            exec(f"v='x'")
            logger.debug(f"{v}='{x}'")

        except:
            ret = 2
            err.append(ev)
            logger.debug(f'Except {sys.exc_info()}')

    if len(err) > 0:
        logger.error(f'Need to define envars {err}')

    return ret
