# cycsat
A synthetic satellite time series generator that uses Cyclus for nuclear non-proliferation monitoring. 

## Dependencies

* pandas
* numpy
* shapely
* sqlalchemy
* skimage
* gdal

## Package structure

```
cycsat\
	archetypes.py
	geometry.py
	image.py
	simulation.py
	prototypes\
		feature.py
		enrichment.py
		instrument.py
		reactor.py
		satellite.py
		shapes.py
		sink.py
		source.py
```

## Facilities, Features, and Shapes
cycsat reads the AgentEntry table of a Cyclus output database and "builds" a geometric
representation of each facility based on a prototpye and stores it in a database.

## Instruments and Materials
Materials are numpy arrays that represent reflectance for the the wavelength spectrum 
from 0.20nu to 3.0nu.

