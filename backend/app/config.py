import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    PROJECT_NAME: str = 'SwasthiQ Kaagazy EOD Billing & Analytics Agent'
    VERSION: str = '1.0.0'
    API_PREFIX: str = '/api'
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'clinic_billing.db')
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    DEFAULT_CLINIC_NAME: str = 'Mehta Multi-Speciality Clinic — Kanpur, Uttar Pradesh'
    DEFAULT_DOCTOR_NAME: str = 'Dr. Arvind Mehta'

settings = Settings()
