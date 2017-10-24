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

__Option 1__ - Send patient to next care segment after exceeding curfew.

__Option 2__ - Put patient in a "limbo state" for time they spend in that segment that exceeds curfew, where their speed (rate of progress through care segments) while in this state is reduced to 0.


After finishing your specifications, click "Read Data", and a new window will appear to allow you to define
care segments and add filters to these segments.

The two option menus are used to set the start and end of the care segment, and "Add Segment" adds this to a list
above these buttons with a default name. Clicking on a segment will show an editing menu at the bottom of the window
where you can rename the segment and add filters to the segment.

Filters are added to a segment by choosing a visit characteristic to filter by, an operator, and a value which 
you type in manually. When a filter is added to that segment, patients with visit characteristics not adhering
to the filters will not be included in the time slices in that segment.


Finally, you can click "Generate Report", and a folder called "flows" will be created with one .csv file for each
segment you defined. Each .csv folder has rows with the start of the time slice, and associated traffic flow calculations.
If writing patients was enabled, it will also include rows of patients in each time slice.

## FlowsPlots.py
Run this program in the same way you ran flowsGUI.py. You will be greeted with a similar option to choose files,
but the input for this program is one of the .csv files outputted by flowsGUI.py. Clicking "Read Data" will convert
the input .csv file into the datastructures necessary to plot the data. Please note that this only works on the .csv files
that __do not__ have patients written with each time slice. This program analyzes the data by time of day, so also
make sure that the delta_t of the time slices divide 24 hours evenly.

At this point, you will see a frame with the currently displayed plot, as well as buttons to change which plot is displayed.
For all the "vs. Time of Day" plots, this is pretty straightforward. Just choose it from the menu and click "Display Plot".
For the "vs. Density" plots, you can also use the arrow buttons next to the plot frame to view this data hour by hour.

The "Export Plot" button exports an image of the currently displayed plot.

"Export Means" exports a .csv file that makes up the raw data for the plot points, and "Export Errors" exports the raw data
for the error bars.




