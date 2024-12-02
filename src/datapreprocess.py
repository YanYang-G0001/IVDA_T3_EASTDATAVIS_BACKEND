import pandas as pd
from sklearn.preprocessing import MinMaxScaler
def normalize_for_radar(patient_data):
    data = {
        'Attribute': ['Pregnancies', 'Pregnancies', 'Glucose', 'Glucose', 'Blood pressure', 'Blood pressure',
                      'Skin thickness', 'Skin thickness', 'Insulin', 'Insulin', 'Body mass index', 'Body mass index',
                      'Diabetes pedigree function', 'Diabetes pedigree function', 'Age', 'Age'],
        'Type': ['Diabetes', 'Non-Diabetes', 'Diabetes', 'Non-Diabetes', 'Diabetes', 'Non-Diabetes',
                 'Diabetes', 'Non-Diabetes', 'Diabetes', 'Non-Diabetes', 'Diabetes', 'Non-Diabetes',
                 'Diabetes', 'Non-Diabetes', 'Diabetes', 'Non-Diabetes'],
        'Average Value': [48.65672, 32.98000, 141.979440, 110.530180, 75.383731, 70.629100,
                      32.930597, 27.047560, 202.488918, 128.105380, 35.381336, 30.849614,
                      55.0500, 42.9734, 37.067164, 31.190000]
    } #dpm increased by 100 times, pregnancy increased by 10 times, for visualization

    # Create DataFrame
    df = pd.DataFrame(data)

    # Initialize MinMaxScaler to normalize to range [0, 1]
    scaler = MinMaxScaler()

    # Fit the scaler on the 'Average Value' column of the original data
    scaler.fit(df[['Average Value']])
    patient_df = pd.DataFrame(list(patient_data.items()), columns=['Attribute', 'Average Value'])

    # Normalize the 'Value' column in the new sample
    patient_df['Normalized Value'] = scaler.transform(patient_df[['Average Value']]).round(2)

    # Convert the normalized values to a string for return
    normalized_values_str = ", ".join(map(str, patient_df['Normalized Value'].tolist()))

    return normalized_values_str