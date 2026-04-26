from enum import StrEnum


class InventoryMovementType(StrEnum):
    INITIAL_LOAD = "INITIAL_LOAD"
    RECEIVE = "RECEIVE"
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    SHIP = "SHIP"
    ADJUSTMENT = "ADJUSTMENT"


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