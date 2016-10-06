########################################################
# tool for querying USGS EE for imagery
########################################################

import subprocess

import shapefile
from usgs import api
from usgs import soap
import pandas as pd

import config

def search_usgs(instrument):
	'''searches usgs earth explorer and returns results as dictionary and pandas df'''

	# login to usgs servers and get and api key
	login = subprocess.check_output(['usgs','login',config.usgs_username,config.usgs_password],shell=True)
	key = login.strip()

	in_file = 'C:/Users/Owen/Documents/Academic/CNERG/data/nuclear-facilities-update/nuclear-facilities-update.shp'
	plants = shapefile.Reader(in_file)

	result = {}
	rows = []
	for plant in plants.records():

		lat = plant[-2]
		lng = plant[-1]

		where = {
		9947: 0,	 # cloud cover less than 10%
		}

		scenes = api.search(instrument, 'EE', start_date='2001-04-01', end_date='2015-05-01', where=where,lat=lat, lng=lng,
							api_key=key)

		print plant[0],plant[1],lat,lng,len(scenes)
		rows.append([plant[0],plant[1],lat,lng,len(scenes)])

		if len(scenes)>0:
			result[plant[0]] = {
			'name': plant[1],
			'state':plant[5],
			'scenes':scenes,
			'count' : len(scenes)
			}

	# logout of usgs servers
	subprocess.check_output(['usgs','logout'],shell=True)

	df = pd.DataFrame(rows,columns=['id','name','lat','lng','scenes'])
	df = df[df['scenes']>0].copy()

	return {'results':result,'dataframe':df}

result = search_usgs('ORBVIEW3')

# # login to usgs servers and get and api key
# login = subprocess.check_output(['usgs','login',config.usgs_username,config.usgs_password],shell=True)
# key = login.strip()

# eid = '3V040902P0000465071A520016001782M_001648451'
# a = api.download('ORBVIEW3','EE',eid,'L1B')

# #fields = api.dataset_fields('ORBVIEW3', 'EE')
