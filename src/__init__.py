from typing import Tuple

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restx import Resource, Api
from flask_pymongo import PyMongo
from pymongo.collection import Collection
from .model import PatientsCat, PatientInput, PatientsSankey
from .datapreprocess import normalize_for_radar
from src.llm.groq_llm import GroqClient
from bson import ObjectId

import os
import json
import pandas as pd
import joblib

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
patients_sankey: Collection = pymongo.db.SANKEY
api = Api(app)
best_model = joblib.load('src/best_xgb_model1.pkl')
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
def individual_predict(patient: PatientInput) -> tuple[str, str]:

    # other data like 'Pregnancies' has been set to the average
    input_data = {
        'Pregnancies': patient.pregnancies,
        'Glucose': patient.glucose,
        'Blood pressure': patient.bp,
        'Skin thickness': patient.st,
        'Insulin': patient.insulin,
        'Body mass index': patient.bmi,
        'Diabetes pedigree function': patient.dpf,
        'Age': patient.age
    }
    input_df = pd.DataFrame([input_data])

    input_df = input_df[['Pregnancies', 'Glucose', 'Blood pressure', 'Skin thickness',
                         'Insulin', 'Body mass index', 'Diabetes pedigree function', 'Age']]

    # predict : 0-non diabetes or 1-diabetes
    pred_label = best_model.predict(input_df)[0]
    # get normalized data
    # dpm increased by 100 times, pregnancy increased by 10 times, for visualization
    input_data['Diabetes pedigree function'] = input_data['Diabetes pedigree function']  * 100
    input_data['Pregnancies'] = input_data['Pregnancies'] * 10
    normalized_data = normalize_for_radar(input_data)
    return str(pred_label), str(normalized_data)

class PredictDisease(Resource):
    def post(self):
        prediction = 'unknown'  # Default value in case result is not 1 or 0
        try:
            data = request.get_json()
            patient = PatientInput(**data)
            result, normalize_data = individual_predict(patient)
            if result == '1':
                prediction = 'positive'
            elif result == '0':
                prediction = 'negative'

            return jsonify({
                "prediction": prediction,
                "result": result,
                "normalized": normalize_data
            })
        except Exception as e:
            return {"error": f"Invalid input: {str(e)}"}, 400

class PatientsSankey(Resource):
    def get(self):
        """
        Fetch Sankey data based on the user's filters and conditions.
        """
        try:
            # Get filters from the request args
            filters = request.args.to_dict()

            # Query the database using the filters
            cursor = patients_sankey.find(filters)
            data = list(cursor)  # Convert cursor to list

            # Construct Sankey data
            sankey_data = []
            for doc in data:
                sankey_data.append(doc)  # Append the filtered document

            return [PatientsSankey(**doc).to_json() for doc in cursor]

        except Exception as e:
            return jsonify({"error": str(e)}), 500
def convert_objectid_to_str(data):
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data
class FilterOptions(Resource):
    def get(self):
        """
        Fetch filter options dynamically from the Sankey data.
        """
        try:
            # Fetch data from the patients_sankey collection
            cursor = patients_sankey.find({}, {"_id": 0})
            data = list(cursor)  # Convert cursor to list
            data = convert_objectid_to_str(data)

            # Convert to DataFrame to perform filtering operations
            df = pd.DataFrame(data)

            # Get unique values for each column
            filter_options = {col: sorted(df[col].unique().tolist()) for col in df.columns}

            return filter_options

        except Exception as e:
            return jsonify({"error": str(e)}), 500

