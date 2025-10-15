import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.data_agent import DataAgent

def train_surge_model():
    """Train and save the surge prediction model."""
    data_agent = DataAgent()
    result = data_agent.load_data('data/hospital_data.csv')
    if result['status'] == 'error':
        print(f"Error loading data: {result['message']}")
        return

    features = data_agent.prepare_features()
    if features is None:
        print("Error preparing features")
        return

    X, y = features

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, 'surge_model.pkl')
    print("Model trained and saved to models/surge_model.pkl")

if __name__ == "__main__":
    train_surge_model()
