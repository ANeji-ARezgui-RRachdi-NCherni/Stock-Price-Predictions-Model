from statsmodels.tsa.arima.model import ARIMA

from .IModel import IModel

class ARIMAModel(IModel):
    def __init__(self, stock_name: str = None):
        super().__init__(stock_name)
        pass
    
    def train(self, features, targets, last_trained_date):
        # for ARIMA model there isn't a separation between features and targets so we pass all the data in the features param
        features = features.flatten()
        print(f"features shape: {features.shape}")
        model = ARIMA(features, order=(2,1,5)) # the order was found when running auto_arima method which generated the best orders
        model_fit = model.fit()
        self.model = model_fit
        self.last_trained_date = max(last_trained_date, self.last_trained_date) if self.last_trained_date != None else last_trained_date
    
    def predict(self, input_data):
        numberOfDays = len(input_data)
        print(f"number of days to predict: {numberOfDays}")
        res = self.model.forecast(steps=numberOfDays)
        print(f"prediction result shape: {res.shape}")
        return res

