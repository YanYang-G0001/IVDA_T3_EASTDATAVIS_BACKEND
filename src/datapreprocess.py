import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
def normalize_for_radar_pre():
    data = pd.read_csv('src\pima_preprocessed_dataset.csv')
    # Create DataFrame
    df = pd.DataFrame(data)

    # drop useless col, use avg value to replace later
    df = df.drop(['pregnancies', 'skin_thickness', 'diabetes_pedigree_function', 'outcome'], axis=1)
    df.rename(columns={'blood_pressure': 'bp', 'body_mass_index': 'bmi'}, inplace=True)
    # Initialize MinMaxScaler to normalize to range [0, 1]
    scaler = MinMaxScaler()

    normalized_data = scaler.fit_transform(df)
    # normalized_df = pd.DataFrame(normalized_data, columns=df.columns)
    return scaler, df.columns


def normalize_for_radar(patient_data):
    scaler, columns = normalize_for_radar_pre()
    patient_df = pd.DataFrame([patient_data])[columns]
    normalized_data = scaler.transform(patient_df)
    normalized_values_str = ', '.join([str(round(float(val), 2)) for val in normalized_data[0]])
    print(normalized_values_str)
    return normalized_values_str
