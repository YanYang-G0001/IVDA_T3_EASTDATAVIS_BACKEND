import pandas as pd
import random

# 生成 Sankey 所需的数据
def generate_sankey_data(n=400, output_path='src/sankey_data.csv'):
    data = []
    smoking_choices = ["Smoking", "Non-Smoking"]
    cholesterol_choices = ["High Cholesterol", "Normal Cholesterol", "Low Cholesterol"]
    bp_choices = ["High BP", "Normal BP", "Low BP"]
    age_choices = ["Senior", "Middle Age", "Young"]
    bmi_choices = ["Underweight", "Normal", "Overweight", "Obese"]
    physical_activity_choices = ["Low", "Moderate", "High"]
    family_history_choices = ["Yes", "No"]
    diabetes_risk_choices = ["High Risk", "Medium Risk", "Low Risk"]

    for _ in range(n):
        smoking = random.choice(smoking_choices)
        cholesterol = random.choice(cholesterol_choices)
        bp = random.choice(bp_choices)
        age = random.choice(age_choices)
        bmi = random.choice(bmi_choices)
        physical_activity = random.choice(physical_activity_choices)
        family_history = random.choice(family_history_choices)

        # 根据某些属性的组合计算糖尿病风险
        if smoking == "Smoking" and bp == "High BP" and family_history == "Yes":
            diabetes_risk = "High Risk"
        elif cholesterol == "High Cholesterol" or bmi == "Obese":
            diabetes_risk = "Medium Risk"
        else:
            diabetes_risk = "Low Risk"

        data.append({
            "C1": smoking,
            "C2": cholesterol,
            "C3": bp,
            "C4": age,
            "C5": bmi,
            "C6": physical_activity,
            "C7": family_history,
            "C8": diabetes_risk
        })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

# 调用函数生成数据
generate_sankey_data()
