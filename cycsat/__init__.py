"""
__init__.py
"""

# Check for the package dependencies
modules = [
    'pandas',
    'numpy',
    'shapely',
    'sqlalchemy',
    'skimage',
    'gdal'
]

for module in modules:
    try:
        __import__(module)
    except:
        print(module, 'required')
