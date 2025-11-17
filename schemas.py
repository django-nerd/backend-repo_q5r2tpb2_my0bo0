from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ContactInquiry(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=2000)
    budget: Optional[str] = Field(None, max_length=100)
    project_type: Optional[str] = Field(None, max_length=100)
