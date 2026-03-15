import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "ml_model",
    "carbon_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_carbon(features):

    features = np.array(features).reshape(1, -1)

    prediction = model.predict(features)

    return float(prediction[0])
def carbon_to_credits(carbon_tons):

    """
    1 carbon credit = 1 ton CO2
    """

    credits = carbon_tons

    return round(credits, 2)