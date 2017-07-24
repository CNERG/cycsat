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
import argparse

from sklearn import svm
from sklearn.neighbors import KNeighborsRegressor

parser = argparse.ArgumentParser()
parser.add_argument('--file', default=False)
args = parser.parse_args()

DATA_DIR = '../cycsat/data/'
DATASET = DATA_DIR + 'ASCIIdata_splib07a/'

# clear the data directory
print('Clearing data')
contents = os.listdir(DATA_DIR)
for path in contents:
    if path == 'info.md':
        continue

    if os.path.isdir(DATA_DIR + path):
        shutil.rmtree(DATA_DIR + path)
    else:
        os.remove(DATA_DIR + path)

if args.file:
    print('Loading USGS Spectral Library from file')
    filename = DATA_DIR + 'spectra.zip'
    shutil.copyfile(args.file, filename)
else:
    print('Downloading the USGS Spectral Library Verson 7')
    url = 'http://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae/?f=__disk__a7%2F4f%2F91%2Fa74f913e0b7d1b8123ad059e52506a02b75a2832'
    filename = '../cycsat/data/spectra.zip'
    filename = wget.download(url, filename)

print('Unpacking...')
zip_ref = zipfile.ZipFile(filename, 'r')
zip_ref.extractall('../cycsat/data/')
zip_ref.close()

# wavelengths
ASD = pd.read_table(
    DATASET + 'splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt',
    skiprows=1, header=None)

AVIRIS = pd.read_table(
    DATASET + 'splib07a_Wavelengths_AVIRIS_1996_0.37-2.5_microns.txt',
    skiprows=1, header=None)

BECK = pd.read_table(
    DATASET + 'splib07a_Wavelengths_BECK_Beckman_0.2-3.0_microns.txt',
    skiprows=1, header=None)

NIC41 = pd.read_table(
    DATASET + 'splib07a_Wavelengths_NIC4_Nicolet_1.12-216microns.txt',
    skiprows=1, header=None)

# the chapters of the spectra library
chapters = ['ChapterA_ArtificialMaterials',
            'ChapterC_Coatings',
            'ChapterL_Liquids',
            'ChapterM_Minerals',
            'ChapterO_OrganicCompounds',
            'ChapterS_SoilsAndMixtures',
            'ChapterV_Vegetation']


def detect_scale(filename):
    if 'ASD' in filename:
        return ASD
    elif 'AVIRIS' in filename:
        return AVIRIS
    elif 'BECK' in filename:
        return BECK
    elif 'NIC':
        return NIC41

print('Reading data files')
sensors = {}
for chap in chapters:
    fs = os.listdir(DATASET + chap)
    for f in fs:
        scale = detect_scale(f)
        data = pd.read_table(DATASET + chap + '//' +
                             f, skiprows=1, header=None)
        sensors[f.replace('splib07a_', '')] = scale.assign(data=data)

os.mkdir('../cycsat/data/spectra')
print('Fitting models')
for material in sensors:
    df = sensors[material]

    X = df[0].values.reshape(-1, 1)
    y = df['data']

    model = KNeighborsRegressor()
    model.fit(X, y)

    pickle.dump(model, open('../cycsat/data/spectra/' + material, 'wb'))

if __name__ == "__main__":
    pass
