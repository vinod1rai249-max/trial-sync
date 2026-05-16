import random

def generate_synthetic_patients(n=10):
    diagnoses = ["ovarian cancer", "breast cancer", "diabetes", "hypertension", "healthy"]
    regions = ["south", "north", "west", "east"]
    
    patients = []
    for i in range(n):
        diagnosis = random.choice(diagnoses)
        age = random.randint(30, 80)
        hba1c = round(random.uniform(5.0, 9.0), 1)
        prior_chemo = random.choice([True, False])
        ecog_status = random.choice([0, 1, 2])
        
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
