from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    clinic_name = Column(String, nullable=True)
    preferences = Column(JSON, nullable=True) # UI/Notification preferences
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Clinical Identity (e.g., VA-1024)
    case_identifier = Column(String, unique=True, index=True, nullable=False)
    
    # Raw Input Records
    query = Column(String, nullable=False)
    # Clinical Status (draft / complete)
    status = Column(String, default="draft", index=True)
    
    # Refactored Clinical Data (JSONB)
    patient_info = Column(JSON, nullable=True)
    consultation = Column(JSON, nullable=True) # symptoms, duration, notes
    ai_analysis = Column(JSON, nullable=True)   # Full AI output
    doctor_input = Column(JSON, nullable=True)  # final_diagnosis, clinical_notes, is_ai_used
    
    # Legacy / Compatibility fields (Can be removed later)
    diagnosis = Column(JSON, nullable=True) 
    treatment = Column(JSON, nullable=True)
    
    # Clinical History & Media (JSONB)
    timeline = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)
    
    # Metadata for filtering/stats (Can be derived from ai_analysis/doctor_input)
    confidence = Column(Integer)
    pitta = Column(Integer)
    vata = Column(Integer)
    kapha = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
