from src.auth.services.RegistrationLinkService import registrationLinkService

def register():
    pass;

def sendVerificationMail(email: str):
    
    registrationLinkService.create_registration_link(email)

    return {"message": "Verification email sent to " + email, "registration-link": "http://localhost:8000/auth/register?code=" + "1234"};

def resendVerificationMail():
    pass;