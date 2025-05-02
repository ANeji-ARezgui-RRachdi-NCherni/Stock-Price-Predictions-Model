from statsmodels.tsa.arima.model import ARIMA

from .IModel import IModel

class ARIMAModel(IModel):
    def __init__(self):
        pass
    
    def train(self, features, targets):
        # for ARIMA model there isn't a seperation between features and targets so we pass all the data in the features param
        features = features.flatten()
        print(f"features shape: {features.shape}")
        model = ARIMA(features, order=(2,1,5)) # the order was found when running auto_arima method which generated the best orders
        model_fit = model.fit()
        self.model = model_fit
    
    def predict(self, input_data):
        numberOfDays = len(input_data)
        print(f"number of days to predict: {numberOfDays}")
        res = self.model.forecast(steps=numberOfDays)
        print(f"prediction result shape: {res.shape}")
        return res

