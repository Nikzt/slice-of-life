import tkinter
from tkinter import *
import tkinter.ttk as ttk
import flows
import copy
import DataStructures
from tkinter import messagebox

from DataStructures import *

# Number of segments
seg_num = 0

# filt_nums[i] is the number of filters in the i'th segment
filt_nums = []

# filt_buttons[i] is the filter ttk.Buttons in the i'th segment
filt_buttons = []


# helper function to convert hh/mm format to excel date-time format
def hmToFloatConvert(hr, mn):
    hrc = hr
    mnc = mn
    if hr == '':
        hrc = 0
    if mn == '':
        mnc = 0

    h = float(hrc)
    m = float(mnc)


    return (h / 24) + (m / (24*60))


# helper function to add time column names to segment name
def tiConvert(name, num, char):
    for i in range(0, len(name)):
        if name[i] == '|':
            new_name = char + str(num) + ' ' + name[i:]
            return new_name



class FlowsApp(tkinter.Tk):
    """
    Window where user defines how data is read into data structures
    Also the home window
    """
    def __init__(self):
        
        # Variables holding user input data and bookkeeping
        self.filename = ''
        self.header = {}
        self.tCols = []
        self.cCols = []
        self.segButtons = []
        self.tColButtons = []
        self.cColButtons = []
        self.opsList = ['<', '<=', '>', '>=', '=', '!=', 'in', 'not in']
       
        # Segment open in editing window
        self.currentSegment = -1
        self.segDefDict = {}
        self.cFiltersDict = {}
        self.dropdownListSeg1 = ['']
        self.dropdownListSeg2 = ['']         
        
        
        
        tkinter.Tk.__init__(self)
        self.wm_title("ED Flows")
        
        # Label displaying file name
        self.fileLabel = Label(text=self.filename)

        # Frames for formatting
        self.nb = ttk.Notebook()
        self.initFrame = Frame()
        self.optionsFrame = Frame()
        self.columnsTab = Frame()
        self.columnsFrame = Frame(self.columnsTab)
        
        self.displayFrame = Frame(self.columnsTab, borderwidth=2, relief=RIDGE, padx=15)
        self.curfewFrame = Frame()
        self.curfValFrame = Frame(self.curfewFrame)

        self.dtFrame = Frame(self.optionsFrame)
        self.hFrame = Frame(self.dtFrame)
        self.mFrame = Frame(self.dtFrame)


        # Tab view for data read options
        
        
        # Labels for column display area
        self.tLabel = Label(self.displayFrame, text="Times",
                            padx=7, pady=7)
        self.cLabel = Label(self.displayFrame, text = "Visit Characteristics",
                            padx=7, pady=7)        
        
        # User input for path to .csv file
        self.csvLabel = Label(self.initFrame, text="Path to .csv file")
        
        # User input for dt
        self.dtLabel = Label(self.optionsFrame, text="delta_t")

        self.hLabel = Label(self.hFrame, text="hh")
        self.mLabel = Label(self.mFrame, text="mm")
        self.dtHEntry = ttk.Entry(self.hFrame, width=5)
        self.dtMEntry = ttk.Entry(self.mFrame, width=5)

                
        # User input for t0 - tj
        self.tColLabel = Label(self.columnsFrame, text="Select columns\ncontaining times")
        
        # ttk.Buttons to add columns
        self.tColButton = ttk.Button(self.columnsFrame, text="Add time column", command=lambda : self.addTCol())
        self.cColButton = ttk.Button(self.columnsFrame, text="Add visit characteristic", command=lambda : self.addCCol())        
          
        # User input for C0 - Cc
        self.extraLabel = Label(self.optionsFrame, text="Select columns containing\nvisit characteristics")

        # User input for data range start
        self.timeLabel = Label(self.optionsFrame, text="First time slice\nstart time")
        self.timeEntry = ttk.Entry(self.optionsFrame)
		
        self.displayPatientsLabel = Label(self.optionsFrame,  text="Display Patients\nin output")
        self.patientVar = StringVar(value = "no")
        self.displayPatientsCheckB = Checkbutton(self.optionsFrame, variable = self.patientVar,
		                                                         onvalue = "yes",
                                                                 offvalue = "no")
																 
        self.missingTimeLabel = Label(self.optionsFrame, text = "Handle Missing\nTime Fields")
        self.missingTimeVar = StringVar(value="Use Previous Time")
        self.missingTimeMenu = ttk.OptionMenu(self.optionsFrame,
                      self.missingTimeVar,"Use Previous Time", "Use Previous Time", "Ignore Time")
         
        # User input for data range end
        self.time2Label = Label(self.optionsFrame, text="Last time slice\nend time")
        self.time2Entry = ttk.Entry(self.optionsFrame)
             
        
        # ttk.Button which initiates reading of data using entries defined above
        self.readDataButton = ttk.Button(text="Read Data",
                        command=lambda : self.callFlows())
        
        # ttk.Button to open file browser
        self.browseButton = ttk.Button(self.initFrame, text="Select File", command=lambda : self.fileBrowser())
        
        
        # ttk.Button to read in header information from file
        self.headerButton = ttk.Button(self.initFrame, text="Read Column Names",
                                       state=DISABLED,
                                        command=lambda : self.getHeader(self.filename))
       
        
        # Layout ----------------------------- Main Window (1)
        self.fileLabel.pack(side=TOP)
        self.initFrame.pack(side=TOP)
        

        


        self.columnsFrame.pack(side=TOP)

        
        self.hLabel.grid(row=0, column=0)
        self.dtHEntry.grid(row=0, column=1)
        self.mLabel.grid(row=0, column=2)
        self.dtMEntry.grid(row=0, column=3)

        self.csvLabel.grid(row=0, column=0)
        self.browseButton.grid(row=0, column=1)
        self.headerButton.grid(row=0, column=2)


    

    
    """
    Gets header names from .csv files. Also displays the rest of the layout
    for the main window.
    """
    def getHeader(self, filename):


        self.header = flows.readHeader(filename)
        self.headerOG = flows.readHeader(filename)
        self.dropdownList = sorted(self.header, key=self.header.get)
        self.tColVar = StringVar()
        self.tColVar.set("Choose Column")
        self.tDropdown = ttk.OptionMenu(self.columnsFrame,
                                    self.tColVar, "Choose Column", *self.dropdownList,
                                    command=lambda x: self.updateButtons())

        
        self.cColVar = StringVar()
        self.cColVar.set("Choose Column")
        self.cDropdown = ttk.OptionMenu(self.optionsFrame,
                                    self.cColVar, *self.dropdownList)

     

        #Curfews
        
        
        self.tcol1List = copy.deepcopy(self.dropdownListSeg1)
        self.tcol2List = copy.deepcopy(self.dropdownListSeg2)    
        
        self.tcol1Var = StringVar()
        self.tcol1Var.set("Choose Curfew Start")
        self.tcol2Var = StringVar()
        self.tcol2Var.set("Choose Curfew End")
        self.curfewVar = StringVar()
        self.curfewVar.set("Choose Curfew Type")
        
        self.tcol1Dropdown = ttk.OptionMenu(self.curfewFrame,
                                        self.tcol1Var, "Choose Curfew Start", *self.tcol1List)
        self.tcol2Dropdown = ttk.OptionMenu(self.curfewFrame,
                                        self.tcol2Var, "Choose Curfew End", *self.tcol2List)
        self.curfewDropdown = ttk.OptionMenu(self.curfewFrame,
                                         self.curfewVar, "Option 1",
                                         "Option 2")
        

        
        self.curfewButton = ttk.Button(self.curfewFrame, text="Add Curfew",
                                   command=lambda : self.addCurfew(self.tcol1Var.get(), self.tcol2Var.get(),
                                                                   self.curfewVar.get(), self.curfewEntry.get()))
        self.curfewEntry = ttk.Entry(self.curfValFrame)
        self.curfewLabel = Label(self.curfewFrame, text="Curfews")
        self.curfValLabel = Label(self.curfValFrame, text="Time (days)")
        
        
        
        # Display other fields
        # Layout ------------------------------ Main Window (2)
        #TimeSlice Tab
        self.timeLabel.grid(row=4, column=0)
        self.timeEntry.grid(row=4, column=1)  
        self.time2Label.grid(row=5, column=0)
        self.time2Entry.grid(row=5, column=1) 
        self.dtLabel.grid(row=1, column=0)
        self.hFrame.grid(row=1, column=1)
        self.mFrame.grid(row=1, column=2)
        self.dtFrame.grid(row=1, column=1)
        self.displayPatientsLabel.grid(row=4, column=2)
        self.displayPatientsCheckB.grid(row=4, column=3)
        self.missingTimeLabel.grid(row=1, column=2)
        self.missingTimeMenu.grid(row=1, column=3)

        #Column Tab
        self.tLabel.grid(row=0, column=0)
        self.cLabel.grid(row=0, column=1)   
        self.tDropdown.grid(row=0,column=2)
        self.tColButton.grid(row=0,column=0)
        self.cColButton.grid(row=0, column=1)  
        
        #Curfew Tab
        self.curfewLabel.grid(row=3, column=1)
        self.curfValFrame.grid(row=5, column=1)
        self.curfValLabel.grid(row=0, column=0)
        self.tcol1Dropdown.grid(row=4,column=0)
        self.tcol2Dropdown.grid(row=5, column=0)
        self.curfewDropdown.grid(row=4, column=1)
        self.curfewEntry.grid(row=0, column=1)
        self.curfewButton.grid(row=4, column=2) 

        #Tab View
        self.nb.pack(side=LEFT)
        self.nb.add(self.optionsFrame, text="Timeslice Options")
        self.nb.add(self.columnsTab, text="Define Columns")
        self.nb.add(self.curfewFrame, text="Define Curfews")
        

          

        self.readDataButton.pack(side=BOTTOM)      
        
        #Disable add column ttk.Buttons until valid column selected
        if (self.tColVar.get() == "Choose Column"):
            self.tColButton.config(state=DISABLED)
            self.cColButton.config(state=DISABLED)
        else:
            self.tColButton.config(state="normal")
            self.cColButton.config(state="normal")            
        

        

    """
    Window which opens when data is read, and allows user to define segments
    """
    def segmentsWindow(self):
        
        # Window formatting
        self.window = Toplevel(self)
        self.leftFrame = Frame(self.window, padx=10, pady=10)
        
        self.segframes = Frame(self.leftFrame)
        self.framer = Frame(self.leftFrame)
        
        
        
        # User input for defining segments
        
        self.dropdownListSeg1 = sorted(self.segDefDict, key=self.segDefDict.get)
        self.dropdownListSeg2 = sorted(self.segDefDict, key=self.segDefDict.get)
        self.seg1Var = StringVar()
        self.seg2Var = StringVar()
        
        self.seg1Var.set("Choose t_in")
        self.seg2Var.set("Choose t_out")
            
        self.seg1Dropdown = ttk.OptionMenu(self.framer,
                                    self.seg1Var, "Choose t_in", *self.dropdownListSeg1,
                                    command=lambda x: self.updateButtons())
        self.seg2Dropdown = ttk.OptionMenu(self.framer,
                                            self.seg2Var, "Choose t_out", *self.dropdownListSeg2,
                                            command=lambda x: self.updateButtons())        

        
        
               
        self.segmentButton = ttk.Button(self.framer,
                                    text="Add Segment",
                                    
                                    command=lambda : self.addSegment())
        
        # ttk.Button to add segment based on input above
        self.A = ttk.Button(self.leftFrame, text="Generate Report",
                         command=lambda : self.generateReport())
         
        # Layout ------------------------------ Segments Window
        self.leftFrame.grid(row=0, column=0)
        self.segframes.grid(row=0,column=0)
        self.framer.grid(row=1,column=0)   
        
        self.seg1Dropdown.grid(row=0, column=0)
        self.seg2Dropdown.grid(row=0, column=1)
        self.A.grid(row=2, column=0) 
        self.segmentButton.grid(row=0, column=2)
        

        
    """
    Window opened when a segment ttk.Button is clicked for editing.
    """
    def editSegmentWindow(self, segnumber):
        global filt_buttons
        self.currentSegment = segnumber
        print("Editing segment " + str(segnumber))
        
        try:
            # Update segment editing window
            self.segwindow
            self.segLabel.config(text="Editing {0}".format(flows.segments[self.currentSegment].name))
            for i in range(0, len(filt_buttons)):
                for j in range(0,len(filt_buttons[i])):
                    if i == segnumber:
                        filt_buttons[i][j].grid(row=j,column=0)
                    else:
                        filt_buttons[i][j].grid_remove()
                              
        except:
        
            # Create window if first time calling this function
            # Window formatting
            self.segwindow = Frame(self.window, padx=10, pady=10, borderwidth=3, relief=RIDGE)
            self.segwindow.grid(row=1, column=0)
            self.topFrame = Frame(self.segwindow)
            self.filtsFrame = Frame(self.segwindow)
            self.coreFrame = Frame(self.segwindow)
            self.topFrame.grid(row=0, column=0)
            self.filtsFrame.grid(row=1, column=0)
            self.coreFrame.grid(row=2, column=0)
            
            # Title label
            self.segLabel = Label(self.topFrame, 
                text="Editing {0}".format(flows.segments[self.currentSegment].name))
            
            
            # User input for defining filters
            
            self.opsVar = StringVar()
            self.opsVar.set("Choose Filter Operator")
            self.opsDropdown = ttk.OptionMenu(self.coreFrame,
                                        self.opsVar, *self.opsList)

            
            
            if len(self.cFiltersDict) == 0:
                self.cList = ['   ']
            else:
                self.cList = self.cFiltersDict.keys()
            self.cVar = StringVar()
            self.cVar.set("Choose Visit Characteristic")
            self.cDropdown = ttk.OptionMenu(self.coreFrame,
                                        self.cVar, *self.cList)

                     
            
            self.filterEntry = ttk.Entry(self.coreFrame)
            self.filterButton = ttk.Button(self.coreFrame,
                                        text="Add Filter",
                                        
                                        command=lambda : self.addFilter(self.currentSegment))
            self.filterLabel = Label(self.coreFrame, text="Filters")
            
            
    
            # Rename segment
            self.nameEntry = ttk.Entry(self.topFrame)
            self.nameButton = ttk.Button(self.topFrame, text="Rename Segment",
                                    
                                     command=lambda : self.renameSegment(self.nameEntry.get(), self.currentSegment))
            
            # Layout
            self.nameButton.grid(row=1, column=1)
            self.opsDropdown.grid(row=1, column=1)
            self.nameEntry.grid(row=1, column=0)
            self.filterButton.grid(row=1, column=3)
            self.filterEntry.grid(row=1, column=2)
            self.cDropdown.grid(row=1, column=0)
            self.segLabel.grid(row=0,column=0)
            self.filterLabel.grid(row=0, column=1)
            
