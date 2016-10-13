from cycsat import Agency
from cycsat.data_model import Base
from cycsat.data_model import Satellite, Instrument, Mission
from cycsat.data_model import Site, Feature
from cycsat.data_model import Scene, Event


# create the interface
hq = Agency('example')

# create a satellite and instrument
new_sat = Satellite(name='land viewer')
new_sat.instruments = [Instrument(name='thermal'),
						Instrument(name='RGB')
						]

# create a new mission with one site
new_sat.missions = [Mission(name='pilot mission')]
new_sat.missions[0].sites = [Site(name='reactor')]

new_sat.missions[0].sites[0].features = [Feature(name='building')]

# create events for all features
for feat in new_sat.missions[0].sites[0].features:
	print feat.name
	feat.events = [Event(name='appear')]

# create scenes for all events
for event in 

# save the data to the database
hq.session.add(new_sat)
hq.session.commit()




