from abc import ABC, abstractmethod
import numpy as np

class IModel(ABC):
    """
    Abstract base class for a prediction model.
    This class defines the interface that all prediction models must implement.
    """

    @abstractmethod
    def train(self, features: np.ndarray, targets: np.ndarray):
        """
        Train the model using the provided data.

        Parameters:
            data: The training data.
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

    @abstractmethod
    def evaluate(self, x_test: np.ndarray, y_test: np.ndarray, metric: str) -> float:
        """
        Evaluate the trained model.

        Parameters:
            x_test: the rows we are trying to predict.
            y_test: the values we want to predcit.
            metric: evaluation metric

        Returns:
            The evaluation result.
        """
        pass