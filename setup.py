from distutils.core import setup
import subprocess

# install the spectral library
subprocess.run("python bin\compile_spectra.py")

setup(
    name='cycsat',
    version='0.1.0',
    author='Owen Selles',
    author_email='oselles@wisc.edu',
    packages=['cycsat'],
    # scripts=[],
    # url='',
    license='LICENSE.rst',
    description='A synthetic satellite image generator.',
    long_description=open('README.md').read(),
    install_requires=[
        "pandas",
        "geopandas",
        "numpy",
        "skimage",
        "scipy",
        "shapely",
        "matplotlib"
    ],
)
