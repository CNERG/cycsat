"""
A script for building the materials database from the
USGS Spectral Library (https://www.sciencebase.gov/catalog/item/586e8c88e4b0f5ce109fccae)
"""
import wget
import zipfile
import os
import shutil
import pandas as pd
import pickle

from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor

DATA_DIR = '../cycsat/data/'
DATASET = DATA_DIR + 'ASCIIdata_splib07a/'

# clear the data directory
print('Clearing data')
# contents = os.listdir(DATA_DIR)
# for path in contents:
#     if path == 'info.md':
#         continue

#     if os.path.isdir(DATA_DIR + path):
#         shutil.rmtree(DATA_DIR + path)
#     else:
#         os.remove(DATA_DIR + path)

# print('Downloading the USGS Spectral Library Verson 7')
# print('More about it here:
# https://www.sciencebase.gov/catalog/item/5807a2a2e4b0841e59e3a18d')

# url = 'http://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae/?f=__disk__a7%2F4f%2F91%2Fa74f913e0b7d1b8123ad059e52506a02b75a2832'
filename = '../cycsat/data/spectra.zip'
# filename = wget.download(url, filename)

print('Unpacking...')
zip_ref = zipfile.ZipFile(filename, 'r')
zip_ref.extractall('../cycsat/data/')
zip_ref.close()

# wavelengths
ASD = pd.read_table(
    DATASET + 'splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt', skiprows=1, header=None)

AVIRIS = pd.read_table(
    DATASET + 'splib07a_Wavelengths_AVIRIS_1996_0.37-2.5_microns.txt', skiprows=1, header=None)

BECK = pd.read_table(
    DATASET + 'splib07a_Wavelengths_BECK_Beckman_0.2-3.0_microns.txt', skiprows=1, header=None)

NIC41 = pd.read_table(
    DATASET + 'splib07a_Wavelengths_NIC4_Nicolet_1.12-216microns.txt', skiprows=1, header=None)

# the chapters of the spectra library
chapters = ['ChapterA_ArtificialMaterials',
            'ChapterC_Coatings',
            'ChapterL_Liquids',
            'ChapterM_Minerals',
            'ChapterO_OrganicCompounds',
            'ChapterS_SoilsAndMixtures',
            'ChapterV_Vegetation']


def detect_scale(filename):
    if 'ASDFR' in filename:
        return ASD
    elif 'AVIRIS' in filename:
        return AVIRIS
    elif 'BECK' in filename:
        return BECK
    elif 'NIC':
        return NIC41

print('Reading data files')
sensors = []
for chap in chapters:
    fs = os.listdir(DATASET + chap)
    for f in fs:
        scale = detect_scale(f)
        data = pd.read_table(DATASET + chap + '//' +
                             f, skiprows=1, header=None)

        result = scale.assign(data=data)
        sensors.append(result)


print('Fitting models')


X = sensors[0][0].values.reshape(-1, 1)
y = sensors[0]['data']

print('fit model')
model = KNeighborsRegressor()
model.fit(X, y)

filename = 'finalized_model.sav'
pickle.dump(model, open(filename, 'wb'))

# if __name__ == "__main__":
#     learn('splib07a_Alizarin_crimson_(dk)_GDS780_ASDFRa_AREF.txt')
