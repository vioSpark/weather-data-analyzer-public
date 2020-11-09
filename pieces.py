# coding: utf-8
# import pandas as pd
import copy
import datetime as dt

import numpy as np

""" 
# not used
class ExtendedDataFrame:
    def __init__(self, df, name='unnamed'):
        self.name = name
        self.df = df
  
    def __str__(self):
        return "DataFrame's name: " + self.name + "\n" + str(self.df)
"""


# stolen from stackoverflow:
def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)


def get_error_msg(severity, name):
    # Optional To Do: import the error msg-s from a (xml?) file, so translating the program is easier
    """header = {
        'error': ("+----------+\n" +
                  "|   Error  |\n" +
                  "+----------+\n"),
        'warning': ("+----------+\n" +
                    "|  Warning |\n" +
                    "+----------+\n")
    }"""
    lookup_directory = {
        'name': 'Error string',
        'extension_error': 'Output file name is invalid! Are you sure it ends with a valid extension (xlsx)?'
                           '\nfilename: ',
        'file_renamed': 'Output file has been renamed to: ',
        'no_sheet_name': 'Input sheet name is not specified. Default setting applied, first sheet will be used',
        'permission_error': "\nYou almost got rekt\n\n"
                            "You were lucky enough to be caught by a quick test, so you won't realize "
                            "2 days later, that you forget to close the excel file",
        'xlrd not imported': "Have you added xlrd to the project's reachable libraries?",
        'dimension_mismatch': "Some dimension mismatch occurred \nbased on file: {} \nbased on array: {}",
        'condition_dimension_mismatch': "Some dimension mismatch occurred \nbased on previous computations: {} "
                                        "\nbased on condition array: {}",
        'too_big': "Save file format doesn't supports that big databases",
        'format': "Check the format of the excel cells! It should be in date format",
        'not_sorted': "Database is not sorted, this will cause further errors at chi^2 test",
        'near_limit': "Database's size is near Excel's row limit",
        'unknown_index_error': "Index error happened"
                               "\nI suggest, that you go after it, but it's not a critical error"
                               "\nThe code is still running!",
        'under_limit': "Not all {} elements are above 5, chi^2 test might be compromised",
        'bad_logfile_extension': 'The extension of the logfile is not txt',
        'bad_chi_file_extension': 'The extension of the chi^2 save file is not txt'
    }
    extra_line = ''
    if severity == 'error':
        extra_line = 'Fatal error encountered, execution stopped'
        print('Fatal error encountered, execution stopped')
        # sys.stdout = sys.__stdout__
    # old: return header[severity] + lookup_directory[name] + extra_line
    return lookup_directory[name] + extra_line


def condition_array_builder(caa, dims, max_depth=-1):
    pm_day = 2
    fixed = []  # just a 'global' variable declaration for the recursion
    for day in range(-pm_day, pm_day + 1):
        condition_builder_recursion(caa, dims, fixed, day, max_depth=max_depth)
    return


def condition_builder_recursion(caa, dims, fixed, day, j=0, max_depth=-1):
    if max_depth == 0:
        print('max_depth=0')
        return
    dim = dims[j]  # WTF is j? is it some sort of badly implemented max_depth?... I should comment more...
    j += 1
    for i in range(-1, dim):
        fixed.append(i)
        if len(dims) != j:
            if i != -1:
                condition_builder_recursion(caa, dims, fixed, day, j, max_depth=max_depth - 1)
            if i == -1:
                condition_builder_recursion(caa, dims, fixed, day, j, max_depth=max_depth)
        else:
            if i == -1 or max_depth > 1:
                # this is needed, so  the last element of the array will only generate, if -1 or has depth remaining
                tmp = [day]
                tmp.extend(copy.deepcopy(fixed))
                caa.append(tmp)
        fixed.pop()
    return


def cluster_madness_generator(size_of_dimensions, length):
    r_clus = 1
    try:
        arr = np.empty(length, dtype=int)
        for dim in size_of_dimensions[::-1]:
            # process:      dim->range->reshape->broadcast->flatten(concat)->broadcast->flatten(concat)
            tmp = np.concatenate(np.broadcast_to(np.reshape(np.arange(dim), (dim, 1)), (dim, r_clus)))
            r_clus *= dim
            row = np.concatenate(np.broadcast_to(tmp, (int(length / r_clus), r_clus)))
            arr = np.vstack((row, arr))
        return arr[:-1]
    except TypeError:
        print("check the excel, it's more than probable you will find some missing data!!!!")
        exit(-100)
        # todo: make a logger for this, and print out which positions it might occur
