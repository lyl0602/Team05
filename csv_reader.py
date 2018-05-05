import csv
import json
import numpy as np
import pandas as pd
from distance import Distance as Dist 
import requests
import urllib.parse
import numpy as np
import os
import sys
import re
from bs4 import BeautifulSoup as bs

class CrimeDataModel():
	def __init__(self, filename="data.csv"):		
		crimeData = {}
		crimeData["id"] = []
		crimeData["date"] = []
		crimeData["type"] = []
		crimeData["address"] = []
		crimeData["lat"] = []
		crimeData["long"] = []

		with open(filename) as csvDataFile:
			csvReader = csv.reader(csvDataFile, delimiter=',')
			for row in csvReader:
				crimeData["id"].append(row[1])
				crimeData["date"].append(row[2])
				crimeData["type"].append(row[3])
				crimeData["address"].append(row[4])
				crimeData["lat"].append(row[5])
				crimeData["long"].append(row[6])

		self.crimeData = crimeData
		self.occurences = len(crimeData["id"])
		self.areas = {
			"Shadyside": [-79.995888, 40.440624],
			"Squirrel Hill": [-79.9277, 40.4456],
			"Downtown": [-79.995888, 40.440624],
			"Oakland": [-79.995888, 40.440624]
		}

		self.MAX_DIST = 2


	def get_crime_count(self, area_index):
		dist = Dist()
		output = []

		for i in range(self.occurences-1):
			lat1, lon1 = self.areas[area_index][0], self.areas[area_index][1]
			lat2, lon2 = self.crimeData["lat"][i+1], self.crimeData["long"][i+1]
			d = dist.calculate_dist_in_miles(lat1, lon1, lat2, lon2)
			if d <= self.MAX_DIST:
				output.append(self.crimeData["type"][i])

		# unique_elements, counts_elements = np.unique(np.array(output), return_counts=True)
		output_dict = {}
		# for i in range(unique_elements):
		# 	output_dict[unique_elements[i]] = counts_elements[i]
		
		df = pd.DataFrame(output, columns=['type'])
		unique_elements = df['type'].value_counts().keys().tolist()
		counts_elements= df['type'].value_counts().tolist()
		for i in range(len(unique_elements)):
			output_dict[unique_elements[i]] = counts_elements[i]

		return output_dict

	def get_historical_data(self):
	    data = pd.read_csv("historical_data.csv", low_memory=False)
	    data=data.drop(['PK', 'CCR','AGE','GENDER','RACE','ARRESTLOCATION','INCIDENTZONE','INCIDENTTRACT','COUNCIL_DISTRICT','PUBLIC_WORKS_DIVISION','INCIDENTNEIGHBORHOOD'], axis=1)
	    data = data.rename(columns={'_id': 'original_id', 'ARRESTTIME': 'date','OFFENSES':'type','INCIDENTLOCATION':'address','X':'lat','Y':'long'})
	    data['zipcode']=data['address']
	    data['zipcode'] = data['zipcode'].astype(str).str[-5:]
	    data.loc[data['type'].str.contains('Assault'), 'type'] = 'Assult'
	    data.loc[data['type'].str.contains('Theft'), 'type'] = 'Theft'
	    data.loc[data['type'].str.contains('Assult|Theft')==False,'type']='Other'
	    data['address'] = data['address'].astype(str).str[:-21]
	# data['zipcode']=pd.to_numeric(data['zipcode'], errors='coerce')
	    data.sort_values(by=['zipcode'])
	    data=data[data['zipcode'].apply(lambda x : x.isalnum())]
	    zipcode_list=data.zipcode.unique()
	    return data

	def get_school_list(self,x,age):
		# get the school list in region user selected
		# x is the region number
		# age is the user's child's age
		if x=='2':
		    zipcodes=['15217']
		elif x=='1':
		    zipcodes=['15232']
		elif x=='3':
		    zipcodes=['15213']
		elif x=='4':
		    zipcodes=['15222']

		hill_number=list()
		hill_address=list()
		hill_schoolname = list()
		hill_address_tele=list()
		for zipcode in zipcodes:
		    page=requests.get('https://www.publicschoolreview.com/schools-by-distance/%s/5/None/0'%zipcode)
		    page=page.content
		    soup = bs(page, 'html.parser')
		    for span in soup.find_all("span",class_="table_cell_county"):
		        b=span.get_text().strip()
		        hill_address_tele.append(b)
		    for i in hill_address_tele[1:]:
		        hill_number.append(i[-13:-1])
		    for i in hill_address_tele[1:]:
		        if len(i)>33:
		            hill_address.append(i[:-33])
		    for span in soup.find_all("span",class_="tooltip"):
		        b=span.get_text().strip()
		        hill_schoolname.append(b)
		a=list(hill_schoolname)
		b=list(hill_address)
		c=list(hill_number)

		hill_school = pd.DataFrame(
		    {'School name': a,
		     'Address': b,
		     'Tele':c
		    })
		
		if int(age)<5 or int(age)>18:
		    school_list=list()
		elif age=='5':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8|K-5")]
		elif age=='6'or age=='7'or age=='8':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8|K-5|6-12|6-8")]
		elif age=='9' or age == '10' or age == '10' or age=='11':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8|K-5|6-12")]
		elif age=='12':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8|6-12|High School")]
		elif age=='13':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8")]
		elif age=='14':
		    school_list=hill_school[hill_school['School name'].str.contains("K-8|High School")]
		elif age=='15'or age=='16' or age=='17' or age=='18':
		    school_list=hill_school[hill_school['School name'].str.contains("High School")]
		return school_list

	def get_apt_list(self,x,max_price = 0,list_number=20 ):
		#return the apartment list for certain region
		#x is the region number
		titles=list()
		addresses=list()
		zipcodes=list()
		prices=list()
		for num in range(1,29):
			#data retrive from this website
		    page=requests.get('https://www.apartments.com/pittsburgh-pa/%s/?bb=z1nsvpj4rIpt24vwa'%num)
		    page=page.content
		    soup = bs(page, 'html.parser')
		    anchors=soup.find_all('a',class_='placardTitle js-placardTitle ')
		    anchors2=soup.find_all('div',class_='location')
		    for a in anchors:
		        if a.has_attr('title'):
		            title=a.get('title')
		            titles.append(title[:-16])
		    for a in anchors2:        
		        if a.has_attr('title'):
		            address=a.get('title')
		            addresses.append(address[:-22])
		            zipcodes.append(address[-5:])
		    anchor3=soup.find_all('span',class_='altRentDisplay')
		    for i in anchor3:
		        i=i.text.strip()
		        if i.find('-')!=-1:
		            prices.append(i[1:6])
		        else:
		            prices.append(i[1:])

		apt_list = pd.DataFrame(
		    {
		     'name': titles,
		     'zipcode': zipcodes,
		     'address': addresses,
		     'price':prices
		    })
		apt_list["price"] = apt_list["price"].str.replace("-", "")
		apt_list['price'] = apt_list['price'].str.replace(',','')
		apt_list['price'] = apt_list['price'].str.replace(' ','')
		filter1 = apt_list['price'].str.contains('allforRent')
		apt_list = apt_list[~filter1]

		apt_list['price'] = pd.to_numeric(apt_list['price'])
		apt_list["address"] = np.where(apt_list["address"]=="",apt_list["name"],apt_list["address"])
		shady1=apt_list[apt_list.zipcode=='15213']
		shady2=apt_list[apt_list.zipcode=='15232']
		shady3=[shady1,shady2]
		shady_list=pd.concat(shady3)
		oak_list=apt_list[apt_list.zipcode=='15213']
		town_list=apt_list[apt_list.zipcode=='15222']
		hill1=apt_list[apt_list.zipcode=='15217']
		hill2=apt_list[apt_list.zipcode=='15232']
		hill3=[hill1,hill2]
		hill_list=pd.concat(hill3)
		if x=='1':
			shady_list_sorted=shady_list[apt_list.price<max_price]
			shady_list_sorted.iloc[np.lexsort((apt_list.price.values))]
			shady_list_sorted.loc[:, apt_list.columns != 'zipcode']
			return shady_list_sorted[0:list_number-1]
		elif x=='2':
			hill_list_sorted=hill_list[apt_list.price<max_price]
			hill_list_sorted.iloc[np.lexsort((apt_list.price.values))]
			hill_list_sorted.loc[:, apt_list.columns != 'zipcode']
			return hill_list_sorted[0:list_number-1]
		elif x=='3':
			oak_list_sorted=oak_list[apt_list.price<max_price]
			oak_list_sorted.iloc[np.lexsort((apt_list.price.values))]
			oak_list_sorted.loc[:, apt_list.columns != 'zipcode']
			return oak_list_sorted[0:list_number-1]
		elif x=='4':
			town_list_sorted=town_list[apt_list.price<max_price]
			town_list_sorted.iloc[np.lexsort((apt_list.price.values))]
			town_list_sorted.loc[:, apt_list.columns != 'zipcode']
			return town_list_sorted[0:list_number-1]
		elif x=='5' or max_price==0:
			apt_list_sorted=apt_list[apt_list.price<max_price]
			apt_list_sorted.iloc[np.lexsort((apt_list.price.values))]
			apt_list_sorted.loc[:, apt_list.columns != 'zipcode']
			return apt_list_sorted[0:list_number-1]
		else:
			print('Sorry, no this region')

