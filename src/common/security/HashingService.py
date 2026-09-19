from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class HashingService:

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return password_hash.verify(password, hashed_password)