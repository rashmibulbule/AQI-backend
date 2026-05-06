import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Load dataset
df = pd.read_csv("city.csv")

# Clean data
df = df.dropna()

# Features & target
X = df[['pollutant_min', 'pollutant_max']]
y = df['pollutant_avg']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model trained and saved as model.pkl")