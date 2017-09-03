import tkinter
from tkinter import *
import tkinter.ttk as ttk
import pandas as pds
import matplotlib
import xlrd
import copy
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def numToTime(num):
  print(num)
  tup = list(xlrd.xldate_as_tuple(round(num, 5) % 1, 0))
  tup = [str(x) for x in tup]
  for c in range(0, 6):
    if len(tup[c]) == 1:
      tup[c] = "0" + tup[c]

  time = "{0}:{1}".format(tup[3], tup[4])
  return time


class PlotsApp(tkinter.Tk):

	def __init__(self):
		self.filename = ''
		self.plot_index = 0


		tkinter.Tk.__init__(self)
		self.wm_title("ED Flows Analysis Tool")
		self.initFrame = Frame()
		self.displayFrame = Frame()
		self.plotFrame = Frame()
		self.plotOptionList = ["Flux vs. Time of Day", "Density vs. Time of Day", "LoS vs. Time of Day",
										"Flux vs. Density", "LoS vs. Density"]

		self.plotVar = StringVar(value = "Flux vs. Time of Day")
		self.plotMenu = ttk.OptionMenu(self.displayFrame,
                      self.plotVar,"Flux vs. Time of Day", *self.plotOptionList)
					  
		self.plotButton = ttk.Button(self.displayFrame, text="Display Plot", command=lambda : self.displayPlot())
		self.browseButton = ttk.Button(self.initFrame, text="Select File", command=lambda : self.fileBrowser())
		self.readDataButton = ttk.Button(self.initFrame, text="Read Data", state="disabled", command=lambda : self.readData())

		self.fluxPlotButton = Button(self.displayFrame, text="Plot Flux", padx=5,
									pady=5, command=lambda : self.fluxPlot())
		self.densPlotButton = Button(self.displayFrame, text="Plot Density", padx=5,
									pady=5, command=lambda : self.densPlot())
		self.losPlotButton = Button(self.displayFrame, text="Plot LoS", padx=5,
									pady=5, command=lambda : self.losPlot())
		self.fluxDensButton = Button(self.displayFrame, text="Plot Flux/Density", padx=5,
									pady=5, command=lambda : self.fluxDensPlot())
		self.losDensButton = Button(self.displayFrame, text="Plot LoS/Density", padx=5,
									pady=5, command=lambda : self.losDensPlot())							
									
		self.exportPlotButton = ttk.Button(self.displayFrame, text="Export Plot", command=lambda : self.exportPlot())
		self.exportDataButton = ttk.Button(self.displayFrame, text="Export Mean Data", command=lambda : self.exportData())
		self.exportErrorsButton = ttk.Button(self.displayFrame, text="Export Error (SD) Data", command=lambda : self.exportErrors())
									
		self.nextButton = ttk.Button(self.plotFrame, text=">", command=lambda : self.nextPlot("next"), state="disabled")
		self.prevButton = ttk.Button(self.plotFrame, text="<", command=lambda : self.nextPlot("prev"), state="disabled")



		self.fluxMean = Label(self.displayFrame)
		self.densityMean = Label(self.displayFrame)
		self.fluxVar = Label(self.displayFrame)
		self.densityVar = Label(self.displayFrame)

		self.initFrame.pack(side=TOP)
		self.plotFrame.pack(side=TOP)
		self.displayFrame.pack(side=TOP)
		self.browseButton.grid(row=0, column=0)
		self.readDataButton.grid(row=0, column=1)
		
		
		self.fluxMean.grid(row=2, column=1)
		self.densityMean.grid(row=3, column=1)
		self.fluxVar.grid(row=4, column=1)
		self.densityVar.grid(row=5, column=1)
		

	def displayPlot(self):
		val = self.plotVar.get()
		if val == "Flux vs. Time of Day":
			self.fluxPlot()
		elif val == "Density vs. Time of Day":
			self.densPlot()
		elif val == "LoS vs. Time of Day":
			self.losPlot()
		elif val == "Flux vs. Density":
			self.fluxDensPlot()
		elif val == "LoS vs. Density":
			self.losDensPlot()
		
	def fileBrowser(self):
		from tkinter.filedialog import askopenfilename
		self.filename = askopenfilename(filetypes=(("CSV Files", "*.csv"),("All Files","*.*")))
		if self.filename != '':
			self.readDataButton.config(state="normal")

		else:
			self.readDataButton.config(state="disabled")

	def readData(self):
		
		# Display plot buttons
		#self.fluxPlotButton.grid(row=1, column=0)
		#self.losPlotButton.grid(row=1, column=1)
		#self.densPlotButton.grid(row=1, column=2)
		#self.fluxDensButton.grid(row=1, column=3)
		#self.losDensButton.grid(row=1, column=4)
		self.plotButton.grid(row=1, column=1)
		self.plotMenu.grid(row=1, column=0)
		self.nextButton.grid(row=0, column=2)
		self.prevButton.grid(row=0, column=0)
		
		self.exportPlotButton.grid(row=6, column=1)
		self.exportDataButton.grid(row=7, column=1)
		self.exportErrorsButton.grid(row=8, column=1)
		
		# Read .csv into DataFrame and group by time of day
		self.data = pds.read_csv(self.filename, index_col="TSLICE_START")
		df = self.timeOfDayConvert(pds.DataFrame(self.data))
	
		
		self.means = df.mean()
		self.groupByTime()
		self.newMeans = copy.deepcopy(self.means)
		self.newMeans.reset_index(inplace=True)
		self.newMeans.set_index("DENSITY", inplace=True)
		#rrow = self.means.iloc[0]
		#rrow.rename("24:00")
		#self.means =  self.means.append(rrow)
		self.errors = df.std()
		self.errors.to_csv("standard-deviation.csv")

		self.dfFlux = pds.DataFrame(self.means["FLUX"], self.means.index)
		self.dfLOS = pds.DataFrame(self.means["MEANDUR"], self.means.index)
		self.dfDensity = pds.DataFrame(self.means["DENSITY"], self.means.index)
		

		self.fig = Figure(figsize=(7, 5), dpi=100)
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfLOS.plot(ax=self.ax, marker="o", yerr=self.errors)
		dfPlot.set_ylim(0)
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row=0, column=1)

		self.fluxMean.config(text="Flux Mean: " + str(self.data["FLUX"].mean()))
		self.densityMean.config(text="Density Mean: " + str(self.data["DENSITY"].mean()))
		self.fluxVar.config(text="Flux SD: " + str(self.data["FLUX"].std()))
		self.densityVar.config(text="Density SD: " + str(self.data["DENSITY"].std()))

	def fluxPlot(self):
		self.ax.clear()
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfFlux.plot(ax=self.ax, marker="o", yerr=self.errors)
		dfPlot.set_xlabel("Time of Day")
		dfPlot.set_ylim(0)
		self.canvas.draw()
		
	def losPlot(self):
		self.ax.clear()
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfLOS.plot(ax=self.ax, marker="o", yerr=self.errors)
		dfPlot.set_xlabel("Time of Day")
		dfPlot.set_ylim(0)
		self.canvas.draw()
	def densPlot(self):
		self.ax.clear()
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfDensity.plot(ax=self.ax, marker="o", yerr=self.errors)
		dfPlot.set_xlabel("Time of Day")
		dfPlot.set_ylim(0)
		self.canvas.draw()
		
	def fluxDensPlot(self):
		
		self.nextPlot("fluxDens")
		self.prevButton.config(state="normal")
		self.nextButton.config(state="normal")
		
	def losDensPlot(self):
		
		self.dfLosDens = pds.DataFrame(data = self.newMeans["MEANDUR"], index = self.newMeans.index)
		self.ax.clear()
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfLosDens.plot(ax=self.ax, style="o", yerr=self.errors["MEANDUR"], xerr=self.errors["DENSITY"])
		dfPlot.set_xlabel("Density")
		dfPlot.set_ylabel("LoS")
		dfPlot.set_ylim(0)
		dfPlot.set_xlim(0,70)
		self.canvas.draw()
	
	def nextPlot(self, calling_button):
		if calling_button == "next":
			self.plot_index += 1
			if self.plot_index >= len(self.time_list):
				self.plot_index = 0
		elif calling_button == "prev":
			self.plot_index -= 1
			if self.plot_index < 0:
				self.plot_index = len(self.time_list) - 1
		else:
			self.plot_index = 0
		self.dfNext = pds.DataFrame(data = self.plot_dict[self.time_list[self.plot_index]].set_index("FLUX")["DENSITY"])
		self.ax.clear()
		self.ax = self.fig.add_subplot(111)
		dfPlot = self.dfNext.plot(ax=self.ax, style="o", title=self.time_list[self.plot_index], legend=None)
		dfPlot.set_xlabel("Density")
		dfPlot.set_ylabel("Flux")
		dfPlot.set_ylim(0,70)
		dfPlot.set_xlim(0,250)
		self.canvas.draw()
		
		
			

	def timeOfDayConvert(self, df):
		df.reset_index(inplace = True)
		df["TSLICE_START"] = df["TSLICE_START"] % 1
		df["TSLICE_START"].round(5)
		#df = df.append(rrow)
		df["TSLICE_START"] =  df["TSLICE_START"].apply(lambda x : numToTime(x))
		df.set_index("TSLICE_START", inplace=True)
		self.group_df = copy.deepcopy(df)
		new_df = df.groupby(df.index)
		
		

		return new_df

	def exportPlot(self):
		from tkinter.filedialog import asksaveasfilename
		filename = asksaveasfilename(filetypes=(("PDF Files", "*.pdf"),("All Files","*.*")))
		self.fig.savefig(filename)
		
	def exportData(self):
		from tkinter.filedialog import asksaveasfilename
		filename = asksaveasfilename(filetypes=(("CSV Files", "*.csv"),("All Files","*.*")), defaultextension = ".csv")
		self.means.to_csv(filename)
		
	def exportErrors(self):
		from tkinter.filedialog import asksaveasfilename
		filename = asksaveasfilename(filetypes=(("CSV Files", "*.csv"),("All Files","*.*")), defaultextension = ".csv")
		self.errors.to_csv(filename)
	
	def groupByTime(self):
		time_series = self.means.index
		self.time_list = time_series.tolist()
		self.plot_dict = {}
		for time in self.time_list:
			for index, row in self.group_df.iterrows():
				if index in self.plot_dict.keys():
					self.plot_dict[index] = self.plot_dict[index].append(row)
					
				else:
					self.plot_dict[index] = pds.DataFrame()
	
			
	
		

		

app = PlotsApp()
app.mainloop()