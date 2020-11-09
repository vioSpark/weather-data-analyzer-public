# coding: utf-8
import datetime as dt
import logging
import os
import sys

import datamanipulator
import pieces as pc
import postprocessor as pp
from deprecated import deprecated


class UI:

    # usage:  todo: examples too
    # input_directory: replace '\' with '/'
    # input_file: include the file-extension
    # input_sheet_name: the sheet's name or it's position (if you pass an integer)
    # output_directory, output_file, output_sheet_name same as above
    #       (except the position thing) include the file-extension
    # logfile_name: name of the chi2 test results file (txt), include the file-extension
    # exit_on_warning: terminate process, if there's a repairable error? (this is not fully supported yet)
    # msg: custom message in the beginning of the logfile
    #       (for example user defined metadata, like what was the purpose of the test
    # logfile: True | False : True redirect std to the logfile, False does otherwise
    # chi_filename: where to save chi^2 results
    # depth: Integer, will limit how many categories can be specific in the chi^2 test.
    #       -1 will allow all categories to be specific
    def __init__(self, input_directory, input_file, output_directory=None,
                 output_file=None,
                 input_sheet_name=0, output_sheet_name=None, exit_on_warning=True, logfile=True,
                 logfile_name=None, chi_filename=None, msg='', depth=-1):
        self.msg = str(msg)
        self.input_directory = str(input_directory)
        self.input_file = str(input_file)
        self.input_sheet_name = input_sheet_name
        self.exit_on_warning = exit_on_warning
        if depth > -1:  # the +1 is needed so the recursion won't shit itself
            # (I have no clear idea what's going on, but it gone through some unit testing)
            self.depth = depth + 1
        else:
            self.depth = -1

        if output_directory:  # old: ==0
            self.output_directory = str(output_directory)
        else:
            self.output_directory = str(input_directory)
        if output_file:  # old: ==0
            self.output_file = str(output_file)
        else:
            self.output_file = str(input_file)[:30] + '...ran_in_python.xlsx'
        if output_sheet_name:
            self.output_sheet_name = output_sheet_name
        else:
            self.output_sheet_name = 'pivot generator table'
        if chi_filename:
            self.chi_filename = chi_filename
        else:
            self.chi_filename = str(input_file)[:30] + '...chi_squared_results.txt'
        if logfile:
            if logfile_name:
                self.logfile_name = str(logfile_name)
            else:
                self.logfile_name = 'logs/results_' + dt.datetime.now().strftime("%Y-%m-%d_%H-%M") + '.txt'
        else:
            self.logfile_name = sys.__stdout__
        try:
            os.makedirs(self.output_directory + '/logs')
            print('logs directory not found, so it was created for log files')
        except FileExistsError:
            # directory already exists
            pass
        logging.basicConfig(filename=self.output_directory + '/' + self.logfile_name,
                            filemode='w',
                            format='%(asctime)s.%(msecs)-3d\t%(name)-20s\t%(levelname)-8s\t%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        self.log = logging.getLogger(__name__)
        self.log_metadata()

        # progress = ProgressBar()

    def __del__(self):
        print("program finished")

    def do_your_job(self):
        self.log.info('task started: ' + str(dt.datetime.now()))
        self.check_errors()
        self.sequence()

    def sequence(self):
        dm = datamanipulator.DataManipulator(self.input_directory + '/' + self.input_file,
                                             sheet_name=self.input_sheet_name)
        dims = dm.read_dimensions_from_excel()
        dm.assign_numbers()
        dm.create_generator_table_old()
        dm.write_pivot_generator_to_excel(self.output_directory + '/' + self.output_file, self.output_sheet_name)
        # automatically check if significant
        self.log.info("chi^2 table generation started")
        caa = []
        pc.condition_array_builder(caa, dims, max_depth=self.depth)
        dm.automatic_condition_check(caa, self.output_directory + '/' + self.chi_filename, save_tables=False)
        self.log.info('task finished: ' + str(dt.datetime.now()))
        self.log.critical('program finished successfully')

    def post_process(self, output_path=None, input_path=None):
        if output_path:
            output_path = str(output_path)
        else:
            output_path = self.output_directory + '/' + self.input_file[:30] + '...significants.txt'
        if input_path:
            input_path = str(input_path)
        else:
            input_path = self.output_directory + '/' + self.chi_filename

        pp.get_significant(input_path, 0.05, output_path)

    def check_errors(self):
        if not (self.output_file.endswith('.xlsx')):
            if self.exit_on_warning:
                self.log.critical(pc.get_error_msg('error', 'extension_error') + self.output_file)
                exit(-1)
            else:
                self.output_file += '.xlsx'
                self.log.error(pc.get_error_msg('warning', 'file_renamed') + self.output_file)
        if self.input_sheet_name == 0:  # old: ==0
            self.log.warning(pc.get_error_msg('warning', 'no_sheet_name'))
        try:
            writer = datamanipulator.pd.ExcelWriter(self.output_directory + '/' + self.output_file)
            datamanipulator.pd.DataFrame(data='Testing of write permission is completed, access granted',
                                         index=range(2),
                                         columns=range(2)).to_excel(writer, index=False, sheet_name='testing IO error')
            writer.save()
            writer.close()
        except PermissionError as pe:
            self.log.critical(pe)
            self.log.critical(pc.get_error_msg('error', 'permission_error'))
            exit(-2)
        if not self.logfile_name.endswith('.txt'):
            self.log.warning(pc.get_error_msg('warning', 'bad_logfile_extension'))
        if not self.chi_filename.endswith('.txt'):
            self.log.warning(pc.get_error_msg('warning', 'bad_chi_file_extension'))
        self.log.debug('First round error checks are completed (UI.check_errors)')

    @deprecated(version='3.0', reason='logging is made through library now')
    def redirect_std(self):
        # TODO: if error happens, only redirect, if explicitly asked
        try:
            os.makedirs(self.output_directory + '/logs')
            print('logs directory not found, so it was created for log files')
        except FileExistsError:
            # directory already exists
            pass
        destination = self.output_directory + '/' + self.logfile_name
        try:
            log = open(destination, 'w')
            print('stdout is now flowing to: \t' + destination)
        except OSError:
            # todo: clean this up
            print('Can not open logfile to write, FATAL ERROR')
            exit()
            log = sys.__stdout__
        sys.stdout = log
        return log

    @deprecated(version='3.0', reason='logging is made through library now. Use UI.log_metadata() instead')
    def print_metadata(self):
        print('DEBUG DATA:{')
        print('message: ' + str(self.msg))
        print('input directory: ' + str(self.input_directory))
        print('input file: ' + str(self.input_file))
        print('input sheet name: ' + str(self.input_sheet_name))
        print('output directory: ' + str(self.output_directory))
        print('output file: ' + str(self.output_file))
        print('output sheet name: ' + str(self.output_sheet_name))
        print('chi^2 results file name: ' + str(self.chi_filename))
        print('logfile original name: ' + str(self.logfile_name))
        print('exit on warning: ' + str(self.exit_on_warning))
        print('}')

    def log_metadata(self):
        self.log.info('DEBUG DATA:{' +
                      '\nmessage: ' + str(self.msg) +
                      '\ninput directory: ' + str(self.input_directory) +
                      '\ninput file: ' + str(self.input_file) +
                      '\ninput sheet name: ' + str(self.input_sheet_name) +
                      '\noutput directory: ' + str(self.output_directory) +
                      '\noutput file: ' + str(self.output_file) +
                      '\noutput sheet name: ' + str(self.output_sheet_name) +
                      '\nchi^2 results file name: ' + str(self.chi_filename) +
                      '\nlogfile original name: ' + str(self.logfile_name) +
                      '\nexit on warning: ' + str(self.exit_on_warning) +
                      '\n}')


@deprecated(version='3.0', reason='not implemented')
class ProgressBar:
    """
    lvl_0: no calculation -- this is implemented through logger
    lvl_1: basic information, like delta time
    lvl_2: complex information, like estimated complete time
    lvl_3: outside, calculations based on more accurate information, which may be a result of another class
    """

    def __init__(self):
        self.start_time = dt.datetime.now()

    def print_lvl_0_info(self):
        return ('--------------------\n' +
                'Start time: ' + str(self.start_time) + '\n' +
                'Current time: ' + str(dt.datetime.now()))

    def print_lvl_1_info(self):
        return "Time elapsed since start: " + str((dt.datetime.now() - self.start_time).total_seconds()) + " s"
