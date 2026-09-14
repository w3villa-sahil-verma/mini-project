from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.auth.controller import Controller as controller

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

class RegistrationRequest(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "sahil.verma@w3villa.com"})
    password: str = Field(..., json_schema_extra={"example": "Sahil@123"})
    verification_code: str = Field(..., json_schema_extra={"example": "1234"})

@router.post("/register")
def register(body: RegistrationRequest):
    # controller.register(registration_request.email, registration_request.password, registration_request.verification_code);
    return {"message": "User registered successfully"}

@router.get("/registration-mail")
def sendVerificationMail(email: str):
    return controller.sendVerificationMail(email);

@router.post("/resend-verification-mail")
def resendVerificationMail():
    controller.resendVerificationMail();