class SankeyData(Resource):
    def post(self):
        """
        Dynamically generate Sankey data based on the node selections and filters passed from the frontend.
        """
        try:
            # Get data from the frontend (nodes and filters)
            request_data = request.get_json()
            nodes = request_data.get("nodes", [])
            filters = request_data.get("filters", {})
            #print(filters, nodes)

            # Fetch the data from the MongoDB collection (patients_sankey)
            cursor = patients_sankey.find({}, {"_id": 0})  # Apply filters directly to the MongoDB query
            data = list(cursor)

            # Convert data to DataFrame
            if not data:
                print("No data returned from database.")
                return {"nodes": {"label": [], "color": []},
                        "links": {"source": [], "target": [], "value": [], "color": []}}

            data = convert_objectid_to_str(data)
            df = pd.DataFrame(data)

            # Apply filters to DataFrame
            for column, values in filters.items():
                if values:
                    if column not in df.columns:
                        print(f"Column {column} not found in DataFrame!")
                        continue
                    df = df[df[column].isin(values)]

            # Risk color mapping based on the endpoint (last node)
            risk_colors = {
                "0.64+ (High Risk)": "#B22222",
                "0.34-0.63 (Moderate Risk)": "#eb7800",
                "0-0.33 (Low Risk)": "#006400"
            }

            # Initialize data structures
            labels = []
            label_map = {}
            source = []
            target = []
            value = []
            link_colors = []

            # Process rows to generate paths
            for _, row in df.iterrows():
                # Generate the path for this row
                path_nodes = [str(row[node]) for node in nodes if pd.notna(row[node])]

                # Ensure there are at least two nodes
                if len(path_nodes) < 2:
                    continue

                # Determine the color for the path based on the last node
                last_node = path_nodes[-1]
                path_color = risk_colors.get(last_node, "#efebe4")

                # Add each node to the label map and labels list
                for node in path_nodes:
                    if node not in label_map:
                        label_map[node] = len(labels)
                        labels.append(node)

                # Create links for each segment of the path
                for i in range(len(path_nodes) - 1):
                    source_label = path_nodes[i]
                    target_label = path_nodes[i + 1]

                    source_idx = label_map[source_label]
                    target_idx = label_map[target_label]

                    if (source_idx, target_idx, path_color) not in zip(source, target, link_colors):
                        source.append(source_idx)
                        target.append(target_idx)
                        value.append(1)
                        link_colors.append(path_color)
                    else:
                        # Increment the value for an existing link
                        idx = list(zip(source, target, link_colors)).index((source_idx, target_idx, path_color))
                        value[idx] += 1

            # Assign colors to nodes (Risk nodes get specific colors, others gray)
            node_colors = []
            for node in labels:
                if node in risk_colors:  # Check if the node is a Risk node
                    node_colors.append(risk_colors[node])  # Use risk-specific colors
                else:
                    node_colors.append("#efebe4")  # Default neutral color for non-risk nodes

            # Debugging: Print processed paths and their colors
            #print("Processed nodes and their colors:")
            #for i, (node, color) in enumerate(zip(labels, node_colors), 1):
             #   print(f"Node {i}: {node} (Color: {color})")

            #print("Processed paths and colors:")
            #for i, (src, tgt, color) in enumerate(zip(source, target, link_colors), 1):
            #    print(f"Link {i}: {labels[src]} -> {labels[tgt]} (Color: {color})")

            # Prepare the Sankey data structure in JSON format
            sankey_data = {
                "nodes": {
                    "label": labels,
                    "color": node_colors,  # Neutral node color
                },
                "links": {
                    "source": source,
                    "target": target,
                    "value": value,
                    "color": link_colors,  # Ensure link colors match the sub-path's last node
                },
            }

            #print("Final Sankey Data:", sankey_data)
            return sankey_data

        except Exception as e:
            return {"error": f"Invalid input: {str(e)}"}, 400



# Register the resource to the Flask API
api.add_resource(SankeyData, '/api/sankey-data')
api.add_resource(FilterOptions, '/api/filter-options')
api.add_resource(PatientsCatList, '/patientscat')
api.add_resource(PredictDisease, '/predict')
api.add_resource(PatientsSankey, '/patientssankey')

#api.add_resource(PoemByCompanyId, '/llm/groq/poem/<int:companyId>')
#api.add_resource(EvaluationByCompanyId, '/llm/groq/evaluation/<int:companyId>')