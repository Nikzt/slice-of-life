# Slice of Life 
Slice of Life is a tool to organize, analyze, and plot data by splitting it up into time slices.
This is the first iteration of this program, and was developed specifically to analyze the flow of
patients through different care segments in an emergency department by utilizing traffic flow
theory.

## What does it do?
Given a .csv file with at least two columns of time data, the program can sort these lines into
user defined time periods (slices). For each time slice, there is an associated measure of flux,
density, and mean length of stay which is all put into an output .csv file. It can then sort 
these output files by time of day, and provide summary statistics and plots to give the user
an idea of how the flow of patients changes throughout the day.

## Dependencies
Anaconda for python 3.6
Download here: https://www.anaconda.com/download/

# Usage
First, make sure that you have downloaded and installed Anaconda.

## FlowsGUI.py
This is the program that will take your input data and output the .csv files corresponding to
your specifications. But first, there are some requirements on the format of your data, which can
be fulfilled using Excel.

All columns containing times must be converted to numbers.

The file must be converted to .csv format.

After this is done, run flowsGUI.py with Python 3, which was included with the Anaconda installation.
The specifics of this will be dependent on which OS you are using, so here is a link explaining it 
if you are not familiar with python:
http://pythoncentral.io/execute-python-script-file-shell/

Once the program is running, a window will pop up. Click "Select File" to choose your formatted input
data file, and then "Read Column Names" to initialize the rest of the user interface.

Now, it is time to input the specifications for the time slices. The delta_t option will determine the 
length of the time slices, and the start/end inputs will determine what range of your data to read (these have
to be numbers, in the same format as they appear in your data). If a column contains missing time fields, the option
for that will determine whether to ignore rows where that time field is missing, or fill in missing times with the
previous time field. There is also an option to write all of the patient data with the timeslices when generating
the final output.

The "Define Columns" tab lets you choose columns from your input file, and two buttons to interpret that column
as containing times, or visit characteristics. A table will appear with everything you have added, and you can delete 
them if you make a mistake. Remember to add time columns in increasing order (eg. a patient's t0 entry should be less than
their t1 entry).

The "Define Curfews" tab lets you choose an upper limit (t_curfew) for how long a patient should be in a given care
segment, as well as how to handle patients that exceed this curfew:

Option 1 - Send patient to next care segment after exceeding curfew.

Option 2 - Put patient in a "limbo state" for time they spend in that segment that exceeds curfew, where their speed (rate of progress through care segments) while in this state is reduced to 0.


After finishing your specifications, click "Read Data", and a new window will appear to allow you to define
care segments and add filters to these segments.

