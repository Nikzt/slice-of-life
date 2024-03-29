import os
import os.path
import copy
import DataStructures
from DataStructures import *


# -- Global Variables -- #
# list of TimeSlices
slices = []

# list of Patients
patients = []

# list of Segments
segments = []

# list of time columns
timecolumns = []

#list of curfews
curfews = []

# how to handle missing times
missingTime = "boi"

# track invalid data to put in error report
decreasingTimeCount = 0
# ---------------------- #



def process_line(csv_line):
  # returns a list representation of a line from a .csv file
  return csv_line.split(',')
    
"""
Returns a directory name of the format 'flows(i)' where i is the i'th directory
with the name flows.
"""
def get_dir_name(dirname="flows", count=0):
  if not os.path.isdir(dirname):
    return dirname
  else:
    return get_dir_name("flows" + "(" + str(count+1) + ")", count+1)

"""
--Input--
csv_line: a line read in from a csv file
time_cols: list of indices in csv_line which contain times.

--Output--
a Patient data structure, constructed from the times in csv_line
"""
def convertLineToPatient(csv_line, time_cols):
  global decreasingTimeCount
  # Convert raw csv line to list
  line = process_line(csv_line)
  
  times = []
  i = 0
  # Extract relevant time fields
  for f in time_cols:
    try:
      times.append(float(line[f]))
    except:
      # Use previous time if current time invalid
      if missingTime == "Use Previous Time":
        try:
          times.append(times[i-1])
        except:
          return None
      else:
        times.append(-1)
    i += 1
  times = [round(x, 5) for x in times]
    # Use time fields to construct an Patient
  patient = Patient(times)
  
  # throw out patient if decreasing times
  prev_t = patient.times[0]
  for t in patient.times[1:]:
    if t < prev_t:
      decreasingTimeCount += 1
      return None
    prev_t = t
  
  patient = curfewCheck(patient)
  
  return patient
	
"""
--Input--
init_time, end_time: excel format times, specifying range of data to include

--Output--
A list of TimeSlice data structures, starting at init_time, and ending at 
end_time. Duration of each time slice is dt.
"""
def initTimeSlices(init_time, end_time):
  data = []
  time = init_time
  while (time < end_time):
    slice = TimeSlice(time, time + dt)
    data.append(slice)
    time += dt
  return data

"""
--Input--
initial_time, end_time: excel formatted date-times, representing the range
                        of input data to be read
dt: duration of time slices, in days
in_fp: file pointer to input file
time_cols: list of indices of columns which contain times
extra_fields: list of indices of columns which contain extra fields

--Output--
Lines from .csv file are converted to Patients, stored in the global list 'patients'.
Timeslice data structures initialized, stored in the global list 'slices'
"""
def readData(init_time, end_time, in_fp, time_cols, extra_fields):
  global slices
  global patients  
  
  lines = in_fp.readlines()[1:]
  slices = initTimeSlices(init_time, end_time) # this holds all timeslices

  # Convert all lines to patients
  for line in lines:
    patient = convertLineToPatient(line, time_cols)
    
    # If an patient is None or 0, there was a problem in converting it from a line
    if patient != None and patient != 0:
      if (patient.t_in < end_time) and (patient.t_out >= init_time):

        fields = process_line(line)
        
        # Extra data (ie. visit charactertistics) added
        for extra_index in extra_fields:
          patient.addData(fields[int(extra_index)])
          
      patients.append(patient)

      
