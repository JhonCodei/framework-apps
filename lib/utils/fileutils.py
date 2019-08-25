"""

@author: eocampo
This module manages OS operations.  All OS specfic should br handled here.

Modification History
date-author-description

"""
__version__ = '20181113'

import sys
import os.path
import csv

import xlrd as xlsx# pip install xlrd

#########
## FILES
#########
def file_exists(fn): return os.path.exists(fn)

def get_file_size(fn): return os.path.getsize(fn)

def open_file(fn, logger, mode='r+'):

    f = None

    try:
        f = open(fn, mode)

    except IOError:
        logger.error(f'Error {sys.exc_info()}')

    finally:
        return f

def close_file(f):
    if f is not None:
        f.close()
#  Data can be a list or a string.
def create_file(fn, data, logger):

    ret = 1
    try:
        f = open(fn, "w")

        import types
        if isinstance(data, list):
            f.writelines(data)
        else:
            f.write(data)

        f.flush()
        f.close()
        ret = 0

    except FileNotFoundError:
        logger.error(f'No purede crear archivo {fn}')

    except IOError:
        logger.error(f'No se pudo crear {fn}')
        logger.debug(f'Except IOError {sys.exc_info()}')

    except:
        logger.error(f'Except {sys.exc_info()}')

    finally:
        return ret

def read_text_file(fn, logger):

    fcont = ''

    try:
        with open(fn, 'r') as f:
            fc = f.read()
            fcont = fc

    except FileNotFoundError:
        logger.error(f'No se encontro archivo {fn}')

    except:
        logger.error(f'Error {sys.exc_info()}')

    finally:
        return fcont

# Reads a csv file and returns a list.
def read_csv_file(fn, logger):

    rd_list = []

    try:
        with open(fn, 'r') as f:
            reader = csv.reader(f)
            rd_list = list(reader)

    except FileNotFoundError:
        logger.error(f'No se encontro archivo {fn}')

    except:
        logger.error(f'Error {sys.exc_info()}')

    finally:
        return rd_list

# returns a list.
def read_file_list(fn, logger):

    f = None
    ln = []
    try:
        f  = open(fn, 'r')
        ln = f.read().splitlines()
    except FileNotFoundError:
        logger.error(f'Except File {fn} not found')

    except:
        logger.error(f'Except {sys.exc_info()}')

    finally:
        if f: close_file(f)
        return ln


#########
## EXCEL FILES
#########

def read_excel_file_x_row_cols(fn, logger, index=0, current_row=-1):

    rd_list = []

    if file_exists(fn) == False:
        logger.error(f"excel file no exist!, {fn}")
        logger.error(f"excel error => {sys.exc_info()}")
        return rd_list

    rd_book = xlsx.open_workbook(fn)
    rd_indx = rd_book.sheet_by_index(index)

    # if len(rd_indx) == 0:
    #     logger.error(f"excel file empty!, {fn}")
    #     logger.error(f"excel error => {sys.exc_info()}")
    #     return rd_list

    frows  = rd_indx.nrows - 1
    fcells = rd_indx.ncols - 1
    #crtrow = current_row # fila actual

    while current_row < frows:
        current_row += 1

        row = rd_indx.row(current_row)
        current_cell = -1

        while current_cell < fcells:
            current_cell += 1

            cell_value = rd_indx.cell_value(current_row, current_cell)

            #if len(cell_value) != 0: #and isinstance(cell_value, str):
            rd_list.append(f"{cell_value}\n")

    return rd_list

def read_excel_file(fn, logger, index=0):

    rd_list = []

    if file_exists(fn) == False:
        logger.error(f"excel file no exist!, {fn}")
        logger.error(f"excel error => {sys.exc_info()}")
        return rd_list

    rd_book = xlsx.open_workbook(fn)
    rd_indx = rd_book.sheet_by_index(index)

    frows  = rd_indx.nrows
    fcells = rd_indx.ncols

    rowvalue = []

    for r in range(frows):
        for c in range(fcells):
            value = rd_indx.cell_value(r, c)
            rowvalue.append(f"{value}")

        rd_list.append(rowvalue)
        rowvalue = []

    return rd_list
