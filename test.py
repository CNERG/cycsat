from cycsat import Interface
from cycsat import data_model

cur = Interface('test.db')

data_model.Base.metadata.create_all(cur.engine)

test_sat = data_model.Satellite(name='test')
test_sat.instruments = [data_model.Instrument(name='thermal')]

cur.session.add(test_sat)
cur.session.commit()




