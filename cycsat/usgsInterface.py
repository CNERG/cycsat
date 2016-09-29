########################################################
# tools for querying USGS EE for imagery
########################################################

import subprocess

import shapefile
from usgs import api

import config
print config.usgs_username,config.usgs_password
# login to usgs servers
subprocess.call(['usgs','login',config.usgs_username,config.usgs_password],shell=True)

in_file = 'C:/Users/Owen/Documents/Academic/CNERG/data/nuclear-facilities-update/nuclear-facilities-update.shp'
plants = shapefile.Reader(in_file)

lat = plants.records()[2][-2]
lng = plants.records()[2][-1]

fields = api.dataset_fields('ORBVIEW3', 'EE')
print fields

where = {
	9947: 0,	 # cloud cover less than 10%
	}

# scenes = api.search('LANDSAT_8', 'EE', start_date='2001-04-01', end_date='2015-05-01', where=where,
# 					 lat=lat, lng=lng, extended=True)

	# for i in scenes:
	# 	print i['acquisitionDate']

# logout of usgs servers
subprocess.check_output(['usgs','logout'],shell=True)


# acquisitionDate
# browseUrl
# displayId
# Scene Cloud Cover