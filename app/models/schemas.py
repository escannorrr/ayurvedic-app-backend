from pydantic import BaseModel, Field, field_validator, validator
from typing import List, Dict, Any, Optional

class ConsultationRequest(BaseModel):
    patient_name: str
    age: int
    gender: str
    symptoms: List[str]
    notes: Optional[str] = None
    duration: str
    prakriti: str = Field(..., description="Vata | Pitta | Kapha")

    @validator("prakriti")
    def validate_prakriti(cls, v):
        allowed = ["Vata", "Pitta", "Kapha"]
        if v not in allowed:
            raise ValueError(f"Prakriti must be one of {allowed}")
        return v

class DiagnosisRequest(BaseModel):
    patient_name: Optional[str] = Field(None, description="Name of the patient.")
    query: Optional[str] = Field(None, min_length=3, description="Free-text health query.")
    symptoms: List[str] = Field(..., min_length=1, description="Structured symptoms from checklist.")
    duration_days: Optional[int] = Field(None, ge=1, description="Duration of symptoms in days.")
    prakriti: Optional[str] = Field(None, description="Vata | Pitta | Kapha")
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = Field(None, description="Male | Female | Other")

class DoshaScores(BaseModel):
    vata: int = Field(..., ge=0, le=100)
    pitta: int = Field(..., ge=0, le=100)
    kapha: int = Field(..., ge=0, le=100)

class DiagnosisItem(BaseModel):
    condition: str
    confidence: int = Field(..., ge=0, le=100)
    label: str = Field(..., description="High | Moderate | Low")

class Treatment(BaseModel):
    principles: List[str] = Field(default_factory=list)
    herbs: List[str] = Field(default_factory=list)
    formulations: List[str] = Field(default_factory=list)
    diet: List[str] = Field(default_factory=list)
    lifestyle: List[str] = Field(default_factory=list)

class DiagnosisResponse(BaseModel):
    diagnosis: List[DiagnosisItem]
    confidence: int = Field(..., ge=0, le=100)
    dosha: DoshaScores
    explanation: str
    dosha_analysis: str
    treatment: Treatment
    precautions: List[str]
    when_to_consult: List[str]
    follow_up_question: Optional[str] = ""
    debug: Optional[Dict[str, Any]] = None

    @field_validator('diagnosis')
    @classmethod
    def validate_diagnosis(cls, v):
        if not v:
            raise ValueError("At least one diagnosis must be provided.")
        return v
