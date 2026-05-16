import os
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for local development convenience if PG isn't set up, 
# but structure it for easy PG swap.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trialsync.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    diagnosis = Column(String)
    hba1c = Column(Float)
    prior_chemo = Column(Boolean)
    ecog_status = Column(Integer)
    region = Column(String)
    raw_fhir_data = Column(JSON) # Store original FHIR for audit
    created_at = Column(DateTime, default=datetime.utcnow)

class Trial(Base):
    __tablename__ = "trials"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    criteria = Column(JSON) # Inclusion/Exclusion rules
    created_at = Column(DateTime, default=datetime.utcnow)

class Site(Base):
    __tablename__ = "sites"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    region = Column(String)
    capacity_total = Column(Integer)
    capacity_current = Column(Integer, default=0)

class ScreeningReport(Base):
    __tablename__ = "screening_reports"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    trial_id = Column(String, ForeignKey("trials.id"))
    eligibility_status = Column(String) # match, no_match
    reasoning = Column(Text)
    assigned_site_id = Column(String, ForeignKey("sites.id"), nullable=True)
    processing_time_sec = Column(Float)
    full_report_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Define clinical trials
    demo_trials = [
        {
            "id": "ONCO-2025-001",
            "title": "Phase II Ovarian Cancer PARP Inhibitor Study",
            "description": "Evaluating the efficacy of a new PARP inhibitor in patients with advanced ovarian cancer.",
            "criteria": {
                "inclusion": ["Age 45-70", "HbA1c > 7.5", "Confirmed ovarian cancer", "ECOG 0 or 1"],
                "exclusion": ["Prior chemo in last 6 months", "Active autoimmune", "Pregnancy"]
            }
        },
        {
            "id": "LUNG-2025-002",
            "title": "Stage III NSCLC Immunotherapy Trial",
            "description": "Study of PD-L1 inhibitors in Non-Small Cell Lung Cancer.",
            "criteria": {
                "inclusion": ["Age 18-80", "Confirmed NSCLC", "Positive PD-L1 (>1%)", "Informed consent"],
                "exclusion": ["Brain metastasis", "Other malignancy in 2 yrs", "Severe CVD"]
            }
        },
        {
            "id": "DIAB-2025-003",
            "title": "Type 2 Diabetes GLP-1/GIP Study",
            "description": "Novel dual-agonist therapy for management of T2D.",
            "criteria": {
                "inclusion": ["Age 18-75", "HbA1c 7.0-10.5", "BMI > 27", "T2D Diagnosis"],
                "exclusion": ["Type 1 Diabetes", "History of pancreatitis", "Current insulin use"]
            }
        }
    ]

    for t_data in demo_trials:
        if not db.query(Trial).filter(Trial.id == t_data["id"]).first():
            trial = Trial(**t_data)
            db.add(trial)
    
    # Define clinical sites
    demo_sites = [
        {"id": "S01", "name": "Chennai Central Lab", "region": "south", "capacity_total": 10},
        {"id": "S02", "name": "Mumbai Trial Hub", "region": "west", "capacity_total": 5},
        {"id": "S03", "name": "Delhi Oncology Ctr", "region": "north", "capacity_total": 15},
    ]

    for s_data in demo_sites:
        if not db.query(Site).filter(Site.id == s_data["id"]).first():
            site = Site(**s_data)
            db.add(site)
            
    db.commit()
    db.close()
