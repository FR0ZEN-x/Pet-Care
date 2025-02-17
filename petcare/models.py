from petcare import mongo, bcrypt, login_manager
from flask_login import UserMixin
from bson.objectid import ObjectId

class PredictionResult:
    def __init__(self, prediction_data):
        self.health_risk_percentage = prediction_data.get("health_risk_percentage", 0)
        self.health_risk_level = prediction_data.get("health_risk_level", "Unknown")
        self.diagnosis = prediction_data.get("diagnosis", [])
        self.diet = prediction_data.get("diet", [])
        self.evn_exposure = prediction_data.get("evn_exposure", [])
        self.consult_vet = prediction_data.get("consult_vet", [])

    @staticmethod
    def from_dict(prediction_data):
        return PredictionResult(prediction_data)

class HealthReport:
    def __init__(self, report_data):
        self.date = report_data.get("date", "")
        self.heart_rate = report_data.get("heart_rate", 0)
        self.respiratory_rate = report_data.get("respiratory_rate", 0)
        self.temperature = report_data.get("temperature", 0)
        self.hydration_level = report_data.get("hydration_level", "")
        self.symptoms = report_data.get("symptoms", [])
        self.previous_health_Issues = report_data.get("previous_health_Issues", [])
        self.prediction_results = [PredictionResult.from_dict(prediction) for prediction in report_data.get("prediction_results", [])]
        self.vet_comments = report_data.get("vet_comments", "")

    @staticmethod
    def from_dict(report_data):
        return HealthReport(report_data)

class Pet:
    def __init__(self, pet_data):
        self.pet_id = str(pet_data.get("_id", None))  # Use None if _id doesn't exist
        self.name = pet_data["name"]
        self.species = pet_data["species"]
        self.gender = pet_data["gender"]
        self.owner_id = str(pet_data.get("owner_id", ""))
        self.health_reports = [HealthReport.from_dict(report) for report in pet_data.get("health_reports", [])]

    @staticmethod
    def from_dict(pet_data):
        return Pet(pet_data)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.vet_license = user_data.get("vet_license")
        self.is_vet = user_data.get("is_vet", False)
        self.pets = [Pet.from_dict(pet) for pet in user_data.get("pets", [])]

    @staticmethod
    def get(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password, attempted_password)

    def is_admin(self):
        return self.username.title() == "Shaik"

class VetLicense:
    def __init__(self, vet_data):
        self.id = str(vet_data["_id"])
        self.vet_license = vet_data.get("vet_license")

    @staticmethod
    def get(vet_license):
        return mongo.db.vetlicense.find_one({"vet_license": vet_license})

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    return User(user_data) if user_data else None
