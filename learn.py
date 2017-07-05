from cycsat.laboratory import Library, USGSMaterial
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.neighbors import KNeighborsRegressor

from sklearn.model_selection import validation_curve

m = USGSMaterial('vermiculite_ws681.23472.asc')

feature_cols = ['std', 'relectance']

X = m.wavelength.reshape(-1, 1)
y = m.response
#X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

model = KNeighborsRegressor()
model.fit(X, y)

y_pred = model.predict(X)

fig, ax = plt.subplots(1)
ax.plot(X[:, 0], y)
ax.plot(X[:, 0], y_pred)
