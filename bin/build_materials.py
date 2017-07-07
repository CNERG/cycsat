"""
A script for building the materials database from the
USGS Spectral Library (https://www.sciencebase.gov/catalog/item/586e8c88e4b0f5ce109fccae)
"""
import urllib.request

print('Downloading USGS spectral library...')
url = 'http://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae/?f=__disk__a7%2F4f%2F91%2Fa74f913e0b7d1b8123ad059e52506a02b75a2832'
filename = '/cycsat/data/materials.zip'
urllib.request.urlretrieve(url, filename)


if __name__ == "__main__":
    pass
