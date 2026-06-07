import zipfile
import joblib  # or import pickle, depending on how you saved the model
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


extraction_path = 'D:/Turing/python_begineer/Projects/Metalytics/trained_models/XAG'

# Load the model from the extracted files
model_path = f"{extraction_path}/_obj"  # Adjust path if necessary

# Load the model
model = joblib.load(model_path)  # or use pickle.load() if applicable
print("Model loaded successfully!")
print("Model parameters:", model)

# Step 2: Prepare Test Data
# Create a test DataFrame for the next 5 time steps
future_times = pd.date_range(start=datetime.now(), periods=5, freq='h')
test_data = pd.DataFrame(index=future_times)

# If your model needs historical data for context, include that as well
# Assuming your model has a method or attribute to retrieve historical data
# Replace 'model.history' with the actual historical data if available
historical_data = pd.DataFrame({
    'timestamp': pd.date_range(start=datetime.now() - timedelta(hours=12), periods=12, freq='h'),
    'price': [1.0 + i * 0.01 for i in range(12)]  # Sample historical prices
})
historical_data.set_index('timestamp', inplace=True)

# Combine historical data with future time index for prediction
test_data = pd.concat([historical_data, test_data])

# Step 3: Make Predictions
# Example: Make predictions for the next 5 time steps
predictions = model.predict(fh=[1, 2, 3, 4, 5])  # Forecasting horizon
print("Predictions for the next 5 time steps:")
print(predictions)

# Step 4: Visualize Predictions
# Plot historical data and predictions
plt.figure(figsize=(10, 6))
plt.plot(historical_data.index, historical_data.values, label='Historical Data', color='blue')
plt.plot(future_times, predictions, label='Predictions', color='red', marker='o')
plt.title('Predictions vs Historical Data')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
