import xlrd

dt = 0.125  #initial default value for delta_t
filters = []
limbo_states = {}
printPatients = "no"  #determines whether or not to write patient
                      #data when writing time slices

"""
 A helper function to convert an excel date (represented by
 a number) to a readable date-time format
"""
def numToDateTime(num):
  tup = list(xlrd.xldate_as_tuple(num, 0))
  tup = [str(x) for x in tup]
  for c in range(0, 6):
    if len(tup[c]) == 1:
      tup[c] = "0" + tup[c]

  date = "{0}-{1}-{2} {3}:{4}:{5}".format(tup[0], tup[1],
    tup[2], tup[3], tup[4], tup[5])
  return date

"""
The data structure representing a time slice. It is a start
and end time, with an (initially empty) list of patients.
When a patient visit falls within a time slice, it can be added
with self.addPatient(patient).

This class also has internally defined functions to perform
calculations on the list of patients, as well as a funcion
to write its list of patients to a file.
"""
class TimeSlice:
  def __init__(self, start_interval, end_interval):
    self.interval = [round(start_interval, 5), round(end_interval, 5)]
    self.num_patients = 0
    self.patients = []
    
  def addPatient(self, patient):
    self.patients.append(patient)
    self.num_patients += 1
  
  # Values that can be calculated from timeslice and patients that 
  # appear in that timeslice -----------------------------------------------------
  def calculateFlux(self, t_in_index, t_out_index):
    if self.patients == []:
      return 0
    return sum([p.Xij(self.interval, t_in_index, t_out_index) for p in self.patients]) / dt

  def calculateDensity(self, t_in_index, t_out_index):
    if self.patients == []:
      return 0
    return sum([p.Tij(self.interval, t_in_index, t_out_index) for p in self.patients]) / dt

  def calculateMeanDur(self, t_in_index, t_out_index):
    if self.calculateFlux(t_in_index, t_out_index) == 0:
      return 0
    if self.patients == []:
      return 0	
    return self.calculateDensity(t_in_index, t_out_index)/self.calculateFlux(t_in_index, t_out_index)

  def calculateAvg(self, data_name):
    if self.patients == []:
      return 0	
    return sum([float(p.extra_data[data_name]) for p in self.patients]) / self.num_patients
  # -------------------------------------------------------------------------------

  # Takes an open file descriptor and writes a representation
  # of the time slice and all its patients to that descriptor, including
  # values calculated from this data
  def writeSlice(self, fd, t_in_index, t_out_index):
    global printPatients

    fd.write(str(self.interval[0]) + ',')
    fd.write(str(self.calculateFlux(t_in_index, t_out_index)) + ',')
    fd.write(str(self.calculateDensity(t_in_index, t_out_index)) + ',')
    fd.write(str(self.calculateMeanDur(t_in_index, t_out_index)) + '\n')
    
    if printPatients == "yes":
      for patient in self.patients:
        patient.writePatient(fd, self.interval)
    

        
"""
The data structure representing a patient visit. It holds the list
of times that make up the visit. Extra characteristic data about
the patient can also be added with self.addData(data).

This class also defines functions to perform traffic flow calculations
in the context of it belonging to a time slice. These functions are
used solely by the TimeSlice class.
"""
class Patient:
  def __init__(self, times):
    self.num_times = len(times)
    self.times = [round(p, 5) for p in times]
    self.extra_data = []
    self.t_in = times[0]
    self.t_out = times[-1]
    
        
  def Tij(self, interval, t_in_index, t_out_index):
    t_in = self.times[t_in_index]
    t_out = self.times[t_out_index]
    
    return min(t_out, interval[0] + dt) - max(t_in, interval[0])


  def Xij(self, interval, t_in_index, t_out_index):
    global limbo_states
    t_in = self.times[t_in_index]
    t_out = self.times[t_out_index]    
    Tij = self.Tij(interval, t_in_index, t_out_index)
    if t_out == t_in:
      return 1

    if t_in_index in limbo_states.keys():
      
      curf = limbo_states[t_in_index]
      if t_out > t_in + curf:
        return max(0, (min((t_in + curf), interval[0] + dt) - max(t_in, interval[0])) / curf)
    
    return Tij / (t_out - t_in)
  
  def addData(self, data):
    self.extra_data.append(data)
  
  # Writes patient data to an open file descriptor
  def writePatient(self, fd, interval):
    fd.write(',,,,')
    for time in self.times:
      fd.write(str(time) + ',')
    for data in self.extra_data:
      fd.write(str(data) + ',')    
    fd.write('\n')
    

"""
The data structure representing a care segment. A segment is
defined by the indices of the time columns which make up that
segment. 

Note that these indices are relative to the time columns of
interest defined by the program (ie. t0 - t2, t3 - t4, etc)
and not indices corresponding to the columns of the original
data input file.

This class is also initialized with a name, which can be changed
with self.rename(new_name). Also contains a list of filters,
which can be added with self.addFilter(filter).
"""
class Segment:
  def __init__(self, cols, name):
    self.t_in_col = cols[0]
    self.t_out_col = cols[1]
    self.name = name

    self.filters = []
    
  def addIncludeFilter(self, filt):
    self.includeFilters.append(filt)
    
  def addFilter(self, filt):
    self.filters.append(filt)
  def rename(self, new_name):
    self.name = new_name

"""
The data structure representing a filter. It is initialized
with a column number, operator, and value. self.runFilter(c)
returns false if and only if the value does not satisfy
the formula:  c <operator> value.

This return value is how the Filter class is used to
filter out data points that do not satisfy this formula.
"""
class Filter:
  def __init__(self, c_num, operator, value):
    self.c_num = c_num
    self.operator = operator
    self.value = value
    
  def runFilter(self, c):
    if self.operator == '<':
      return float(c) < float(self.value)
    elif self.operator == '<=':
      return float(c) <= float(self.value)
    elif self.operator == '>':
      return float(c) > float(self.value)
    elif self.operator == '>=':
      return float(c) >= float(self.value)
    elif self.operator == '=':
      return str(c) == str(self.value)
    elif self.operator == '!=':
      return str(c) != str(self.value)
    elif self.operator == 'not in':
      return c not in self.value
    elif self.operator == 'in':
      return c in self.value

"""
This data structure represents a curfew. It is just used
to hold the data corresponding to a user defined curfew.
"""
class Curfew:
  def __init__(self, tcol1, tcol2, c_type, time):
    self.t_start_index = tcol1
    self.t_end_index = tcol2
    # How to handle curfew:
    # 0 -> jump to next segment
    # 1 -> send to limbo state
    self.c_type = c_type
    self.time = time
    
class TimeColumn:
  def __init__(self, col_num, col_name):
    self.col_num = col_num
    self.col_name = col_name