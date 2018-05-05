import pandas as pd
import requests
import json
import urllib.parse
import numpy as np
import os
import sys
import re
from bs4 import BeautifulSoup as bs
import csv


def get_historical_data():
    ''' Reads historical data which was received from data.gov and does following operations
    drop some columns
    extract zip codes
    sort on the basis of zipcode
    '''
    data = pd.read_csv("historical_data.csv", low_memory=False)
    data=data.drop(['PK', 'CCR','AGE','GENDER','RACE','ARRESTLOCATION','INCIDENTZONE','INCIDENTTRACT','COUNCIL_DISTRICT','PUBLIC_WORKS_DIVISION','INCIDENTNEIGHBORHOOD'], axis=1)
    data = data.rename(columns={'_id': 'original_id', 'ARRESTTIME': 'date','OFFENSES':'type','INCIDENTLOCATION':'address','X':'lat','Y':'long'})
    data['zipcode']=data['address']
    data['zipcode'] = data['zipcode'].astype(str).str[-5:]
    data.loc[data['type'].str.contains('Assault'), 'type'] = 'Assult'
    data.loc[data['type'].str.contains('Theft'), 'type'] = 'Theft'
    data.loc[data['type'].str.contains('Assult|Theft')==False,'type']='Other'
    data['address'] = data['address'].astype(str).str[:-21]
    data.sort_values(by=['zipcode'])
    data=data[data['zipcode'].apply(lambda x : x.isalnum())]
    zipcode_list=data.zipcode.unique()
    return data


def get_apt_list():
    ''' Uses beautiful soup to scrape listings on apartments.com
    '''
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



def json_to_csv():
    ''' 
    Takes the spotcrime.json file and converts into a csv file
    '''
    with open('spotcrime.json', encoding='utf-8') as data_file:
        crime_parsed = json.loads(data_file.read())
    print(crime_parsed)

    print(crime_parsed)
    data_file.close()

    crimes = crime_parsed['crimes']
    print(crimes)

    crime_csv = open('spotcrime.csv', 'w')
    csvwriter = csv.writer(crime_csv)

    count = 0
    for crime in crimes:
        if count == 0:
            header = crime.keys()
            csvwriter.writerow(header)
            count = count + 1
        csvwriter.writerow(crime.values())
    crime_csv.close()


def clean_spotcrime_data():
    ''' Cleans the spotcrime data by dropping and renaming columns
    '''
    data = pd.read_csv("spotcrime.csv", low_memory=False)
    data = data.drop(['link'], axis=1)
    data = data.rename(columns={'cdid': 'original_id'})
    data['zipcode']="NA"
    return data


def merge_csv_files():
    '''Merges the different data csv files into one file'''
    f1 = open('spotcrime.csv', 'w')
    f2 = open('historical_data.csv', 'w')
    files = [f1, f2]
    merged = []
    for f in files:
        filename, ext = os.path.splitext(f)
        if ext == '.csv':
            read = pd.read_csv(f)
            merged.append(read)

    result = pd.concat(merged)

    result.to_csv('merged.csv')
