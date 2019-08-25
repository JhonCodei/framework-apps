# """
# @author: jalcarraz
#
# Modification History
# date-author-description
# Use for standalone application.
#
# """
# __version__ = '20190821'
#
# import sys, os
# import inspect
# import threading
# import platform
#
#
# def set_path_project():
#     main_id = None
#     for t in threading.enumerate():
#         if t.name == 'MainThread':
#             main_id = t.ident
#             break
#     if not main_id:
#         raise RuntimeError("Main thread exited before execution")
#
#     current_main_frame = sys._current_frames()[main_id]
#     base_frame = inspect.getouterframes(current_main_frame)[-1]
#
#     if platform.system() == 'Windows':
#         filename = base_frame.filename
#     else:
#         filename = base_frame[0].f_code.co_filename
#
#     ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(filename)))
#     return ROOT_DIR

# """
# @author: eocampo
#
# Modification History
# date-author-description
# Use for standalone application.
#
# """
# __version__ = '20181113'
#
# import os
# #Pycharm
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# # Shell
# #BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# DATA_DIR   = os.path.join(BASE_DIR, 'data'  )
# OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
# INPUT_DIR  = os.path.join(DATA_DIR, 'input' )
# LOG_DIR    = os.path.join(BASE_DIR, 'log'   )
# CONFIG_DIR = os.path.join(BASE_DIR, 'config')
# SCRIPT_DIR = os.path.join(BASE_DIR, 'script')


import os
import sys
import inspect
import threading
import platform

class _AppBase(object):

    def __init__(self):
        pass

    def _set_dir_project(self):
        main_id = None
        for t in threading.enumerate():
            if t.name == 'MainThread':
                main_id = t.ident
                break
        if not main_id:
            raise RuntimeError("Main thread exited before execution")

        current_main_frame = sys._current_frames()[main_id]
        base_frame = inspect.getouterframes(current_main_frame)[-1]

        if platform.system() == 'Windows':
            filename = base_frame.filename
        else:
            filename = base_frame[0].f_code.co_filename

        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(filename)))
        return ROOT_DIR
