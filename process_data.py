import pandas as pd
import requests
import json
import urllib.parse
import numpy as np
import os
import sys
import re
from bs4 import BeautifulSoup as bs




def get_historical_data():
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


def get_apt_list():
	titles=list()
    addresses=list()
    zipcodes=list()
    prices=list()
    for num in range(1,29):
        page=requests.get('https://www.apartments.com/pittsburgh-pa/%s/?bb=z1nsvpj4rIpt24vwa'%num)
        page=page.content
        soup = bs(page, 'html.parser')
        anchors=soup.find_all('a',class_='placardTitle js-placardTitle ')
        anchors2=soup.find_all('div',class_='location')
#     anchors3=soup.find_all('div').find_all('div',class_='apartmentRentRollupContainer').find_all('span',class_='altRentDisplay')
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
            prices.append(i)
#         str_list = re.split("\s+", i)     
#         for s in str_list[1:len(str_list)+1]:
#             prices.append(s)  
    apt_id=list(range(len(titles)))
    apt_list = pd.DataFrame(
        {'id':apt_id,
         'name': titles,
         'zipcode': zipcodes,
         'address': addresses,
         'price':prices
        })
    print(apt_list)
    return(apt_list)
