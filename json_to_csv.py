import json
import csv

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