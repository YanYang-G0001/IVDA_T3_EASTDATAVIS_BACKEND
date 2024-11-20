from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Resource, Api
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from .model import PatientsCat, PatientInput
from src.llm.groq_llm import GroqClient
import os
import json

# Configure Flask & Flask-PyMongo:
app = Flask(__name__)
# allow access from any frontend
cors = CORS()
cors.init_app(app, resources={r"*": {"origins": "*"}})
# add your mongodb URI
app.config["MONGO_URI"] = "mongodb://localhost:27017/patientsdatabase"
pymongo = PyMongo(app)
# Get a reference to the patient collection.
patients_cat: Collection = pymongo.db.ESDRP
patients_merged: Collection = pymongo.db.MERGED
api = Api(app)
class PatientsCatList(Resource):
    def get(self, args=None):
        # retrieve the arguments and convert to a dict
        args = request.args.to_dict()
        print(args)
        # If the user specified category is "All" we retrieve all companies
        #if args['category'] == 'All':
        cursor = patients_cat.find()
        # In any other case, we only return the companies where the category applies
        #else:
        #    cursor = patients_cat.find(args)
        # we return all companies as json
        return [PatientsCat(**doc).to_json() for doc in cursor]
def fake_predict(patient: PatientInput) -> str:
    """
    temp fake model
    """
    if patient.polyuria.lower() == "yes" or patient.polydipsia.lower() == "yes":
        return "Positive"
    return "Negative"

class PredictDisease(Resource):
    def post(self):
        try:
            data = request.get_json()
            patient = PatientInput(**data)
            prediction = fake_predict(patient)
            return jsonify({
                "id": patient.id,
                "name": patient.name,
                "prediction": prediction
            })
        except Exception as e:
            return {"error": f"Invalid input: {str(e)}"}, 400



api.add_resource(PatientsCatList, '/patientscat')
api.add_resource(PredictDisease, '/predict')
#api.add_resource(PoemByCompanyId, '/llm/groq/poem/<int:companyId>')
#api.add_resource(EvaluationByCompanyId, '/llm/groq/evaluation/<int:companyId>')