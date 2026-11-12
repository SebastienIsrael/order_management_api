from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class MovementType(StrEnum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
