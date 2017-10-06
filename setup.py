from distutils.core import setup
from compile_spectra import compile_spectra

DATA_DIR = 'cycsat/data/'
DATASET = DATA_DIR + 'ASCIIdata_splib07a/'


def main():
    # compiles the USGS Spectral Library into the data folder
    compile_spectra(DATA_DIR, DATASET)

    setup(
        name='cycsat',
        version='0.1.0',
        author='Owen Selles',
        author_email='oselles@wisc.edu',
        packages=['cycsat'],
        license='LICENSE.rst',
        description='A synthetic satellite image generator inteneded for cyclus',
        long_description=open('README.md').read(),
        install_requires=[
            "pandas",
            "geopandas",
            "numpy",
            "skimage",
            "scipy",
            "shapely",
            "matplotlib",
            "rasterio",
            "skimage",
            "imageio",
        ],
    )

if __name__ == "__main__":
    main()
