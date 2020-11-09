# coding: utf-8
import pieces as pc
import pandas as pd
import scipy.stats as scs
import csv
import numpy as np
import logging
from numba import jit
from deprecated import deprecated

"""
lessons learned:

something like an infinite loop in the very beginning -> Excel's data formats are fucking up the computations
failed contingency table build  (really low values)

contingency table's sum is nowhere near to the number of records in database
-> not ascending order database
-> more generally there's a fuck-up in the dates column

pycharm's dataframe viewer not works
-> it dislikes the following characters: <, >       (there might be more)
-> it dislikes duplicate index names

"""


# TODO: have a nicer handling for the contingency tables
# TODO: make the multi-threaded progress printing
# TODO: after that, multi-thread the pivot table generator function

def debug():
    print('reference rounding limit for [2,13] dimension tables')
    df = pd.DataFrame(data=8.5685, index=range(2), columns=range(13))
    excepted = pd.DataFrame(data=1, index=range(2), columns=range(13))
    print(scs.chisquare(df, excepted, axis=None, ddof=13))
    print('end of debug:\n\n\n')


# TODO: optimise automated chi^2
# TODO: save - load system
class DataManipulator:
    def __init__(self, filename, excel=True, sheet_name=0):
        self.log = logging.getLogger(__name__)
        self.log.debug("DataManipulator created")

        self.df = pd.DataFrame()
        self.excel = excel
        if excel:
            try:
                xlsx_file = pd.ExcelFile(filename)
                self.df = xlsx_file.parse(sheet_name, header=0)
                xlsx_file.close()
            except ImportError:
                self.log.critical(pc.get_error_msg('error', 'xlrd not imported'))

            self.column_names = self.df.columns.values.tolist()[1:]
        else:
            self.ifile = open(filename, "r", encoding='utf_8')
            self.ofile = open("peczely_hozzarendelt.tmp", "w", encoding='utf_8')
            self.column_names = []
        self.maxdate = pd.Timestamp.min  # =    1677-09-21
        self.mindate = pd.Timestamp.max  # =    2262-04-11
        self.pivot_generator = pd.DataFrame()
        self.number_of_clusters = 0
        self.size_of_dimensions = []
        self.dims_can_be_checked = False
        self.dates = pd.DataFrame()
        self.p_values = []

    """@deprecated
    def __del__(self):
        self.log.debug("DataManipulator destroyed")
        if not self.excel:
            self.ifile.close()
            print("input file closed")
            self.ofile.close()
            print("output file closed")
    """

    def read_dimensions_from_excel(self):
        for i in range(1, self.df.columns.size):
            self.size_of_dimensions.append(self.df.iloc[:, i].max() + 1)
        # return for the UI
        return self.size_of_dimensions

    # "interface" for copying the dimension's possible values
    def modify_dimensions(self, dims):
        if self.dims_can_be_checked:
            if self.check_dims():
                self.size_of_dimensions = dims
            else:
                exit()
        else:
            self.dims_can_be_checked = True
            self.size_of_dimensions = dims

    # check if the dimension of the passed excel, is the same, as hardcoded into the beginning
    def check_dims(self):
        a = len(self.size_of_dimensions)
        if a != self.number_of_clusters:
            try:
                self.log.debug(self.df.columns.values)
            except UnicodeEncodeError:
                self.log.debug('failed to print self.df.columns.values')
            self.log.critical(pc.get_error_msg('error', 'dimension_mismatch').format(self.number_of_clusters,
                                                                                     len(self.size_of_dimensions)))
            return False
        else:
            return True

    # because excel isn't the best thing
    def check_number_of_rows(self, rows):
        excel_max_rows = 1048576
        if rows > excel_max_rows:
            self.log.critical(pc.get_error_msg('error', 'too_big'))
            exit()
        if rows > 0.8 * excel_max_rows:
            self.log.warning(pc.get_error_msg('warning', 'near_limit'))
        return

    # deprecated
    def assign_numbers_print_to_csv(self):
        # watch out for not HUN locale written csv files, this will cause a problem
        csv_reader = csv.reader(self.ifile, delimiter=';', lineterminator="\r\n")
        # csvwriter = csv.writer(self.ofile, delimiter=';', lineterminator="\n")
        print("DataManipulator has been connected to input and output file")

        # iterating through
        row_number = 0
        pFAssign = PFAssign()
        # todo: refactor this ... it's ugly af
        for row in csv_reader:
            if row_number == 0:
                pass  # header = row
            else:
                column_number = 0
                temp = []
                for col in row:
                    if column_number == 0:
                        date = col
                    else:
                        temp += col
                    column_number += 1
                date_as_number = round(float(date.replace(",", ".")))
                row[0] = date_as_number
                self.data_as_array.append(row + pFAssign.return_date(date_as_number))

                # min max
                if date_as_number > self.maxdate:
                    self.maxdate = date_as_number
                if date_as_number < self.mindate:
                    self.mindate = date_as_number

            row_number += 1

        print("temporary csv file written")
        print('min: ' + str(self.mindate))
        print('max: ' + str(self.maxdate))

    # using data frames
    def assign_numbers(self):
        self.log.debug("assigning meteorological numbers to dates started")
        self.number_of_clusters = self.df.shape[1] - 1
        # error check
        if self.dims_can_be_checked:
            if not self.check_dims():
                exit()
        else:
            self.dims_can_be_checked = True

        row_number = 0
        pFAssign = PFAssign()
        meteo_df = pd.DataFrame(columns=['P-2', 'P-1', 'P0', 'P1', 'P2', 'F-2', 'F-1', 'F0', 'F1', 'F2'])
        for index, row in self.df.iterrows():
            # print(row[0], row[1], row[2])
            date = row[0]  # it's a Timestamp format
            try:
                meteo_df.loc[row_number] = pFAssign.return_date(round(to_excel_date(date)))
            except TypeError:
                self.log.critical(pc.get_error_msg('error', 'format'))
                exit()

            # min max
            if date > self.maxdate:
                self.maxdate = date
            if date < self.mindate:
                self.mindate = date
            row_number += 1

        self.check_ascending()
        self.df = self.df.join(meteo_df)
        self.log.info("assigning meteorological numbers to dates ended")
        self.log.debug('min date: ' + str(self.mindate))
        self.log.debug('max date: ' + str(self.maxdate))

    # partial check if the excel is sorted (otherwise building of contingency tables are fooled)
    def check_ascending(self):
        if self.mindate != self.df.iloc[0, 0] or self.maxdate != self.df.iloc[-1, 0]:
            self.log.critical(pc.get_error_msg('error', 'not_sorted'))
            exit()

    # notice, that the naming conventions are stricter than usual: the name's first character must correspond to the
    # name in self.df, where only the first character can be ....
    # e.g. the name of column of the Péczely day 0 values in self.df is 'P0'
    # name[:1] grabs the name"s first letter. 'i' means the current day.
    # In Péczely's case, the name is Peczely.
    # So name[:1] + str(i) translates into P0, which is the exact name of the required column in self.df
    # ctrl+f for c1 = (self.df[name[:1] + str(i)] == generated_table.iloc[sor, 3]) to understand more details
    def create_generator_table(self, name, number, pm_day, day_type_counter):
        # define stuff:
        name_ascii = name.encode(encoding='ascii', errors='replace')
        self.log.info('started creating ' + name + " generator table")
        # header for the table
        header = ['Érték', 'Meteo típus', 'nap', 'Meteorológiai szám']
        header.extend(self.column_names)
        self.log.info('columns: ' + str(header))
        # For first, calculate helper variables:
        number_of_days = 2 * pm_day + 1
        clus = 1
        for i in range(self.number_of_clusters):
            clus = clus * self.size_of_dimensions[i]
        n_number = number * number_of_days * clus
        day_length = n_number / number_of_days

        # error check for excel limit has been omitted
        # build separate parts of the dataframe

        # cluster madness, which is always hard
        clus_matrix = pc.cluster_madness_generator(self.size_of_dimensions, n_number)
        self.log.debug('cluster madness has been generated')

        # an array which indicates the name of the meteorological number
        name_array = np.concatenate(np.broadcast_to([name_ascii], (n_number, 1)))
        self.log.debug('name_array has been generated')

        # days are going from -pm_day to +pm_day
        day_array = np.broadcast_to(np.reshape(np.arange(-pm_day, pm_day + 1), (number_of_days, 1)),
                                    (number_of_days, int(day_length))).flatten()
        self.log.debug('day_array has been generated')

        # numbers are going from 1 to 1+number, in each day (note: 1+number is 13 for Péczely)
        number_array = np.broadcast_to(np.reshape(
            np.broadcast_to(np.reshape(np.arange(1, 1 + number), (number, 1)),
                            (number, int(day_length / number))).flatten(), (1, int(day_length))),
            (number_of_days, int(day_length))).flatten()
        self.log.debug('(meteorological)number_array has been generated')

        # concat all the generated tables
        generated_table = pd.concat(
            [pd.DataFrame([np.zeros(n_number), name_array, day_array, number_array], index=header[:4]),
             pd.DataFrame(clus_matrix, index=header[4:])]).T
        self.log.debug('Generator table has been completed without the values')

        # Values (number=13 for Peczely)
        dates_found = [None] * number
        # this is where it fucks up:
        for i in range(number):
            dates_found[i] = day_type_counter(to_excel_date(self.mindate), to_excel_date(self.maxdate), i + 1)

        for i in range(-pm_day, pm_day + 1):
            # given day

            # df[(df.a > 1) & (df.a < 3)].count()
            # countifs= df[df["class"]==1].count(), where df equals a dataframe

            for j in range(number):
                # this on belows checks the i^th day member-wise, if they equal to 1
                # self.df["P" + str(i)] == 1
                for g in range(clus):
                    # iterate through every row of generated_table
                    sor = (i + pm_day) * number * clus + clus * j + g
                    # checking for meteorological number equality
                    c1 = (self.df[name[:1] + str(i)] == generated_table.iloc[sor, 3])
                    # initialize condition array
                    ca = [None] * self.number_of_clusters
                    # checking the conditions
                    for h in range(self.number_of_clusters):
                        # this one is good, it counts how many records found with the given row's cluster variation
                        # self.df.iloc[:, 1 + h] == generated_table.iloc[sor, 4 + h]
                        ca[h] = (self.df.iloc[:, 1 + h] == generated_table.iloc[sor, 4 + h])
                    for h in range(self.number_of_clusters):
                        # checking if every condition is true
                        c1 &= ca[h]
                        generated_table.iloc[sor, 0] = np.count_nonzero(c1) / dates_found[j]
        self.log.debug('Values are calculated')
        self.log.info('generator table for {0} is complete'.format(name))
        self.log.debug('First few rows of the table:')
        self.log.debug(generated_table.head(3))
        return generated_table

    # the old function for creating the generator table, using the new method, but not lacking the tests
    def create_generator_table_old(self):
        # error check
        clus = 1
        for i in range(self.number_of_clusters):
            clus = clus * self.size_of_dimensions[i]
        rows = (13 + 9) * 5 * clus
        self.check_number_of_rows(rows)
        if rows > 1000000:
            self.log.warning(pc.get_error_msg('warning', 'near_limit'))

        # generate
        peczely_table = self.create_generator_table('Peczely', 13, 2, count_peczely)
        front_table = self.create_generator_table('Front', 9, 2, count_front)
        self.pivot_generator = pd.concat([peczely_table, front_table], copy=False)

    def write_pivot_generator_to_excel(self, path, sheet_name):
        # possible problem: file locked by excel -> if you call it through UI, it checks for it
        self.log.info("pivot generator table saving started")
        writer = pd.ExcelWriter(path)
        # this line (causes numpy.str problems):
        self.pivot_generator.to_excel(writer, index=False, sheet_name=sheet_name)
        writer.save()
        writer.close()
        self.log.warning("file saved under: " + path)

    def save_p_values(self, path, sheet_name, dataframes):
        # possible problem: file locked by excel -> if you call it through UI, it checks for it
        self.log.info("p values saving started")
        writer = pd.ExcelWriter(path)

        # p values
        df = pd.DataFrame(data='corrupted', index=range(2), columns=range(2))
        df.iloc[0, :] = self.p_values
        df.iloc[1, 0] = 'Péczely??'
        df.iloc[1, 1] = 'Front??'
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        i = 0

        # contingency tables
        for frame in dataframes:
            frame.to_excel(writer, startrow=10, startcol=i * 3, sheet_name=sheet_name)
            i += 3

        writer.save()
        writer.close()
        self.log.warning("file saved under: " + path)

    # TODO: Cleanup the code

    def automatic_condition_check(self, array_of_condition_arrays, path_to_save, save_tables=False):
        i = 0
        with open(path_to_save, 'w') as save_file:

            assigner = PFAssign()
            meteo_df = assigner.read_to_df()
            meteo_df.columns = meteo_df.iloc[0]
            # self.dates.index.name = None
            meteo_df = meteo_df.drop([0], axis=0)

            for ca in array_of_condition_arrays:
                day = ca[0]
                self.log.debug('condition: ' + str(ca) + ' is under checking')
                tables = self.create_conditional_contingency_table(ca=ca, meteo_numbers_as_df=meteo_df)
                # old: tables = self.create_conditional_contingency_table_old(ca)
                warning = self.do_chi2_test(tables[0], tables[1])
                save_file.write('id: ' + str(i + 1) + '\n' +
                                'day: ' + str(day) + '\n' +
                                'warning: ' + str(warning) + '\n' +
                                'condition: ' + str(ca) + '\n' +
                                'results:\n' +
                                '\tPéczely: \tp=' + str(self.p_values[0][1]) + '\n' +
                                '\tFront: \t\tp=' + str(self.p_values[1][1]) + '\n')
                if save_tables:
                    save_file.write('Tables:\n' +
                                    '\tPéczely:\n' + str(tables[0]) + '\n' +
                                    '\tFront:\n' + str(tables[1]) + '\n\n')
                i += 1
        self.log.info('automatic condition check ended')

    def create_conditional_contingency_table(self, ca, meteo_numbers_as_df):

        # for a query we have a condition array like this:
        # [0, -1, 0, 0, 0, 3, 1, 2, ... ]
        # where the first element means which day, and -1 means to omit that condition
        # (naturally the first element cannot be -1, so it means the -1th day)
        # the function returns with an array of dataframes, where [0] is the Péczely, [1] is the Front contingency table

        self.p_values = []
        day = ca[0]
        del (ca[0])

        tables = [pd.DataFrame(data=0, columns=["event occurred", "event not occurred"],
                               index=list(range(1, 14))),
                  pd.DataFrame(data=0, columns=["event occurred", "event not occurred"],
                               index=list(range(1, 10)))]
        start_date = int(meteo_numbers_as_df.iloc[0, 0])

        # self.df's last read element
        last_element = 0
        # for every day
        for date in range(int(to_excel_date(self.mindate)), int(to_excel_date(self.maxdate)) + 1):

            try:
                line = self.df.iloc[last_element, :].tolist()
                # deb=int(to_excel_date(line[0]))
                matched_line = int(to_excel_date(line[0])) == date
                date_found = matched_line
                # condition:
                for i in range(len(ca)):
                    if ca[i] != -1:
                        matched_line = matched_line and (line[i + 1] == ca[i])
            # This is necessary for the below to work """
            except IndexError:
                raise

            try:
                front = int(meteo_numbers_as_df.iloc[date - start_date + day, 2])
                if matched_line:
                    tables[1].iloc[front - 1, 0] += 1
                else:
                    tables[1].iloc[front - 1, 1] += 1
            except ValueError:
                pass
            pecz = int(meteo_numbers_as_df.iloc[date - start_date + day, 1])
            if matched_line:
                # corresponding table element +=1
                tables[0].iloc[pecz - 1, 0] += 1
            else:
                tables[0].iloc[pecz - 1, 1] += 1
            # getting the upper hand on the organized excel tables
            # if date found, than jump to the next line
            if date_found:
                # step 1 (or required) in self.df
                try:
                    last_element += 1
                    while self.df.iloc[last_element - 1, 0].date() == self.df.iloc[last_element, 0].date():
                        last_element += 1
                except IndexError:
                    # autoincrement only in the last case causes IndexError
                    pass
        # TODO: don't return the tables,
        # TODO: have an inner variable for handling it, or something... just now it's not OO approach
        return tables

    """@deprecated(version='3.0', reason='this code is pretty much junk')
    def create_conditional_contingency_table_old(self, ca):
        # for a query we have a condition array like this:
        # [0, -1, 0, 0, 0, 3, 1, 2, ... ]
        # where the first element means which day, and -1 means to omit that condition
        # (naturally the first element cannot be -1, so it means the -1th day)
        # the function returns with an array of dataframes, where [0] is the Péczely, [1] is the Front contingency table

        self.p_values = []
        day = ca[0]
        del (ca[0])
        a = len(ca)
        # error check
        if a != self.number_of_clusters:
            self.log.critical(
                pc.get_error_msg('error', 'condition_dimension_mismatch').format(self.number_of_clusters, str(a)))
            return

        # read péczely + front numbers to ram
        assigner = PFAssign()
        self.dates = assigner.read_to_df()
        self.dates.columns = self.dates.iloc[0]
        self.dates.index.name = None
        self.dates = self.dates.drop([0], axis=0)

        # tables[0]=peczely, [1]=front
        tables = [pd.DataFrame(data=0, columns=["event occurred", "event not occurred"],
                               index=list(range(1, 14))),
                  pd.DataFrame(data=0, columns=["event occurred", "event not occurred"],
                               index=list(range(1, 10)))]
        start_date = int(self.dates.iloc[0, 0])

        # self.df's last read element
        last_element = 0
        # for every day
        for date in range(int(to_excel_date(self.mindate)), int(to_excel_date(self.maxdate)) + 1):

            try:
                line = self.df.iloc[last_element, :].tolist()
                # deb=int(to_excel_date(line[0]))
                matched_line = int(to_excel_date(line[0])) == date
                date_found = matched_line
                # condition:
                for i in range(len(ca)):
                    if ca[i] != -1:
                        matched_line = matched_line and (line[i + 1] == ca[i])
            except IndexError:
                print(pc.get_error_msg('warning', 'unknown_index_error'))
                matched_line = False
                date_found = False
            try:
                front = int(self.dates.iloc[date - start_date + day, 2])
                if matched_line:
                    tables[1].iloc[front - 1, 0] += 1
                else:
                    tables[1].iloc[front - 1, 1] += 1
            except ValueError:
                pass
            pecz = int(self.dates.iloc[date - start_date + day, 1])
            if matched_line:
                # corresponding table element +=1
                tables[0].iloc[pecz - 1, 0] += 1
            else:
                tables[0].iloc[pecz - 1, 1] += 1
            # getting the upper hand on the organized excel tables
            # if date found, than jump to the next line
            if date_found:
                # step 1 (or required) in self.df
                try:
                    last_element += 1
                    while self.df.iloc[last_element - 1, 0].date() == self.df.iloc[last_element, 0].date():
                        last_element += 1
                except IndexError:
                    # autoincrement only in the last case causes IndexError
                    pass
        return tables
        """

    # TODO: normally display % of the runtime (some calculations will be necessary,
    # TODO:          like how many assembly steps is the given for loop's body)
    # TODO: estimate the full runtime, and measure longer runs with some trick
    # TODO: Refactor the code better
    # TODO: let the user select debug level (let them tamper the logfile's level)

    @jit
    def do_chi2_test(self, peczely_table, front_table):
        # calculates the chi^2 test results, and saves them in it's memory
        warning = ''
        self.p_values = []
        # test for at least 5 (or 3) is 70% percent of the cells
        # 13*2*0.3=7.8
        if ((peczely_table < 5).sum().sum()) > 7:
            self.log.warning(pc.get_error_msg('warning', 'under_limit').format('Péczely'))
            warning += 'P'
        # Péczely
        excepted = pd.DataFrame(data=0, index=range(len(peczely_table.index)),
                                columns=range(len(peczely_table.columns)))
        for i in range(13):
            excepted.iloc[i, :] = ((peczely_table.sum(axis=1).values[i]) / (self.maxdate - self.mindate).days)
            excepted.iloc[i, 0] = excepted.iloc[i, 0] * peczely_table.sum(axis=0).values[0]
            excepted.iloc[i, 1] = excepted.iloc[i, 1] * peczely_table.sum(axis=0).values[1]
        # print('Péczely p value:')
        # ddof=13, because scipy.stats.chisquare is a bit fucked up
        res = scs.chisquare(peczely_table, excepted, axis=None, ddof=13)
        # print(res)
        self.p_values.append(res)

        # Front
        # 9*2*0.3=5.4
        if (front_table < 5).sum().sum() > 5:
            self.log.warning(pc.get_error_msg('warning', 'under_limit').format('Front'))
            warning += 'F'
        excepted = pd.DataFrame(data=0, index=range(len(front_table.index)),
                                columns=range(len(front_table.columns)))
        for i in range(9):
            excepted.iloc[i, :] = ((front_table.sum(axis=1).values[i]) / (self.maxdate - self.mindate).days)
            excepted.iloc[i, 0] = excepted.iloc[i, 0] * front_table.sum(axis=0).values[0]
            excepted.iloc[i, 1] = excepted.iloc[i, 1] * front_table.sum(axis=0).values[1]
        # print('p value:')
        # ddof=9, because scipy.stats.chisquare is a bit fucked up
        res = scs.chisquare(front_table, excepted, axis=None, ddof=9)
        # print(res)
        self.p_values.append(res)


