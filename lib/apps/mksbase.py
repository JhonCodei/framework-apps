"""
 mksbase is the base class for all MKS applications.
 This program :
    1)
    2)

"""

__version__ = '20181113'

import sys
import os

from common.app_log  import get_logger
from common.app_conf import load_app_config
from common.app_env  import get_env_vars

#import common.app_base as app_base

RET_WARN = 101

class _MksBaseApp(object):
    # exitOnError = False
    def __init__(self):
        self.appName = self.__class__.__name__.lower()
        # Path section.
        # Pycharm
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Shell
        #self.base_dir   = app_base.set_path_project()
        self.data_dir   = os.path.join(self.base_dir, 'data'       )
        self.config_dir = os.path.join(self.base_dir, 'config'     )
        self.script_dir = os.path.join(self.base_dir, 'script'     )
        self.log_dir    = os.path.join(self.base_dir, 'log'        )
        self.lib_dir    = os.path.join(self.base_dir, 'lib'        )
        self.stmnt_dir  = os.path.join(self.lib_dir , 'statements' )
        self.output_dir = os.path.join(self.data_dir, 'output'     )
        self.input_dir  = os.path.join(self.data_dir, 'input'      )

        self.stmnt_fn = os.path.join(self.stmnt_dir, f'{self.appName}.py')

        self.cfg_file = os.path.join(self.config_dir, f'{self.appName}.cfg') # Can be overwritten by ENV Vars.
        self.log_name = f'{self.appName}.log'                                # Can be overwritten by ENV Vars.
        self.log = get_logger(self.log_dir, self.log_name)                   # Can be overwritten by ENV Vars.
        self.env_vars    = {}
        self.config_vars = {}
        self.config      = {}
        self.cmdStep     = {}
        self.runSeq      = None
        self.runSeq2     = None # set default

    # Abstract define in child class.
    # Use to set configuration variables, that might need spme verification.
    # e.g. int, float, emails, etc
    def set_statement_file(self):
        if os.path.exists(self.stmnt_fn):
            self.log.info(f" statements file exist, name:{self.stmnt_fn}")
        else:
            self.log.error(f" statements file no exist, name:{self.stmnt_fn}")


    def set_config_vars(self):
        return 0

    # Abstract define in child class.
    def set_global_exe(self):
        return 0


    def print_config_vars(self):
        for k,v in self.config_vars.items():
            self.log.debug(f'self.config_vars = {k} --  {v}')

    # Set Incoming arguments
    def _set_args(self, argv):

        if len(argv) == 2:
            self.log.critical(f" running <{argv[1]}> fx [runSeq] - Number of arguments ({len(argv)})")
        elif len(argv) == 3:
            self.log.critical(f" running <{argv[1]}>, {argv[2]}> fx [runSeq] - Number of arguments ({len(argv)})")
            self.runSeq2 = argv[2]

        self.runSeq  = argv[1]

        return 0

    # # Execute Steps
    def _execSteps(self, run_step):

        self.log.info(f'runStep = {run_step}')
        for s in run_step:
            if not s in self.cmdStep:
                self.log.error(f'Invalid step {s}')
                return 1

            rv = 1
            try:
                rv = self.cmdStep[s]()
                if rv != 0 and self.exitOnError:
                    self.log.error(f'{s}:{self.cmdStep[s].__name__}()\trc\t={rv}')
                    return rv

                self.log.info(f'{s}:{self.cmdStep[s].__name__}()\trc\t= {rv}')

            except AttributeError:
                self.log.error(f'{s}:{self.cmdStep[s].__name__}')
                self.log.error(f'Except {sys.exc_info()}')
                if (self.exitOnError): return rv

            except SyntaxError:
                self.log.error(f'{s}:{self.cmdStep[s].__name__}()\trc\t={rv}')
                self.log.error(f'Except {sys.exc_info()}')
                if (self.exitOnError): return rv

        return rv

    # # Execute Steps Troubleshoooting

    # argv is a list of runnable commands, defined per class basis
    def main(self, argv):
        rc = 1  # Failed

        # should NEVER get this programmatic error !!!!
        if self.cmdStep is None or len(self.cmdStep) == 0:
            self.log.critical(f'Program Error:self.cmdStep is {self.cmdStep}')
            return 1

        rc = self._set_args(argv)
        if rc != 0:
            return rc

        rc = get_env_vars(self.env_vars, self.log)
        if rc != 0:
            self.log.error('Need to set all env vars}')
            return rc

        self.config_vars = load_app_config(self.cfg_file, self.config, self.log)
        if self.config_vars is None:
            self.log.error("Error Loading Config File:\n")
            return rc

        self.print_config_vars()

        rc = self.set_config_vars()
        if rc != 0:
            self.log.error("Error Setting Config Vars\n")
            return rc

        rc = self.set_statement_file()##

        if self.runSeq is not None and len(self.runSeq) > 0:
            rc = self._execSteps(self.runSeq)
            if rc == 0:
                self.log.info(f'Completed running exec_steps rc = {rc}')
            else:
                self.log.error(f'execSteps rc = {rc}')

        sys.exit(rc)

    def __del___(self):
        self.log.debug('Base class cleaning')

if __name__ == '__main__':

    from apps.set_env import setEnvVars

    os.environ['LOG_CONS']  =  'TRUE'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    a = _MksBaseApp()
    rc = a.main(('a','b'))
