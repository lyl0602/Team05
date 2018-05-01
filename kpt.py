import numpy as np
from distance import Distance
from csv_reader import CrimeDataModel as CDM 
import pandas as pd
import requests
import json
import urllib.parse
import os
import sys
import re
from bs4 import BeautifulSoup as bs
from plotly.offline import download_plotlyjs, plot
from plotly.graph_objs import Pie, Figure, Bar, Layout


region_dict={'1':'Shadyside','2':'Squirrel Hill',"3":"Oakland", "4":"Downtown" ,"5":"No Preference"}
class KPS():
	def __init__(self):
		self.safety_matrix = np.ndarray(())
		self.user = {"1":"Student", "2":"Working Professional"}
		self.location = {"1":"Shadyside", "2":"Squirrel Hill", "3":"Oakland", "4":"Downtown" ,"5":"No Preference"}
		self.job = None
		self.preference = None
		self.price=None


	def create_array(self):
		return 


	def main(self):
		# self.show_security_index_rank()
		# return
		u_type = input("Hi! Welcome to Keep Pitt Safe!\n\nEnter\n1 - Student\n2 - Working Professional\n")
		self.job = u_type
		print("You entered: " + self.user[u_type] + "\n\n")
		child_type = input("Do you have kid? (Y/N)")
		self.child=child_type
		quit = False
		max_pay=input('Enter the max payment you can afford every month($):\n')
		self.price=pd.to_numeric(max_pay)
		max_pay=pd.to_numeric(max_pay)
		while True:
			l_type = input("Do you have a preference?\n1 - Shadyside\n2 - Squirrel Hill\n3 - Oakland\n4 - Downtown\n5 - No Preference\n")
			self.preference = l_type
			print("You entered: " + self.location[l_type] + "\n\n")
			while True:
				print('1.Show region crime trend')
				print('2.Show recommendations for you')
				print('3.Show the region security report')
				print('4.Quit')
				x =input()
				print(self.choose(x))

			# cdm = CDM()
			# count = cdm.get_crime_count(self.location[l_type])
			# print("Crime count in " + self.location[l_type] + "\n")
			# for k, v in count.items():
			# 	print("%s : %s" %(k, v))
			
			prompt = input("\n\nEnter\n1 - Go back\n0 - Exit\n\n")
			if prompt == "0":
				return
			

	def show_security_report(self):
		if self.preference == "5":
			print('Which region do you want to look into?')
			print('1. Shadyside')
			print('2. Squirrel Hill')
			print('3. Oakland')
			print('4. Downtown')
			region_input=str(input())
			self.preference = region_input
		cdm = CDM()
		count = cdm.get_crime_count(self.location[str(self.preference)])
		print("Crime count in " + self.location[str(self.preference)] + "\n")
		keys = []
		values = []
		for k, v in count.items():
			print("%s : %s" %(k, v))
			keys.append(k)
			values.append(v)
		filename = "%s_security_report.html" %(self.location[str(self.preference)])
		self.plot_graph(keys, values, filename, "Shadyside - Security Report")


# how to align these/ print in one line
# if enter invalid value, add reenter function
	def show_recommend_house(self):
		#list_number=input("Please enter the number of recommended houses you want:")
		list_number=10#pd.to_numeric(list_number)
		if self.preference == "5":
			print('which region do you want to look into?')
			print('1. Shadyside')
			print('2. Squirrel Hill')
			print('3. Oakland')
			print('4. Downtown')
			region_input=str(input())
			self.preference = region_input
		cdm = CDM()
		apt_list = cdm.get_apt_list(self.preference,self.price)
		print("Our recommendations for you in " + self.location[str(self.preference)] + "\n")
		print("*****"*10)
		#for i in apt_list.items():
		if len(apt_list)==0:
			print('Sorry, there are no recommendedations for this region')
		else:
			print(apt_list)
		print("*****"*10)
		

	def show_security_index_rank(self):
		print('1 - Squirrel Hill\n2 - Shadyside\n3 - Oakland\n4 - Downtown\n')
		cdm = CDM()
		loc = []
		x = []
		y = []
		for k,v in self.location.items():
			if k=="5":
				continue
			count = cdm.get_crime_count(v)
			loc.append(v)
			keys = []
			vals = []
			for k1, v1 in count.items():
				keys.append(k1)
				vals.append(v1)
				#print("%s : %s" %(k1, v1))
			x.append(keys)
			y.append(vals)
		self.plot_bar_chart(x, y, loc)


	def plot_bar_chart(self, x, y, location):
		data = []
		for i in range(len(x)):
			trace = Bar(x=x[i], y=y[i], name=location[i])
			data.append(trace)

		layout = Layout(
		    barmode='stack'
		)
		print(data)
		fig = Figure(data=data, layout=layout)
		plot(fig, filename='stacked-bar.html')



	def choose(self,x):
		chooser={
		    '3':self.show_security_report,
			'2':self.show_recommend_house,
			'4':self.quit,
		    '1':self.show_security_index_rank
		}
		fun=chooser.get(x,lambda:'Invalid input')
		fun()


	def plot_graph(self, labels, values, filename, title):
		trace = Pie(labels=labels, values=values)
		plot([trace], filename=filename)


	def quit(self):
		sys.exit(0)
		quit=True
		return


if __name__=='__main__':
	kps = KPS()
	kps.main()