#------------------------------ Non-layout Functions ---------------------------------------------
    
    def renameSegment(self, name, segnumber):
        seg = flows.segments[segnumber]
        flows.segments[segnumber].rename(name)
        self.segLabel.config(text="Editing {0}".format(flows.segments[self.currentSegment].name))
        self.segButtons[segnumber].grid_remove()
        
        self.segButton = ttk.Button(self.segframes, text="{0}: t{1}-t{2}".format(name, seg.t_in_col, seg.t_out_col),
                                command=lambda : self.editSegmentWindow(segnumber))
        self.segButton.grid(row=segnumber, column=0)        
        self.segButtons[segnumber] = self.segButton
        
        self.nameEntry.delete(0, 'end')
        print("Segment {0} renamed to {1}".format(segnumber, name))
        
    """
    Called when the 'Add Filter' ttk.Button is clicked
    Adds a filter to the global list of filters.
    """
    def addFilter(self, segnumber):
        global filt_buttons
        
        # Read and format user input
        op = self.opsVar.get()
        val = self.filterEntry.get()
        c_num = int(self.cFiltersDict[self.cVar.get()])
        
        if op in ['in', 'not in']:
            val = self.filterEntry.get().split(',')
            
        
        # Add filter to flows.py
        flows.addFilter(op, val, c_num, segnumber)
        print("Filter added to segment " + str(segnumber))
        self.filterEntry.delete(0, 'end')
        
        # Keep track of index used to delete filter
        filt_del_index = filt_nums[segnumber]
        
        # ttk.Button to delete filter 
        self.filtButton = ttk.Button(self.filtsFrame, text=self.cVar.get() + " " + op + " " + str(val),
                                  command=lambda : self.deleteFilter(filt_del_index, segnumber))
        # ttk.Buttons must be kept track of in a 2-dimensional array
        print(self.filtButton)
        try:
            filt_buttons[segnumber].append(self.filtButton)
        except:
            filt_buttons.append([])
            filt_buttons[segnumber].append(self.filtButton)        
        self.filtButton.grid(row=filt_nums[segnumber], column=0)
        
        
            
        filt_nums[segnumber] += 1
    
    """
    Called when a ttk.Button representing a filter is clicked
    Removes filter from all data structures that keep track of it
    """
    def deleteFilter(self, index, segnumber):
        
        global filt_buttons
        filt_buttons[segnumber][index].destroy()
        del(filt_buttons[segnumber][index])
        filt_nums[segnumber] -= 1
        del(flows.segments[segnumber].filters[index])
    
    def fileBrowser(self):
        from tkinter.filedialog import askopenfilename
        self.tempFilename = askopenfilename(filetypes=(("CSV Files", "*.csv"),("All Files","*.*")))
        if not (self.tempFilename == '' and self.filename != ''):
            self.filename = self.tempFilename
        if self.filename != '':
            self.headerButton.config(state="normal")
            self.fileLabel.config(text=self.filename, borderwidth=2, relief=RIDGE)
        else:
            self.headerButton.config(state="disabled")
            self.fileLabel.config(text=self.filename, borderwidth=0)
    
    # adds a curfew to the list of curfews
    def addCurfew(self, tcol1Key, tcol2Key, option, value):
        tcol1 = self.segDefDict[tcol1Key]
        tcol2 = self.segDefDict[tcol2Key]
        val = float(value)
        flows.addCurfew(tcol1, tcol2, option, val)
    
    # Updates the visual display of defined columned
    def displayArea(self, coord, name, char, colnum):
        displayLabelFrame = ttk.Frame(self.displayFrame)
        displayLabel = ttk.Label(displayLabelFrame,
                                  text=tiConvert(name, coord[0] - 1, char))
        if char == "t":
            buttonIndex = len(self.tColButtons)
            deleteColumnButton = ttk.Button(displayLabelFrame, text="✕", width=3,
                   command=lambda : self.deleteColumn(name, coord, char, colnum, buttonIndex))
            self.tColButtons.append(displayLabelFrame)
        else:
            buttonIndex = len(self.cColButtons)
            self.cColButtons.append(displayLabelFrame)
            deleteColumnButton = ttk.Button(displayLabelFrame, text="✕", width=3,
                   command=lambda : self.deleteColumn(name, coord, char, colnum, buttonIndex))
        displayLabel.grid(row=0, column=0)
        deleteColumnButton.grid(row=0, column=1)
        displayLabelFrame.grid(row=coord[0], column=coord[1])
    
    # Deletes a visit characteristic column or time column
    def deleteColumn(self, name, coord, char, colnum, buttonIndex):
        
        if char == "t":
            print(self.tCols)

            self.tCols.remove(colnum)
            self.tColButtons[buttonIndex].destroy()
            #del self.tColButtons[buttonIndex]

            print(self.tCols)
        else:
            print(self.cCols)
            self.cCols.remove(colnum)
            self.cColButtons[buttonIndex].destroy()
            #del self.cColButtons[buttonIndex-1]
            print(self.cCols)
    """
    Call writeData from flows.py
    """
    def generateReport(self):
        if len(flows.segments) < 1:
            messagebox.showinfo("Error", "Please add at least one segment")
            return
        flows.writeData()
        print("Report Generated")
        
    """
    Add a segment to the list of segments in flows.py, as defined by user.
    """
    def addSegment(self):
        global seg_num
        
        # Read and format user input for defining segment
        cols = [self.segDefDict[self.seg1Var.get()], self.segDefDict[self.seg2Var.get()]]
        
        # Add segment to list of segments in flows.py
        seg_name = "Segment {0}".format(seg_num)
        flows.addSegment(cols, seg_name)
        print("Segment Added")
        
        # Copy of seg_num to keep editSegment argument seperate for each ttk.Button
        function_segnum = seg_num
        
        # Create a ttk.Button which can be clicked to edit segment
        self.segButton = ttk.Button(self.segframes, text="{0}: t{1}-t{2}".format(seg_name, cols[0], cols[1]),
                                 command=lambda : self.editSegmentWindow(function_segnum))
        self.segButton.grid(row=seg_num, column=0)
        self.segButtons.append(self.segButton)
        
        filt_buttons.append([])
        seg_num += 1
        filt_nums.append(0)


    def updateButtons(self):
        if (self.tColVar.get() == "Choose Column"):
            self.tColButton.config(state=DISABLED)
            self.cColButton.config(state=DISABLED)
        else:
            self.tColButton.config(state="normal")
            self.cColButton.config(state="normal")           
    
    # Adds a time column
    def addTCol(self):
        
        key = self.tColVar.get()
        colnum = self.header[key]
        if colnum not in self.tCols:
            self.tCols.append(colnum)
        else:
            messagebox.showinfo("Error", "This column has already been added")
            return
        
        # Update drop down menus for segment defining
        self.segDefDict[tiConvert(key, len(self.tCols) - 1, 't')] = len(self.tCols) - 1
        
        # Recreate drop down menu to update column options
        

        self.dropdownList = sorted(self.header, key=self.header.get)
        self.tDropdown.destroy()
        self.tDropdown = ttk.OptionMenu(self.columnsFrame,
                                    self.tColVar, "Choose Column", *self.dropdownList,
                                    command=lambda x: self.updateButtons())  

        self.tDropdown.grid(row=0,column=2)
        self.tColVar.set("Choose Column")
        
        self.updateButtons()
        self.displayArea([len(self.tCols),0], key, 't', colnum)
        
        
        
        self.dropdownListSeg1 = sorted(self.segDefDict, key=self.segDefDict.get)
        self.dropdownListSeg2 = sorted(self.segDefDict, key=self.segDefDict.get)  
        
        #self.tcol1Dropdown.config(*self.dropdownListSeg1)
        
        self.tcol1Dropdown.destroy()
        self.tcol1Dropdown = ttk.OptionMenu(self.curfewFrame, self.tcol1Var,
                                        "Choose Curfew Start", *self.dropdownListSeg1)
        self.tcol2Dropdown.destroy()
        self.tcol2Dropdown = ttk.OptionMenu(self.curfewFrame, self.tcol2Var,
                                        "Choose Curfew End", *self.dropdownListSeg2) 
        
        self.tcol1Dropdown.grid(row=4,column=0)
        self.tcol2Dropdown.grid(row=5, column=0)      
        self.displayFrame.pack(side=BOTTOM)  
        print("Added time column")
        
    # Adds a visit characteristic column
    def addCCol(self):
        
        key = self.tColVar.get()
        colnum = self.header[key]
        if colnum not in self.cCols:
            self.cCols.append(colnum)
        else:
            messagebox.showinfo("Error", "This column has already been added")
            return
        
        # Update drop down menus for segment defining
        self.cFiltersDict[tiConvert(key, len(self.cCols) - 1, 'c')] = len(self.cCols) - 1        
        
        # Recreate drop down menu to update column options

        self.dropdownList = sorted(self.header, key=self.header.get)
        self.tDropdown.destroy()
        self.tDropdown = ttk.OptionMenu(self.columnsFrame,
                                    self.tColVar, "Choose Column", *self.dropdownList,
                                    command=lambda x: self.updateButtons())  

        self.tDropdown.grid(row=0,column=2)
        self.tColVar.set("Choose Column")        
        
        
        self.updateButtons()
        self.displayArea([len(self.cCols),1], key, 'c', colnum)
        self.displayFrame.pack(side=BOTTOM)
        print("Added visit characteristic column")




    
    """
    Function called when ttk.Button for 'Read Data' is clicked.
    Calls the function callFromGUI from flows.py, using the 
    user defined inputs.
    """
    def callFlows(self):
        
        try: 
            # Call with user-defined inputs, if they are valid
            # Extract and format user-defined inputs
            dt = hmToFloatConvert(self.dtHEntry.get(),
                                  self.dtMEntry.get())
        except:
            messagebox.showinfo("Error", "Please enter a valid time for delta_t")
            return
        try:
            start_time = float(self.timeEntry.get())
            end_time = float(self.time2Entry.get())         
              
        except:
            messagebox.showinfo("Error", "Please enter a valid time slice range")
            return 
			
        if len(self.tCols) < 2:
            messagebox.showinfo("Error", "Please pick at least two time columns\nto read from the file")
            
        DataStructures.printPatients = self.patientVar.get()
        flows.missingTime = self.missingTimeVar.get()
        flows.callFromGUI(self.filename, self.tCols, start_time, end_time, dt, self.cCols)

	
            
        # Open next window
        self.segmentsWindow()
        
        
# Runs the GUI
app = FlowsApp()
app.mainloop()