class PFAssign:
    def __init__(self):
        self.log = logging.getLogger(__name__ + 'PFA')
        self.inputFile = open("Peczely_es_Front_szamok.csv", "r", encoding='utf_8')
        self.filereader = csv.reader(self.inputFile, delimiter=';', lineterminator="\r\n")
        self.pmday = 2
        self.log.debug('\tPéczely table opened for reading')

    def __del__(self):
        self.inputFile.close()
        self.log.debug('\tPéczely table closed')

    def return_date(self, date):
        # can be optimized
        rnr = 0
        row_found = 0
        self.inputFile.seek(0)
        for row in self.filereader:
            if str(date) == row[0]:
                row_found = rnr
                break
            rnr += 1
        payloadp1 = []
        payloadp2 = []
        if row_found != 0:
            self.inputFile.seek(0)
            rnr = 0
            for row in self.filereader:
                if rnr + self.pmday >= row_found:
                    payloadp1.append(int(row[1]))
                    try:
                        payloadp2.append(int(row[2]))
                    except ValueError:
                        payloadp2.append(row[2])
                if rnr - self.pmday >= row_found:
                    break
                rnr += 1
        return payloadp1 + payloadp2

    def read_to_df(self):
        self.inputFile.seek(0)
        self.log.debug("Meteorological numbers have been copied to the memory")
        return pd.DataFrame([row for row in self.filereader])


def count_peczely(min_date, max_date, number):
    input_file = open("Peczely_es_Front_szamok.csv", "r", encoding='utf_8')
    filereader = csv.reader(input_file, delimiter=';', lineterminator="\r\n")
    input_file.seek(0)
    result = 0
    for row in filereader:
        # date conversion?
        try:
            if (int(row[0]) >= min_date) & (int(row[0]) <= max_date):
                if row[1] == str(number):
                    result += 1
        except ValueError:
            pass
    return result


def count_front(min_date, max_date, number):
    input_file = open("Peczely_es_Front_szamok.csv", "r", encoding='utf_8')
    filereader = csv.reader(input_file, delimiter=';', lineterminator="\r\n")
    input_file.seek(0)
    result = 0
    for row in filereader:
        try:
            if (int(row[0]) >= min_date) & (int(row[0]) <= max_date):
                if row[2] == str(number):
                    result += 1
        except ValueError:
            pass
    return result


# stolen from stackoverflow
def to_excel_date(date1):
    temp = pd.datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)
