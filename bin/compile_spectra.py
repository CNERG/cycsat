"""
A script for building the materials database from the
USGS Spectral Library (https://www.sciencebase.gov/catalog/item/586e8c88e4b0f5ce109fccae)
"""
import wget
import zipfile
import os

# print('Downloading the USGS Spectral Library Verson 7')
# print('More about it here:
# https://www.sciencebase.gov/catalog/item/5807a2a2e4b0841e59e3a18d')

# url = 'http://www.sciencebase.gov/catalog/file/get/586e8c88e4b0f5ce109fccae/?f=__disk__a7%2F4f%2F91%2Fa74f913e0b7d1b8123ad059e52506a02b75a2832'
# filename = '../cycsat/data/spectra.zip'
# filename = wget.download(url, filename)

# print('Unpacking...')
# zip_ref = zipfile.ZipFile(filename, 'r')
# zip_ref.extractall('../cycsat/data/')
# zip_ref.close()

# wavelengths
# ASD = pd.read_table('splib07a_Wavelengths_ASD_0.35-2.5_microns_2151_ch.txt')
# AVIRIS = pd.read_table('splib07a_Wavelengths_AVIRIS_1996_0.37-2.5_microns.txt')
# BECK = pd.read_table('splib07a_Wavelengths_BECK_Beckman_0.2-3.0_microns.txt')
# NIC41 = pd.read_table('splib07a_Wavelengths_NIC4_Nicolet_1.12-216microns.txt')
# NIC48 = pd.read_table('splib07a_Wavenumber_NIC4_Nicolet_8,900_-_46_cm^-1.txt')

chaps = ['ChapterA_ArtificialMaterials',
         'ChapterC_Coatings',
         'ChapterL_Liquids',
         'ChapterM_Minerals',
         'ChapterO_OrganicCompounds',
         'ChapterS_SoilsAndMixtures',
         'ChapterV_Vegetation']

data = []
for chap in chaps:
    fs = os.listdir('../cycsat/data/ASCIIdata_splib07a/' + chap)
    for f in fs:
        data.append(f.split('_'))

# def detect_scale(filename):
#     if 'ASDFR' in filename:
#         return ASD
#     elif 'AVIRIS' in filename:
#         return AVIRIS
#     elif 'BECK' in filename:
#         return BECK
#     elif 'NIC'
# def learn(filename):


# if __name__ == "__main__":
#     learn('splib07a_Alizarin_crimson_(dk)_GDS780_ASDFRa_AREF.txt')
