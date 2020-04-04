import statsmodels.api as sm
from statsmodels.formula.api import ols
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_boston
import matplotlib.pyplot as plt
import pandas as pd

boston = load_boston()
bos = pd.DataFrame(boston.data)
bos.columns = boston.feature_names
bos['PRICE'] = boston.target

#LR using sklearn

X = bos.drop('PRICE', axis = 1)
lm = LinearRegression()

#lm.fit = Fit a linear model
#lm.predict = Predict Y using the linear model with estimated coefficients
#lm.score =  Returns the coefficient of determination (R^2)

lm.fit(X,bos.PRICE)
print(lm.predict(X)[0:5])
predicted = lm.predict(X)
plt.scatter(predicted, bos.PRICE)

# Evaluating the Model: Sum-of-Squares

# Using PTRATIO (Pupil-Teacher Ratio) as predictor
lm_ptratio = LinearRegression()
lm_ptratio.fit(X[['PTRATIO']], bos.PRICE)
#pd.DataFrame({'features': X.columns, 'estimatedCoefficients': lm.coef_})
# [['features', 'estimatedCoefficients']]
print(lm_ptratio.intercept_)
print(lm_ptratio.coef_)
print("r2 value:", lm_ptratio.score(X[['PTRATIO']],bos.PRICE))

m = ols('PRICE ~ PTRATIO',bos).fit()
print('F-Statistic',m.fvalue)
print('P-Val',m.pvalues)