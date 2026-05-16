import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agent.graph import build_graph
from database import SessionLocal, Patient, Trial, Site, ScreeningReport, init_db
from dotenv import load_dotenv
from utils.synthea_sim import generate_synthetic_patients

load_dotenv()

# Initialize DB
init_db()

app = FastAPI(title="TrialMatch AI - Enterprise Edition")
graph = build_graph()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PatientSchema(BaseModel):
    id: str
    name: str
    age: int
    diagnosis: str
    hba1c: float
    region: str
    
    class Config:
        from_attributes = True

class TrialSchema(BaseModel):
    id: str
    title: str
    description: str
    criteria: Dict[str, Any]

    class Config:
        from_attributes = True

@app.get("/trials", response_model=List[TrialSchema])
async def get_trials(db: Session = Depends(get_db)):
    return db.query(Trial).all()

@app.post("/patients/generate")
async def generate_patients(count: int = 10, db: Session = Depends(get_db)):
    raw_patients = generate_synthetic_patients(count)
    db_patients = []
    for p in raw_patients:
        patient_id = str(uuid.uuid4())
        db_p = Patient(
            id=patient_id,
            name=p["name"],
            age=p["age"],
            diagnosis=p["diagnosis"],
            hba1c=p["hba1c"],
            prior_chemo=p["prior_chemo"],
            ecog_status=p["ecog_status"],
            region=p["region"],
            raw_fhir_data=p # Simulating FHIR
        )
        db_patients.append(db_p)
    
    db.add_all(db_patients)
    db.commit()
    return {"message": f"Generated {count} patients", "count": count}

@app.get("/patients", response_model=List[PatientSchema])
async def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).order_by(Patient.created_at.desc()).limit(50).all()

@app.post("/screen/batch")
async def screen_batch(trial_id: str = "ONCO-2025-001", db: Session = Depends(get_db)):
    trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
        
    # Get IDs of patients already screened for this trial
    screened_patient_ids = [r.patient_id for r in db.query(ScreeningReport.patient_id).filter(ScreeningReport.trial_id == trial_id).all()]
    
    # Get patients not yet screened
    patients = db.query(Patient).filter(~Patient.id.in_(screened_patient_ids)).all()
    
    if not patients:
        return {"message": "No new patients to screen", "screened_count": 0, "reports": []}
    
    start_batch_time = time.time()
    tasks = []
    
    for p in patients:
        initial_state = {
            "patient_id": p.id,
            "trial_id": trial_id,
            "trial_criteria": trial.criteria,
            "raw_data": {
                "age": p.age,
                "hba1c": p.hba1c,
                "diagnosis": p.diagnosis,
                "region": p.region,
                "prior_chemo": p.prior_chemo,
                "ecog_status": p.ecog_status
            },
            "deidentified_data": {},
            "eligibility_result": None,
            "eligibility_reason": None,
            "site_assignment": None,
            "report": None,
            "processing_time": 0.0
        }
        config = {"run_name": f"Batch-{p.id[:8]}", "tags": ["production", "batch"]}
        tasks.append(asyncio.to_thread(graph.invoke, initial_state, config=config))
    
    results = await asyncio.gather(*tasks)
    
    # Bulk save results
    reports = []
    for res in results:
        reports.append(ScreeningReport(
            id=str(uuid.uuid4()),
            patient_id=res["patient_id"],
            trial_id=trial_id,
            eligibility_status=res["eligibility_result"],
            reasoning=res["eligibility_reason"],
            assigned_site_id=res["site_assignment"]["site_id"] if res["site_assignment"] else None,
            processing_time_sec=0.0, # Will update after batch
            full_report_json=res["report"]
        ))
    db.add_all(reports)
    db.commit()
    
    total_time = time.time() - start_batch_time
    return {
        "screened_count": len(results),
        "total_time_sec": round(total_time, 2),
        "reports": [r.full_report_json for r in reports]
    }

@app.post("/screen/{patient_id}")
async def screen_single_patient(patient_id: str, trial_id: str = "ONCO-2025-001", db: Session = Depends(get_db)):
    trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
        
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    start_time = time.time()
    
    # Prepare state for agent
    initial_state = {
        "patient_id": patient.id,
        "trial_id": trial_id,
        "trial_criteria": trial.criteria,
        "raw_data": {
            "age": patient.age,
            "hba1c": patient.hba1c,
            "diagnosis": patient.diagnosis,
            "region": patient.region,
            "prior_chemo": patient.prior_chemo,
            "ecog_status": patient.ecog_status
        },
        "deidentified_data": {},
        "eligibility_result": None,
        "eligibility_reason": None,
        "site_assignment": None,
        "report": None,
        "processing_time": 0.0
    }
    
    config = {"run_name": f"Screening-{patient.id[:8]}", "tags": ["production"]}
    result = await asyncio.to_thread(graph.invoke, initial_state, config=config)
    
    processing_time = time.time() - start_time
    
    # Persist report
    report = result["report"]
    db_report = ScreeningReport(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        trial_id=trial_id,
        eligibility_status=result["eligibility_result"],
        reasoning=result["eligibility_reason"],
        assigned_site_id=result["site_assignment"]["site_id"] if result["site_assignment"] else None,
        processing_time_sec=round(processing_time, 2),
        full_report_json=report
    )
    db.add(db_report)
    db.commit()
    
    return report

@app.get("/reports")
async def get_reports(db: Session = Depends(get_db)):
    return db.query(ScreeningReport).order_by(ScreeningReport.created_at.desc()).all()
