from sklearn.preprocessing import MinMaxScaler

def get_or_create_scaler(stock: str):
    # TODO: Check first if the scaler exists already in azure ML, if so bring it
    return MinMaxScaler()

def save_scaler(scaler: MinMaxScaler):
    raise NotImplementedError("This method isn't implemented!")