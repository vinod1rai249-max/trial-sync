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
    
    # Seed initial data if empty
    db = SessionLocal()
    if not db.query(Trial).first():
        trials = [
            Trial(
                id="ONCO-2025-001",
                title="Phase II Ovarian Cancer PARP Inhibitor Study",
                description="Evaluating the efficacy of a new PARP inhibitor in patients with advanced ovarian cancer.",
                criteria={
                    "inclusion": [
                        "Age between 45 and 70",
                        "HbA1c greater than 7.5",
                        "Confirmed ovarian cancer diagnosis",
                        "ECOG performance status 0 or 1"
                    ],
                    "exclusion": [
                        "Prior chemotherapy in last 6 months",
                        "Active autoimmune disease",
                        "Pregnancy or breastfeeding"
                    ]
                }
            ),
            Trial(
                id="LUNG-2025-002",
                title="Stage III NSCLC Immunotherapy Trial",
                description="Study of PD-L1 inhibitors in Non-Small Cell Lung Cancer.",
                criteria={
                    "inclusion": [
                        "Age between 18 and 80",
                        "Confirmed NSCLC diagnosis",
                        "Positive PD-L1 expression (>1%)",
                        "Able to provide informed consent"
                    ],
                    "exclusion": [
                        "Metastatic disease to the brain",
                        "History of other malignancy in last 2 years",
                        "Severe cardiovascular disease"
                    ]
                }
            ),
            Trial(
                id="DIAB-2025-003",
                title="Type 2 Diabetes GLP-1/GIP Study",
                description="Novel dual-agonist therapy for management of T2D.",
                criteria={
                    "inclusion": [
                        "Age between 18 and 75",
                        "HbA1c between 7.0 and 10.5",
                        "BMI greater than 27 kg/m2",
                        "Diagnosis of Type 2 Diabetes"
                    ],
                    "exclusion": [
                        "Type 1 Diabetes diagnosis",
                        "History of pancreatitis",
                        "Current use of insulin"
                    ]
                }
            )
        ]
        db.add_all(trials)
        
        sites = [
            Site(id="S01", name="Chennai Central Lab", region="south", capacity_total=10),
            Site(id="S02", name="Mumbai Trial Hub", region="west", capacity_total=5),
            Site(id="S03", name="Delhi Oncology Ctr", region="north", capacity_total=15),
        ]
        db.add_all(sites)
        db.commit()
    db.close()
