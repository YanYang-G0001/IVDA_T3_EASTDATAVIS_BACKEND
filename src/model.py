from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
'''
class Company(BaseModel):
        id: int
        name: str
        category: str
        founding_year: int
        employees: int
        profit: List
        def to_json(self):
            return jsonable_encoder(self, exclude_none=True)
'''
class PatientsCat(BaseModel):
    _id: str
    age: int
    gender: str
    polyuria: str
    polydipsia: str
    sudden_weight_loss: str
    weakness: str
    polyphagia: str
    genital_thrush: str
    visual_blurring: str
    itching: str
    irritability: str
    delayed_healing: str
    partial_paresis: str
    muscle_stiffness: str
    alopecia: str
    obesity: str
    class_: str
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)
class PredictionResult(BaseModel):
    id: int
    name: str
    prediction: str  # "Positive" or "Negative"

class PatientInput(BaseModel):
    pregnancies: int
    glucose: float
    bp: float
    st: float
    insulin: float
    bmi: float
    dpf: float
    age: int


class PatientsSankey(BaseModel):
    Pregnancies: str
    Glucose: str
    Blood_pressure: str
    Skin_thickness: str
    Insulin: str
    Body_mass_index: str
    Diabetes_pedigree_function: str
    Age: str
    Diabetes_Probability: str