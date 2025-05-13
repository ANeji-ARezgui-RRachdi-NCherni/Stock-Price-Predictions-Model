from abc import ABC, abstractmethod
import numpy as np
from enums import ValidationMetricEnum
from datetime import datetime

class IModel(ABC):
    """
    Abstract base class for a prediction model.
    This class defines the interface that all prediction models must implement.
    """
    @abstractmethod
    def __init__(self, stock_name: str = None):
        self.__last_trained_date = None
        self.__stock_name = stock_name

    @abstractmethod
    def train(self, features: np.ndarray, targets: np.ndarray, last_trained_date: datetime):
        """
        Train the model using the provided data.

        Parameters:
            features: The training features.
            targets: the training targets.
        """
        pass

    @abstractmethod
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """
        Make predictions using the trained model.

        Parameters:
            input_data: The input data for making predictions.

        Returns:
            The predicted output.
        """
        pass

    def evaluate(self, x_test: np.ndarray, y_test: np.ndarray, metric: ValidationMetricEnum, scale: float) -> float:
        """
        Evaluate the trained model.

        Parameters:
            x_test: the rows we are trying to predict.
            y_test: the values we want to predict.
            metric: evaluation metric
            scale: the scale used to normalize the training and test data before training phase

        Returns:
            The evaluation result.
        """
        y_predict = self.predict(x_test)
        print(f"test y dim before flattening:{y_test.shape}")
        print(f"predict y dim before flattening:{y_predict.shape}")
        if (y_predict.ndim > 1):
            y_predict = y_predict.flatten()
        if (y_test.ndim > 1):
            y_test = y_test.flatten()
        y_test = y_test
        y_predict = y_predict * scale
        y_test = y_test * scale
        print(f"test y dim after flattening:{y_test.shape}")
        print(f"predict y dim after flattening:{y_predict.shape}")
        match metric:
            case ValidationMetricEnum.RMSE:
                rmse = np.sqrt(np.mean((y_predict - y_test)**2))
                return rmse
            case ValidationMetricEnum.MAPE:
                mape = np.mean(abs(y_test - y_predict)/y_test)*100
                return mape
            case _:
                raise NotImplementedError("This metric isn't implemented yet, if you want to use it please add its implementation")
    
    def get_last_trained_date(self) -> datetime:
        return self.__last_trained_date

    def get_stock_name(self) -> str:
        return self.__stock_name
