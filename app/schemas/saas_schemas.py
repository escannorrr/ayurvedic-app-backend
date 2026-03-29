from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models.schemas import DiagnosisResponse

# --- Auth & User ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None

# --- Settings & Profile ---
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    clinic_name: Optional[str] = None
    preferences: Optional[dict] = None

class ProfileOut(BaseModel):
    full_name: Optional[str]
    email: EmailStr
    clinic_name: Optional[str]
    preferences: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# --- Patient & Diagnosis Support ---
class PatientInfo(BaseModel):
    patient_name: str
    age: int
    gender: str
    location: Optional[str] = None

class ConsultationData(BaseModel):
    symptoms: List[str]
    duration: str
    notes: Optional[str] = None

class DoctorInput(BaseModel):
    final_diagnosis: List[str]
    clinical_notes: Optional[str] = None
    is_ai_used: bool = True

# --- Case & Dashboard ---
class CaseCreate(BaseModel):
    patient_info: PatientInfo
    consultation: ConsultationData
    ai_analysis: Optional[DiagnosisResponse] = None # Full AI engine output
    doctor_input: Optional[DoctorInput] = None
    status: str = "draft"
    
    # Backward compatibility support
    diagnosis_result: Optional[DiagnosisResponse] = None

class CaseCreateResponse(BaseModel):
    case_id: str
    status: str
    created_at: datetime

class NotesUpdate(BaseModel):
    notes: str

class CaseOut(BaseModel):
    id: int
    case_identifier: str
    query: Optional[str]
    diagnosis: List[Any]
    treatment: Any
    confidence: int
    created_at: datetime
    status: str
    
    # Optional detailed info
    patient_info: Optional[dict] = None
    symptoms: Optional[List[str]] = None
    
    # Dosha breakdown for UI charts
    pitta: int
    vata: int
    kapha: int

    class Config:
        from_attributes = True

class CaseListOut(BaseModel):
    id: int
    case_identifier: str
    patient_name: str
    diagnosis_summary: str
    date: datetime
    status: str

    class Config:
        from_attributes = True

class TimelineEvent(BaseModel):
    event: str
    date: datetime
    description: Optional[str] = None

class CaseDetailOut(BaseModel):
    id: int
    case_identifier: str
    status: str
    patient_info: PatientInfo
    consultation: ConsultationData
    ai_analysis: Optional[DiagnosisResponse]
    doctor_input: Optional[DoctorInput]
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedCases(BaseModel):
    items: List[CaseListOut]
    total: int
    page: int
    limit: int

class DashboardStats(BaseModel):
    total_consultations: int
    dominant_dosha: str
    recent_cases: List[CaseOut]

class DashboardSummary(BaseModel):
    patients_today: int
    ai_consultations: int
    saved_cases: int

class RecentConsultation(BaseModel):
    id: int
    patient_name: str
    date: datetime
    diagnosis_tag: str
