"""
A script for downloading building footprints and other useful shapefiles.
"""
import wget
import zipfile
import os
import shutil
import argparse

DATA_DIR = 'cycsat/data/'
TEMP_DIR = 'cycsat/data/footprints_temp/'
SHAPE_DIR = DATA_DIR + 'footprints/'

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

if not os.path.isdir(SHAPE_DIR):
    os.mkdir(SHAPE_DIR)


def reset_dir(DIR):
    if os.path.isdir(DIR):
        shutil.rmtree(DIR)
        os.mkdir(DIR)


def get_dataset(dataset_url):

    print('Downloading {} footprint shapefiles'.format(dataset_url))
    reset_dir(TEMP_DIR)

    url = 'http://download.geofabrik.de/{}-latest-free.shp.zip'.format(
        dataset_url)

    filename = DATA_DIR + 'footprints_temp.zip'
    filename = wget.download(url, filename)

    print('')
    print('Unpacking...')
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(TEMP_DIR)
    zip_ref.close()
    os.remove(filename)

    for f in os.listdir(TEMP_DIR):
        if 'gis.osm_buildings_a_free_1' in f:
            filename, ext = os.path.splitext(f)
            shutil.copyfile(TEMP_DIR + f, SHAPE_DIR +
                            dataset_url.replace('/', '-') + ext)
    shutil.rmtree(TEMP_DIR)


def main(args):
    if args.wipe:
        reset_dir(SHAPE_DIR)

    get_dataset(args.ds)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--ds')
    parser.add_argument('--wipe', default=False)
    args = parser.parse_args()
    main(args)
