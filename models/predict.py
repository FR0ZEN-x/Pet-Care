import joblib
import pandas as pd
import numpy as np

# Load all trained models
preprocessor = joblib.load("models/preprocessor.pkl")
symptoms_encoder = joblib.load("models/symptoms_encoder.pkl")
prev_issues_encoder = joblib.load("models/prev_issues_encoder.pkl")

risk_model = joblib.load("models/risk_model.pkl")
risk_level_model = joblib.load("models/risk_level_model.pkl")
diagnosis_model = joblib.load("models/diagnosis_model.pkl")
causes_model = joblib.load("models/causes_model.pkl")
diet_model = joblib.load("models/diet_model.pkl")
vet_model = joblib.load("models/vet_model.pkl")

def preprocess_input(data):
    """Preprocess input data for prediction."""
    data["Symptoms"] = data["Symptoms"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])
    data["Previous Health Issues"] = data["Previous Health Issues"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])

    X_symptoms = symptoms_encoder.transform(data["Symptoms"])
    X_prev_issues = prev_issues_encoder.transform(data["Previous Health Issues"])

    data = data.drop(["Symptoms", "Previous Health Issues"], axis=1)
    data = pd.concat([data.reset_index(drop=True),
                      pd.DataFrame(X_symptoms, columns=symptoms_encoder.classes_),
                      pd.DataFrame(X_prev_issues, columns=prev_issues_encoder.classes_)], axis=1)

    return preprocessor.transform(data)

def predict_health_risk(input_data):
    """Generate predictions for a given pet health input."""
    processed_data = preprocess_input(input_data)

    risk_percent = risk_model.predict(processed_data)[0]
    risk_level = risk_level_model.predict(processed_data)[0]
    diagnosis = diagnosis_model.predict(processed_data)[0]
    causes = causes_model.predict(processed_data)[0]
    diet = diet_model.predict(processed_data)[0]
    consult_vet = "Yes" if vet_model.predict(processed_data)[0] == 1 else "No"

    return {
        "Health Risk (%)": risk_percent,
        "Health Risk Level": risk_level,
        "Diagnosis": diagnosis,
        "Potential Causes": causes.tolist(),
        "Recommended Diet": diet,
        "Consult Vet": consult_vet
    }

# Test example
if __name__ == "__main__":
    sample_input = pd.DataFrame([{
        "Age": 5,
        "Weight (kg)": 4.3,
        "Symptoms": "Lethargy, Sneezing",
        "Previous Health Issues": "Diabetes",
        "Hydration (%)": 55,
        "Heart Rate (bpm)": 190,
        "Respiratory Rate (bpm)": 30,
        "Temperature (°C)": 38.6,
        "Environmental Exposure": "Indoor"
    }])

    prediction = predict_health_risk(sample_input)
    print(prediction)
