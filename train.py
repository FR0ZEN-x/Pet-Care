import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("cat_health_dataset.csv")

# Load saved preprocessor and encoders
preprocessor = joblib.load("models/preprocessor.pkl")
symptoms_encoder = joblib.load("models/symptoms_encoder.pkl")
prev_issues_encoder = joblib.load("models/prev_issues_encoder.pkl")

# Separate features (X) and targets (y)
X = df.drop(columns=["Health Risk (%)", "Health Risk Level", "Diagnosis", "Potential Causes", "Recommended Diet", "Consult Vet"])
y_risk_percent = df["Health Risk (%)"]
y_risk_level = df["Health Risk Level"]
y_diagnosis = df["Diagnosis"]
y_causes = symptoms_encoder.transform(df["Potential Causes"].apply(lambda x: x.split(", ") if isinstance(x, str) else []))
y_diet = df["Recommended Diet"]
y_vet = df["Consult Vet"].map({"Yes": 1, "No": 0})  # Convert "Yes"/"No" to 1/0

# Split dataset into training and test sets
X_train, X_test, y_risk_percent_train, y_risk_percent_test, y_risk_level_train, y_risk_level_test, \
y_diagnosis_train, y_diagnosis_test, y_causes_train, y_causes_test, \
y_diet_train, y_diet_test, y_vet_train, y_vet_test = train_test_split(
    X, y_risk_percent, y_risk_level, y_diagnosis, y_causes, y_diet, y_vet, 
    test_size=0.2, random_state=42
)

# Preprocess input features
X_train_processed = preprocessor.transform(X_train)
X_test_processed = preprocessor.transform(X_test)

# Train and save models
risk_percent_model = RandomForestRegressor(n_estimators=100, random_state=42)
risk_percent_model.fit(X_train_processed, y_risk_percent_train)
joblib.dump(risk_percent_model, "models/risk_model.pkl")

risk_level_model = RandomForestClassifier(n_estimators=100, random_state=42)
risk_level_model.fit(X_train_processed, y_risk_level_train.ravel())
joblib.dump(risk_level_model, "models/risk_level_model.pkl")

diagnosis_model = RandomForestClassifier(n_estimators=100, random_state=42)
diagnosis_model.fit(X_train_processed, y_diagnosis_train)
joblib.dump(diagnosis_model, "models/diagnosis_model.pkl")

causes_model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
causes_model.fit(X_train_processed, y_causes_train)
joblib.dump(causes_model, "models/causes_model.pkl")

diet_model = RandomForestClassifier(n_estimators=100, random_state=42)
diet_model.fit(X_train_processed, y_diet_train)
joblib.dump(diet_model, "models/diet_model.pkl")

vet_model = RandomForestClassifier(n_estimators=100, random_state=42)
vet_model.fit(X_train_processed, y_vet_train)
joblib.dump(vet_model, "models/vet_model.pkl")

print("✅ All models trained and saved successfully!")
