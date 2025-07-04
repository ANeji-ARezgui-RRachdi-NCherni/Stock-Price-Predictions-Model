from .IModel import IModel
from keras.src.models import Sequential
from keras.src.layers import GRU, Dense, Dropout
class GRUModel(IModel):
    def __init__(self, stock_name: str = None):
        super().__init__(stock_name)
        model = Sequential()
        model.add(GRU(50))
        model.add(Dropout(0.2))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model

    def train(self, features, targets, last_trained_date):
        print(f"features shape: {features.shape}")
        print(f"targets shape: {targets.shape}")
        self.model.fit(x=features, y=targets, batch_size=32, epochs=40, verbose=1)
        self.last_trained_date = max(last_trained_date, self.last_trained_date) if self.last_trained_date != None else last_trained_date
    
    def predict(self, input_data):
        print(f"input shape: {input_data.shape}")
        res = self.model.predict(input_data)
        print(f"prediction result shape: {res.shape}")
        return res.squeeze()

