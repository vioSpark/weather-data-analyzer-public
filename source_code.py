# coding: utf-8
"""
data model: Convert all excel sheets into csv files with only the important 'columns'
Important notes on this: date has to be in number format at exporting time!!!
date must be the first column!!!

make the pécz and front number columns for the events   -- done

find min and max dates of events    -- done

make the following dataframes:              (estimated ram usage ~40MB)
date on the event happened || additional features 3 || weather numbers 2
weather numbers (2 columns) || additional features || value 4

Where:
1: (in that combination of features)    0
2: Péczely/Front numbers to +-n days
3: unique combination of  gender, event type, ...
4: conditional probabilities...

This is where we left things off:
So i have to research, how to make histograms from dataframes, and evaluate, if the creation of pivot tables
    are necessary


check if the given distribution is coming from noise, or it's something deeper (chi^2 probe)
for that we have to make a table:
date || event happened or not || weather numbers 2 || additional features 3
export: histograms, p values, raw data in csv or excel

there is a master class, with functions, for each tasks -- this should be modified, if needed
for top level interface you can call class UI
one level deeper is the class DataManipulator
one level deeper are functions and class(es) helping the DataManipulator to do it's job
"""

import datetime as dt
import postprocessor as pp

import UI

# todo: vector calculations -> approx 300 times faster
# todo: HDFStore for save/load system


# freshest UI code:
ui = UI.UI(
    input_directory=r'D:\Documents\tmp SSD\Project B\Publication Brigi\python\2020_05_07_request\test',
    input_file='Klima_AMI_dummy_for_testing.xlsx',
    input_sheet_name='Összes',
    depth=-1,
    msg="testing" + ' ' + str(dt.datetime.now())
)
# cProfile.run("ui.do_your_job()", 'profile_data_' + dt.datetime.now().strftime("%Y-%m-%d_%H-%M"))
ui.do_your_job()
ui.post_process()
