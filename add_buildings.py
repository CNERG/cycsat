"""
A script for downloading building footprints and other useful shapefiles.
"""
import wget
import zipfile
import os
import shutil
import argparse

DATA_DIR = 'cycsat/data/'
DATASET = DATA_DIR + 'shapefiles/'

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)


def clear_building_data(DATA_DIR):
    """Clears spectral data from the data directory."""
    for path in os.listdir(DATA_DIR):
        if path == 'buildings':
            shutil.rmtree(DATA_DIR + path)


def get_dataset(DATA_DIR, dataset_url):
    print('Downloading {} dataset'.format(dataset_url))

    url = 'http://download.geofabrik.de/{}-latest-free.shp.zip'.format(
        dataset_url)
    filename = 'cycsat/data/buildings_temp.zip'
    filename = wget.download(url, filename)
    print('')
    print('Unpacking...')
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall('cycsat/data/buildings')
    zip_ref.close()

    os.remove(DATA_DIR + 'buildings_temp.zip')


def main(args):
    get_dataset(DATA_DIR, args.ds)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--ds')
    args = parser.parse_args()
    main(args)
