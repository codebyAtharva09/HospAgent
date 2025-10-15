import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load data
data = pd.read_csv('data/hospital_data.csv')
data['date'] = pd.to_datetime(data['date'])

# Features and target
X = data[['AQI', 'festival_flag', 'epidemic_flag']]
y = data['patient_count']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
joblib.dump(model, 'model.pkl')
print('Model trained and saved as model.pkl')
