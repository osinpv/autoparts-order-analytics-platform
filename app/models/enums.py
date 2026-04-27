from enum import StrEnum


class InventoryMovementType(StrEnum):
    INITIAL_LOAD = "INITIAL_LOAD"
    RECEIVE = "RECEIVE"
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    SHIP = "SHIP"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"


class InventoryReferenceType(StrEnum):
    INVENTORY_BALANCE = "INVENTORY_BALANCE"
    MANUAL = "MANUAL"
    ORDER = "ORDER"
    ORDER_ITEM = "ORDER_ITEM"
    SHIPMENT = "SHIPMENT"


class OrderStatus(StrEnum):
    NEW = "NEW"
    RESERVED = "RESERVED"
    RELEASED = "RELEASED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
    DELIVERED = "DELIVERED"


class ShipmentStatus(StrEnum):
    CREATED = "CREATED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    RETURNED = "RETURNED"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(StrEnum):
    CARD = "CARD"
    PAYPAL = "PAYPAL"
    BANK_TRANSFER = "BANK_TRANSFER"