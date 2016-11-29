'''

__init__.py

'''

# Check for dependencies. #
modules = [
'pandas',
'numpy',
'shapely',
'sqlalchemy',
'skimage',
'gdal'
]

needed_modules = list()

for module in modules:
	try:
		__import__(module)
	except:
		print(module,'required')