"""
Makes a directory, then goes through each user-defined segment and writes each
one to a .csv file within the new directory.
"""
def writeData():
  global decreasingTimeCount
  # Create directory to contain output files
  dirname = get_dir_name()
  os.makedirs(dirname)
  
  for seg in segments:
    # Create output file name based on which times the segment is built from
    out_file = os.path.join(dirname, seg.name + ' - t' + str(seg.t_in_col) + '-t' + str(seg.t_out_col) + '.csv')
    out_fd = open(out_file, 'w+')    
    
    # Write file headers
    out_fd.write("TSLICE_START,FLUX,DENSITY,MEANDUR,PATIENT_TIMES\n")
    
    # Copy of slices, so that empty slices can be used for each new segment
    tslices = copy.deepcopy(slices)
    for tslice in tslices:
      for patient in patients:
        
        # Check conditions required of patient to fit into current tslice
        if filterCheck(patient, seg) == True:
          if not ((patient.times[seg.t_in_col]) < 0 or (patient.times[seg.t_out_col]) < 0):
            if (patient.times[seg.t_in_col] < tslice.interval[1] ) and (patient.times[seg.t_out_col] >= tslice.interval[0]):
              tslice.addPatient(patient)
      
      tslice.writeSlice(out_fd, seg.t_in_col, seg.t_out_col)
    out_fd.close()
    
  report_file = os.path.join(dirname, "Report.txt")
  report_fd = open(report_file, 'w+')
  report_fd.write("Patients with decreasing times not included: " + str(decreasingTimeCount))
  
      
  
"""
--Input--
init_time, end_time: excel formatted date-times, representing the range
                        of input data to be read
new_dt: duration of time slices, in days
in_file: path to input file
time_cols: list of indices of columns which contain times in data
extra_fields: list of indices of columns which contain extra fields

A function to initiate the data reading phase from the GUI.
Opens the user-specified input file and reads it into data structures.
"""
def callFromGUI(in_file, time_cols, init_time, end_time, new_dt, extra_fields):
  global dt, slices, patients, segments
  dt = new_dt
  DataStructures.dt = new_dt
  fp = open(in_file, 'r')
  slices = []
  patients = []
  segments = []
  readData(init_time, end_time, fp, time_cols, extra_fields)
  fp.close()
  
"""
Add a segment to the global list of segments
"""
def addSegment(cols, name):
  global segments
  seg = Segment(cols, name)
  segments.append(seg)
  
"""
Runs each filter on a patient in a given segment
"""
def filterCheck(patient, seg):
  for filt in seg.filters:
    if len(patient.extra_data) == 0:
      return False
    if not filt.runFilter(patient.extra_data[filt.c_num]):
      return False
  return True

"""
Adds an includeFilter to segment specified by seg_index.
"""
  
def addFilter(op, val, c_num, seg_index):
  global segments
  filt = Filter(c_num, op, val)
  segments[seg_index].addFilter(filt)
  
"""
Reads first line of file.
Returns a dict:
  key - Name of column
  value - column number
"""
def readHeader(filename):
  in_fp = open(filename, 'r')
  header_list = in_fp.readline().split(',')
  header = {}
  
  for i in range(0,len(header_list)):
    header_list[i] = str(i) + " | " + header_list[i]
    header_list[i] = header_list[i].rstrip('\n')
    header[header_list[i]] = i
    
  print("Header Data Read")
  return header

"""
Adds a curfew to the global list of curfews.
"""
def addCurfew(tcol1, tcol2, option, val):
  global curfews
  curf = Curfew(tcol1, tcol2, option, val)
  curfews.append(curf)
  print(curfews)
  
"""
Takes a patient, and re-adjusts their time data to
adhere to the currently defined curfews
"""
def curfewCheck(patient):
  global curfews
  new_patient = patient
  for curf in curfews:
    if new_patient.times[curf.t_end_index] - new_patient.times[curf.t_start_index] > curf.time:
      if curf.c_type == "Option 1":
        new_patient.times[curf.t_end_index] = new_patient.times[curf.t_start_index] + curf.time

      else:
        DataStructures.limbo_states[curf.t_start_index] = curf.time
        #new_patient.times.insert(curf.t_start_index, new_patient.times[curf.t_start_index] + curf.time)
      print("Curfewed!")
      print(new_patient.times)      

  return new_patient