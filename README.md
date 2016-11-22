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

cycsat\
	archetypes.py
	geometry.py
	image.py
	simulation.py
	prototypes\
		enrichment.py
		instrument.py
		reactor.py
		satellite.py
		shapes.py
		sink.py
		source.py

| Module           | Description                                              |
| -----------------| ---------------------------------------------------------|
| archetypes       | database classes (eg. satellite, facility)               |
| geometry         | functions for managing geometry                          |
| image            | classes and functions for writing images                 |
| simulation       | classes for running simulations and reading/writing data |
| prototypes       | defined prototypes of database classes (archetypes)      |

## Database schema
Show the schema

## Facilities, Features, and Shapes
cycsat reads the AgentEntry table of a Cyclus output database and "builds" a geometric
representation of each facility based on a prototpye and stores it in a database.

Facilities are made up of features and features are collections of shapes. For example, a 
reactor facility might have a cooling tower, which would be composed of a few circles and a plume.

## Events
Event records represent the apperance of a non-static shape at a faciltiy for a particular timestep. 
Each shape has rules stored in the CycSat_Rule table that must be met in order for the shape
to appear at a given timestep. A rule is a simple boolean SQL query that is checked in the cyclus
output database. If all the rules for a particlar shape at a particlar time step are True an event
record will be added for that shape at that timestep.

## Instruments and Materials
Materials are numpy arrays that represent reflectance for the the wavelength spectrum 
from 0.20nu to 3.0nu.

Instruments pick out a range from the material array and return the mean reflectance.

## Satellites and Missions 

## Prototyping

## Running simulations

## Sample
The following code reads cyclus output, builds a geometric representation of the world,

makes a LANDSAT8 prototype

three images are a standard blue band, green band, and red band output for a simple
reactor prototype.

```python


```

