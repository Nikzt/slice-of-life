import xlrd

dt = 0.125
filters = []
limbo_states = {}
printAgents = "no"

def numToDateTime(num):
  tup = list(xlrd.xldate_as_tuple(num, 0))
  tup = [str(x) for x in tup]
  for c in range(0, 6):
    if len(tup[c]) == 1:
      tup[c] = "0" + tup[c]

  date = "{0}-{1}-{2} {3}:{4}:{5}".format(tup[0], tup[1],
    tup[2], tup[3], tup[4], tup[5])
  return date


class TimeSlice:
  def __init__(self, start_interval, end_interval):
    self.interval = [round(start_interval, 5), round(end_interval, 5)]
    self.num_agents = 0
    self.agents = []
    
  def addAgent(self, agent):
    self.agents.append(agent)
    self.num_agents += 1
  
  # Values that can be calculated from timeslice and agents that 
  # appear in that timeslice
  def calculateFlux(self, t_in_index, t_out_index):
    if self.agents == []:
      return 0
    return sum([p.Xij(self.interval, t_in_index, t_out_index) for p in self.agents]) / dt
  def calculateDensity(self, t_in_index, t_out_index):
    if self.agents == []:
      return 0
    return sum([p.tij(self.interval, t_in_index, t_out_index) for p in self.agents]) / dt
  def calculateMeanDur(self, t_in_index, t_out_index):
    if self.calculateFlux(t_in_index, t_out_index) == 0:
      return 0
    if self.agents == []:
      return 0	
    return self.calculateDensity(t_in_index, t_out_index)/self.calculateFlux(t_in_index, t_out_index)
  def calculateAvg(self, data_name):
    if self.agents == []:
      return 0	
    return sum([float(p.extra_data[data_name]) for p in self.agents]) / self.num_agents
  
  def writeSlice(self, fd, t_in_index, t_out_index):
    global printAgents
    # Takes an open file descriptor and writes a representation
    # of the time slice and all its agents to that descriptor, including
    # values calculated from this data
    fd.write(str(self.interval[0]) + ',')
    fd.write(str(self.calculateFlux(t_in_index, t_out_index)) + ',')
    fd.write(str(self.calculateDensity(t_in_index, t_out_index)) + ',')
    fd.write(str(self.calculateMeanDur(t_in_index, t_out_index)) + '\n')
    
    if printAgents == "yes":
      for agent in self.agents:
        agent.writeAgent(fd, self.interval)
    

        
        
class Agent:
  def __init__(self, times):
    self.num_times = len(times)
    self.times = [round(p, 5) for p in times]
    self.extra_data = []
    self.t_in = times[0]
    self.t_out = times[-1]
    
        
  def tij(self, interval, t_in_index, t_out_index):
    t_in = self.times[t_in_index]
    t_out = self.times[t_out_index]
    
    return min(t_out, interval[0] + dt) - max(t_in, interval[0])

  def Xij(self, interval, t_in_index, t_out_index):
    global limbo_states
    t_in = self.times[t_in_index]
    t_out = self.times[t_out_index]    
    Tij = self.tij(interval, t_in_index, t_out_index)
    if t_out == t_in:
      return 1

    if t_in_index in limbo_states.keys():
      
      curf = limbo_states[t_in_index]
      if t_out > t_in + curf:
        return max(0, (min((t_in + curf), interval[0] + dt) - max(t_in, interval[0])) / curf)
    
    return Tij / (t_out - t_in)
  
  def addData(self, data):
    self.extra_data.append(data)
  
  def writeAgent(self, fd, interval):
    fd.write(',,,,')
    for time in self.times:
      fd.write(str(time) + ',')
    for data in self.extra_data:
      fd.write(str(data) + ',')    
    fd.write('\n')
    
    
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