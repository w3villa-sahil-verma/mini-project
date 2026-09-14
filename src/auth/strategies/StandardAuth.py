class StandardAuth:
    def __init__(self, controller):
        self.controller = controller

    def register(self, registration_request):
        # controller.register(registration_request.email, registration_request.password, registration_request.verification_code);
        return {"message": "User registered successfully"}

    def sendRegistrationMail(self, email: str):
        # Check 
        return self.controller.sendVerificationMail(email)