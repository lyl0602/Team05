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
	''' This is the main class to run the application'''
	def __init__(self):
		self.safety_matrix = np.ndarray(())
		self.user = {"1":"Student", "2":"Working Professional"}
		self.location = {"1":"Shadyside", "2":"Squirrel Hill", "3":"Oakland", "4":"Downtown" ,"5":"No Preference"}
		self.job = None
		self.preference = None
		self.price=None
		self.age=None
		self.child_type=None

		
	def main(self):
		''' Main function to run the commandline application'''
		u_type = input("Hi! Welcome to Keep Pitt Safe!\n\nEnter\n1 - Student\n2 - Working Professional\n")
		if u_type=='1' or u_type=='2':
			self.job = u_type
		else:
			u_type = input("Please enter valid number:\n1 - Student\n2 - Working Professional\n")
			self.job=u_type
		print("You entered: " + self.user[u_type] + "\n\n")
		self.child_type = input("Do you have kid? Please input Y or N: ")
		
		if self.child_type.lower()!='y' and self.child_type.lower()!='n' :
			self.child_type = input("Please input Y or N: ")
		self.child=self.child_type.lower()
		if self.child_type.lower()=='y':
			age=input('Please input your kids age: ')
			if age.isdigit()==True:
				self.age=age
			else:
				age=input('Please input a valid age: ')
				self.age=age
		quit = False
		max_pay=input('Enter the max payment you can afford every month($):\n')
		if max_pay.isdigit()!=True:
			max_pay=input('Please enter a valid number:\n')
		elif int(max_pay)<0:
			max_pay=input('Please enter a valid number larger than 0:\n')
		self.price=pd.to_numeric(max_pay)
		max_pay=pd.to_numeric(max_pay)
		while True:
			l_type = input("Do you have a preference?\n1 - Shadyside\n2 - Squirrel Hill\n3 - Oakland\n4 - Downtown\n5 - No Preference\n")
			self.preference = l_type
			print("You entered: " + self.location[l_type] + "\n\n")
			while True:
				print('1.Show region crime trend')
				print('2.Show recommendationded houses for you')
				print('3.Show the region security report')
				print('4.Show recommendationded schools for your child')
				print('5.Quit')
				x =input()
				print(self.choose(x))
			
			prompt = input("\n\nEnter\n1 - Go back\n0 - Exit\n\n")
			if prompt == "0":
				return
			
	def show_school_list(self):
		''' Depening on user's preference on region, this function prints list of schools'''
		if self.preference == "5":
			print('which region do you want to look into?')
			print('1. Shadyside')
			print('2. Squirrel Hill')
			print('3. Oakland')
			print('4. Downtown')
			region_input=str(input())
			self.preference = region_input

		if self.child_type=='y':
			cdm = CDM()
			school_list = cdm.get_school_list(self.preference,self.age)
			print("Our school recommendations for you in " + self.location[str(self.preference)] + "\n")
			print("*****"*20)
			# for i in school_list.items():
			if len(school_list)==0:
				print('Sorry, there are no recommendeded school for your child in this region')
			else:
				print(school_list)
			print("*****"*20)

			
	def show_security_report(self):
		''' Takes user's region preference and returns a table of crimes
		It also plots a graph showing the distribution of crimes'''
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


	def show_recommend_house(self):
		'''Takes user's region preference and prints a table of recommended houses'''
		list_number=10
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
		print("*****"*20)
		#for i in apt_list.items():
		if len(apt_list)==0:
			print('Sorry, there are no recommendedation for this region')
		else:
			print(apt_list)
		print("*****"*20)
		

	def show_security_index_rank(self):
		''' Generates the distribution of crimes for all regions and types'''
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
		''' Takes data of crimes and location and plots a stacked bar chart'''
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
		''' Maps user's choice with different functions '''
		chooser={
		    '3':self.show_security_report,
			'2':self.show_recommend_house,
			'4':self.show_school_list,
			'5':self.quit,
		    '1':self.show_security_index_rank
		}
		fun=chooser.get(x,lambda:'Invalid input')
		fun()


	def plot_graph(self, labels, values, filename, title):
		''' Plots a Pie chart '''
		trace = Pie(labels=labels, values=values)
		plot([trace], filename=filename)


	def quit(self):
		''' Quits the application'''
		sys.exit(0)
		quit=True
		return


if __name__=='__main__':
	kps = KPS()
	kps.main()
