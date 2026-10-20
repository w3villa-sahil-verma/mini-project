from enum import Enum
from pydantic import BaseModel

# -------------------------
# Enums
# -------------------------
class TOKEN_TYPES(str, Enum):
    REGISTRATION = "REGISTRATION"
    ACCESS = "ACCESS"