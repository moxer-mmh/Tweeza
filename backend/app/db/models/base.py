# backend/app/db/models/base.py
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    WORKER = "worker"
    VOLUNTEER = "volunteer"
    BENEFICIARY = "beneficiary"


class ResourceTypeEnum(enum.Enum):
    FOOD = "food"
    MONEY = "money"
    MATERIALS = "materials"
    TIME = "time"


class EventTypeEnum(enum.Enum):
    IFTAR = "iftar"
    CLEANUP = "cleanup"
    EMERGENCY = "emergency"
    WORKSHOP = "workshop"
