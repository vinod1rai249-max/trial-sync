import random

def generate_synthetic_patients(n=10):
    regions = ["south", "north", "west", "east"]
    
    patients = []
    for i in range(n):
        # We pick a "Target Trial Profile" to bias towards for each patient
        # This ensures we have matches for all trials in our database.
        profile_type = random.choice(["ONCO", "LUNG", "DIAB", "REJECT"])
        
        if profile_type == "ONCO":
            diagnosis = "ovarian cancer"
            age = random.randint(45, 70)
            hba1c = round(random.uniform(7.6, 9.0), 1)
            prior_chemo = False
            ecog_status = random.choice([0, 1])
        elif profile_type == "LUNG":
            diagnosis = "Non-Small Cell Lung Cancer (NSCLC)"
            age = random.randint(18, 80)
            hba1c = round(random.uniform(5.0, 7.0), 1)
            prior_chemo = False
            ecog_status = 0
        elif profile_type == "DIAB":
            diagnosis = "Type 2 Diabetes"
            age = random.randint(18, 75)
            hba1c = round(random.uniform(7.1, 10.4), 1) # Criteria is 7.0-10.5
            prior_chemo = False
            ecog_status = 0
        else:
            # Random "Reject" patient
            diagnosis = random.choice(["hypertension", "healthy", "flu"])
            age = random.randint(20, 40)
            hba1c = 5.5
            prior_chemo = random.choice([True, False])
            ecog_status = 2
        
        patients.append({
            "name": f"Patient_{i+1}",
            "age": age,
            "hba1c": hba1c,
            "diagnosis": diagnosis,
            "region": random.choice(regions),
            "prior_chemo": prior_chemo,
            "ecog_status": ecog_status
        })
    return patients
